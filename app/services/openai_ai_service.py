"""
OpenAI AI Service
Real implementation using OpenAI's GPT API.
Implements BaseAIService interface.
"""
from typing import List, Dict, Any
import json
from openai import AsyncOpenAI
from app.models.course import Chapter, CourseConfig
from app.services.base_ai_service import BaseAIService
from app.config import settings


class OpenAIService(BaseAIService):
    """
    OpenAI AI service for production use.
    Makes actual API calls to OpenAI's GPT models.
    """
    
    def __init__(self, model: str = None):
        """
        Initialize OpenAI AI service.
        
        Args:
            model: Optional model override. If not provided, uses config defaults.
        """
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured. Please set OPENAI_API_KEY in .env file.")
        
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.default_model = model or settings.model_chapter_generation
    
    async def generate_chapters(
        self,
        topic: str,
        config: CourseConfig,
        content: str = ""
    ) -> List[Chapter]:
        """
        Generate chapters using OpenAI GPT.

        Args:
            topic: The subject/topic for the course
            config: CourseConfig with chapter count, difficulty, depth, and time settings
            content: Optional document content to analyze

        Returns:
            List of Chapter objects
        """
        # Extract config values
        num_chapters = config.recommended_chapters
        difficulty = config.difficulty
        depth = config.chapter_depth
        time_per_chapter = config.time_per_chapter_minutes

        # Depth descriptions for the prompt
        depth_instructions = {
            "overview": "Provide a high-level overview with key points. Keep summaries brief and focus on main ideas.",
            "detailed": "Provide thorough coverage with explanations and examples. Include practical applications.",
            "comprehensive": "Provide in-depth, expert-level content. Include advanced concepts, nuances, and real-world case studies."
        }
        depth_instruction = depth_instructions.get(depth, depth_instructions["detailed"])

        # Build the prompt
        if content:
            prompt = f"""You are an expert educational content creator.

Given this document about {topic}, break it down into exactly {num_chapters} logical chapters.

Course Configuration:
- Difficulty Level: {difficulty}
- Content Depth: {depth}
- Time per Chapter: approximately {time_per_chapter} minutes of study

{depth_instruction}

Document content:
{content}

For each chapter, provide:
1. Chapter number (1 to {num_chapters})
2. Title (concise, clear)
3. Summary (2-3 sentences appropriate for {depth} depth)
4. Key concepts (3-5 main ideas)
5. Difficulty: "{difficulty}"
6. Estimated time in minutes: {time_per_chapter}

Return ONLY valid JSON in this format:
{{
  "chapters": [
    {{
      "number": 1,
      "title": "...",
      "summary": "...",
      "key_concepts": [...],
      "difficulty": "{difficulty}",
      "estimated_time_minutes": {time_per_chapter}
    }}
  ]
}}"""
        else:
            prompt = f"""You are an expert educational content creator.

Create a structured course about {topic} with exactly {num_chapters} chapters.

Course Configuration:
- Difficulty Level: {difficulty}
- Content Depth: {depth}
- Time per Chapter: approximately {time_per_chapter} minutes of study

{depth_instruction}

For each chapter, provide:
1. Chapter number (1 to {num_chapters})
2. Title (concise, clear)
3. Summary (2-3 sentences appropriate for {depth} depth)
4. Key concepts (3-5 main ideas)
5. Difficulty: "{difficulty}"
6. Estimated time in minutes: {time_per_chapter}

Create chapters that progressively build knowledge from foundational to more advanced within the {difficulty} level.

Return ONLY valid JSON in this format:
{{
  "chapters": [
    {{
      "number": 1,
      "title": "...",
      "summary": "...",
      "key_concepts": [...],
      "difficulty": "{difficulty}",
      "estimated_time_minutes": {time_per_chapter}
    }}
  ]
}}"""

        # Call OpenAI API
        response = await self.client.chat.completions.create(
            model=self.default_model,
            max_tokens=settings.max_tokens_chapter,
            temperature=settings.temperature,
            messages=[
                {"role": "system", "content": "You are an expert educational content creator. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}  # Force JSON response
        )

        # Parse response
        response_text = response.choices[0].message.content

        # Parse JSON
        data = json.loads(response_text)

        # Convert to Chapter objects
        chapters = [Chapter(**chapter) for chapter in data["chapters"]]

        return chapters
    
    async def generate_questions(
        self, 
        chapter: Chapter, 
        num_mcq: int = 5, 
        num_true_false: int = 3
    ) -> Dict[str, Any]:
        """
        Generate quiz questions using OpenAI GPT.
        
        Args:
            chapter: The chapter object
            num_mcq: Number of multiple choice questions
            num_true_false: Number of true/false questions
            
        Returns:
            Dictionary with 'mcq' and 'true_false' question arrays
        """
        prompt = f"""Create assessment questions for this chapter.

Chapter: {chapter.title}
Summary: {chapter.summary}
Key Concepts: {', '.join(chapter.key_concepts)}
Difficulty: {chapter.difficulty}

Generate:
- {num_mcq} multiple choice questions (4 options each, one correct)
- {num_true_false} true/false questions

For each question include:
1. Question text
2. Options (for MCQ)
3. Correct answer
4. Explanation (why this answer is correct)
5. Difficulty level (easy/medium/hard)

Return ONLY valid JSON:
{{
  "mcq": [
    {{
      "id": "mcq_1",
      "question": "...",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correct_answer": "A",
      "explanation": "...",
      "difficulty": "medium"
    }}
  ],
  "true_false": [
    {{
      "id": "tf_1",
      "question": "...",
      "correct_answer": true,
      "explanation": "...",
      "difficulty": "easy"
    }}
  ]
}}"""
        
        response = await self.client.chat.completions.create(
            model=settings.model_question_generation,
            max_tokens=settings.max_tokens_question,
            temperature=settings.temperature,
            messages=[
                {"role": "system", "content": "You are an expert at creating educational assessments. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        response_text = response.choices[0].message.content
        return json.loads(response_text)
    
    async def generate_feedback(
        self, 
        user_progress: Dict[str, Any],
        weak_areas: List[str]
    ) -> str:
        """
        Generate personalized feedback using OpenAI GPT.
        
        Args:
            user_progress: User's progress data
            weak_areas: Areas where student needs improvement
            
        Returns:
            Feedback message as string
        """
        prompt = f"""You are a supportive learning mentor.

Student Progress:
- Overall Score: {user_progress.get('overall_score', 0):.0%}
- Weak Areas: {', '.join(weak_areas) if weak_areas else 'None'}

Provide:
1. Encouraging feedback on progress
2. Specific areas to review
3. Study recommendations
4. Readiness assessment (ready/not ready for exam)

Be supportive but honest. Keep it concise (3-4 paragraphs)."""
        
        response = await self.client.chat.completions.create(
            model=settings.model_student_feedback,
            max_tokens=settings.max_tokens_feedback,
            temperature=0.8,
            messages=[
                {"role": "system", "content": "You are a supportive learning mentor."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content
    
    async def check_answer(
        self, 
        question: str, 
        user_answer: str, 
        correct_answer: str
    ) -> Dict[str, Any]:
        """
        Check answer using OpenAI GPT.
        
        Args:
            question: The question text
            user_answer: User's answer
            correct_answer: The correct answer
            
        Returns:
            Dictionary with 'is_correct', 'explanation', 'score'
        """
        prompt = f"""Evaluate this student's answer.

Question: {question}
Student Answer: {user_answer}
Correct Answer: {correct_answer}

Provide:
1. Is the answer correct? (true/false)
2. Explanation of why it's correct or incorrect
3. Score (1.0 for correct, 0.0 for incorrect, or partial credit 0.0-1.0)

Return ONLY valid JSON:
{{
  "is_correct": true/false,
  "explanation": "...",
  "score": 0.0-1.0
}}"""
        
        response = await self.client.chat.completions.create(
            model=settings.model_answer_checking,
            max_tokens=settings.max_tokens_answer,
            temperature=0.3,
            messages=[
                {"role": "system", "content": "You are an objective assessment evaluator. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        response_text = response.choices[0].message.content
        return json.loads(response_text)
    
    async def answer_question(
        self, 
        question: str, 
        context: str
    ) -> str:
        """
        Answer student question using RAG context with OpenAI GPT.
        
        Args:
            question: Student's question
            context: Relevant context from the material
            
        Returns:
            Answer as string
        """
        prompt = f"""You are a helpful tutor. Answer the student's question using the provided context.

Context from the learning material:
{context}

Student's Question: {question}

Provide a clear, concise answer based on the context. If the context doesn't contain enough information, say so."""
        
        response = await self.client.chat.completions.create(
            model=settings.model_rag_query,
            max_tokens=settings.max_tokens_rag,
            temperature=0.7,
            messages=[
                {"role": "system", "content": "You are a helpful tutor."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content