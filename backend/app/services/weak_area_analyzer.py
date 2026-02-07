"""
Weak Area Analyzer Service for mentor feedback feature.

Analyzes user progress to identify weak areas and prepare data for gap quizzes.
"""
from typing import List, Dict, Any, Optional
from app.config import get_settings
from app.db import crud
from app.models.mentor import (
    MentorAnalysis,
    WeakArea,
    WeakConcept,
    WrongAnswer,
    MentorStatusResponse
)


class WeakAreaAnalyzer:
    """
    Analyzes user progress to find weak areas and prepare gap quiz data.
    """

    def __init__(self):
        self.settings = get_settings()

    def is_mentor_available(self, chapters_completed: int) -> bool:
        """
        Check if mentor feature is available based on chapters completed.

        Args:
            chapters_completed: Number of chapters the user has completed

        Returns:
            True if mentor is available
        """
        return chapters_completed >= self.settings.mentor_chapters_threshold

    async def get_mentor_status(
        self,
        user_id: str,
        course_slug: str
    ) -> MentorStatusResponse:
        """
        Get mentor availability status for a user on a course.

        Args:
            user_id: User identifier
            course_slug: Course slug

        Returns:
            MentorStatusResponse with availability info
        """
        stats = await crud.get_course_stats_for_mentor(user_id, course_slug)

        if not stats:
            return MentorStatusResponse(
                mentor_available=False,
                chapters_completed=0,
                chapters_required=self.settings.mentor_chapters_threshold,
                average_score=0.0,
                weak_areas_count=0,
                total_wrong_answers=0
            )

        completed = stats.get("completed_chapters", 0)
        mentor_available = self.is_mentor_available(completed)

        # Count weak areas (chapters with score < threshold)
        weak_count = 0
        for prog in stats.get("progress_by_chapter", []):
            if prog.get("completed") and prog.get("score", 1.0) < self.settings.mentor_weak_score_threshold:
                weak_count += 1

        return MentorStatusResponse(
            mentor_available=mentor_available,
            chapters_completed=completed,
            chapters_required=self.settings.mentor_chapters_threshold,
            average_score=stats.get("average_score", 0.0),
            weak_areas_count=weak_count,
            total_wrong_answers=stats.get("total_wrong_answers", 0)
        )

    async def analyze_user_progress(
        self,
        user_id: str,
        course_slug: str
    ) -> Optional[MentorAnalysis]:
        """
        Perform complete weak area analysis for a user on a course.

        Args:
            user_id: User identifier
            course_slug: Course slug

        Returns:
            MentorAnalysis with weak areas identified, or None if course not found
        """
        stats = await crud.get_course_stats_for_mentor(user_id, course_slug)

        if not stats:
            return None

        completed = stats.get("completed_chapters", 0)
        mentor_available = self.is_mentor_available(completed)

        # Identify weak areas
        weak_areas = self._identify_weak_areas(
            progress_list=stats.get("progress_by_chapter", []),
            chapters=stats.get("chapters", [])
        )

        return MentorAnalysis(
            course_slug=course_slug,
            course_topic=stats.get("course_topic", ""),
            difficulty=stats.get("difficulty", ""),
            total_chapters_completed=completed,
            total_chapters=stats.get("total_chapters", 0),
            average_score=stats.get("average_score", 0.0),
            weak_areas=weak_areas,
            total_wrong_answers=stats.get("total_wrong_answers", 0),
            mentor_available=mentor_available
        )

    def _identify_weak_areas(
        self,
        progress_list: List[Dict[str, Any]],
        chapters: List[Dict[str, Any]]
    ) -> List[WeakArea]:
        """
        Identify chapters where user scored below threshold.

        Args:
            progress_list: User's progress records
            chapters: Course chapters with key_concepts

        Returns:
            List of WeakArea objects
        """
        weak_areas = []
        threshold = self.settings.mentor_weak_score_threshold

        # Build chapter lookup
        chapters_by_number = {ch.get("number"): ch for ch in chapters}

        for prog in progress_list:
            if not prog.get("completed"):
                continue

            score = prog.get("score", 1.0)
            if score >= threshold:
                continue  # Not a weak area

            chapter_num = prog.get("chapter_number")
            chapter = chapters_by_number.get(chapter_num, {})

            # Extract weak concepts from wrong answers
            weak_concepts = self._extract_weak_concepts(
                answers=prog.get("answers", []),
                key_concepts=chapter.get("key_concepts", [])
            )

            weak_areas.append(WeakArea(
                chapter_number=chapter_num,
                chapter_title=prog.get("chapter_title", chapter.get("title", f"Chapter {chapter_num}")),
                score=score,
                questions_total=prog.get("total_questions", 0),
                questions_wrong=prog.get("total_questions", 0) - prog.get("correct_answers", 0),
                weak_concepts=weak_concepts
            ))

        # Sort by score (lowest first - weakest areas first)
        weak_areas.sort(key=lambda x: x.score)

        return weak_areas

    def _extract_weak_concepts(
        self,
        answers: List[Dict[str, Any]],
        key_concepts: List[str]
    ) -> List[WeakConcept]:
        """
        Map wrong answers to key concepts using basic text matching.

        Args:
            answers: List of user answers
            key_concepts: Chapter's key concepts

        Returns:
            List of WeakConcept objects
        """
        if not key_concepts:
            return []

        # Count wrong answers per concept (simple keyword matching)
        concept_wrong = {concept: [] for concept in key_concepts}
        total_questions = len(answers)

        for ans in answers:
            if ans.get("is_correct"):
                continue

            question_text = ans.get("question_text", "").lower()

            # Match to concepts
            for concept in key_concepts:
                concept_lower = concept.lower()
                if concept_lower in question_text:
                    concept_wrong[concept].append(question_text)

        # Build WeakConcept objects for concepts with wrong answers
        weak_concepts = []
        for concept, wrong_questions in concept_wrong.items():
            if wrong_questions:
                weak_concepts.append(WeakConcept(
                    concept=concept,
                    wrong_count=len(wrong_questions),
                    total_questions=total_questions,
                    sample_questions=wrong_questions[:3]  # Max 3 samples
                ))

        # Sort by wrong count (most wrong first)
        weak_concepts.sort(key=lambda x: x.wrong_count, reverse=True)

        return weak_concepts

    async def get_wrong_answers(
        self,
        user_id: str,
        course_slug: str,
        include_hints: bool = False
    ) -> List[WrongAnswer]:
        """
        Get all wrong answers for gap quiz (free feature).

        Args:
            user_id: User identifier
            course_slug: Course slug
            include_hints: Whether to include hints

        Returns:
            List of WrongAnswer objects ready for gap quiz
        """
        raw_wrong = await crud.get_wrong_answers_for_course(user_id, course_slug)

        wrong_answers = []
        for w in raw_wrong:
            # Build hint from explanation if requested
            hint = None
            if include_hints:
                explanation = w.get("explanation", "")
                if explanation:
                    # Create a simplified hint from explanation
                    hint = self._generate_hint(explanation)

            wrong_answers.append(WrongAnswer(
                question_id=w.get("question_id", ""),
                question_text=w.get("question_text", ""),
                question_type=w.get("question_type", "mcq"),
                options=w.get("options"),
                user_answer=str(w.get("user_answer", "")),
                correct_answer=w.get("correct_answer"),
                explanation=w.get("explanation", ""),
                chapter_number=w.get("chapter_number", 0),
                chapter_title=w.get("chapter_title", ""),
                hint=hint
            ))

        return wrong_answers

    def _generate_hint(self, explanation: str) -> str:
        """
        Generate a hint from the explanation without giving away the answer.

        Args:
            explanation: Full explanation text

        Returns:
            A simplified hint string
        """
        # Simple approach: take first sentence and make it vague
        sentences = explanation.split(".")
        if sentences:
            first = sentences[0].strip()
            if len(first) > 100:
                first = first[:100] + "..."
            return f"Think about: {first}"
        return "Review the related concept carefully."


# Singleton instance
_analyzer_instance: Optional[WeakAreaAnalyzer] = None


def get_weak_area_analyzer() -> WeakAreaAnalyzer:
    """Get or create the WeakAreaAnalyzer singleton."""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = WeakAreaAnalyzer()
    return _analyzer_instance
