import { useState, useEffect } from 'react';
import { useLocation, Link, Navigate, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import { getTrueFalseOptions, getTrueFalseLabel } from '../utils/translations';

function GapQuiz() {
  const location = useLocation();
  const navigate = useNavigate();
  const { quiz, analysis, feedbackText, course } = location.state || {};
  const language = course?.language || 'en';

  // Quiz state
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [showFeedback, setShowFeedback] = useState(false);

  // Redirect if no quiz data
  if (!quiz) {
    return <Navigate to="/app/my-courses" replace />;
  }

  // Prepare questions on mount
  useEffect(() => {
    // Combine wrong answers and extra questions
    const wrongAnswerQuestions = (quiz.wrong_answers || []).map((q) => ({
      id: q.question_id,
      type: q.question_type,
      question: q.question_text,
      options: q.options?.map(opt => opt.replace(/^[A-D]\)\s*/, '')) || [],
      correct_answer: q.question_type === 'true_false'
        ? (q.correct_answer === true ? 'True' : 'False')
        : q.correct_answer,
      explanation: q.explanation,
      hint: q.hint,
      chapter_title: q.chapter_title,
      chapter_number: q.chapter_number,
      source: 'wrong_answer',
      user_previous_answer: q.user_answer,
    }));

    const extraQuestions = (quiz.extra_questions || []).map((q) => ({
      id: q.id,
      type: q.question_type,
      question: q.question_text,
      options: q.options?.map(opt => opt.replace(/^[A-D]\)\s*/, '')) || [],
      correct_answer: q.question_type === 'true_false'
        ? (q.correct_answer === true ? 'True' : 'False')
        : q.correct_answer,
      explanation: q.explanation,
      hint: q.hint,
      difficulty: q.difficulty,
      target_concept: q.target_concept,
      source_chapter: q.source_chapter,
      source: 'extra',
    }));

    // Shuffle all questions
    const allQuestions = [...wrongAnswerQuestions, ...extraQuestions];
    const shuffled = allQuestions.sort(() => Math.random() - 0.5);
    setQuestions(shuffled);
  }, [quiz]);

  const currentQuestion = questions[currentIndex];
  const totalQuestions = questions.length;
  const progress = totalQuestions > 0 ? ((currentIndex) / totalQuestions) * 100 : 0;

  const handleAnswerSelect = (answer) => {
    if (showFeedback) return;
    setSelectedAnswer(answer);
  };

  const handleSubmitAnswer = () => {
    if (selectedAnswer === null) return;

    setAnswers((prev) => ({
      ...prev,
      [currentIndex]: {
        selected: selectedAnswer,
        correct: currentQuestion.correct_answer,
        isCorrect: selectedAnswer === currentQuestion.correct_answer,
      },
    }));

    setShowFeedback(true);
  };

  const handleNextQuestion = () => {
    if (currentIndex < totalQuestions - 1) {
      setCurrentIndex((prev) => prev + 1);
      setSelectedAnswer(null);
      setShowFeedback(false);
    } else {
      // Quiz complete - navigate to results
      navigate(`/app/mentor/${quiz.course_slug}/results`, {
        state: {
          quiz,
          questions,
          answers: {
            ...answers,
            [currentIndex]: {
              selected: selectedAnswer,
              correct: currentQuestion.correct_answer,
              isCorrect: selectedAnswer === currentQuestion.correct_answer,
            },
          },
          analysis,
          feedbackText,
          course,
        },
      });
    }
  };

  // No questions state
  if (questions.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 text-lg">No questions available for this gap quiz.</p>
          <Link
            to="/app/my-courses"
            className="mt-4 inline-block px-6 py-3 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700"
          >
            Back to Courses
          </Link>
        </div>
      </div>
    );
  }

  if (!currentQuestion) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      {/* Progress Bar */}
      <div className="bg-white border-b">
        <div className="max-w-4xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
            <span>Question {currentIndex + 1} of {totalQuestions}</span>
            <span>{Math.round(progress)}% complete</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-purple-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Question Card */}
      <main className="max-w-2xl mx-auto px-4 py-8">
        <div className="bg-white rounded-xl shadow-sm p-6">
          {/* Source Badge */}
          <div className="flex items-center gap-2 mb-4">
            <span
              className={`inline-block px-3 py-1 text-xs font-medium rounded-full ${
                currentQuestion.source === 'wrong_answer'
                  ? 'bg-orange-100 text-orange-700'
                  : 'bg-purple-100 text-purple-700'
              }`}
            >
              {currentQuestion.source === 'wrong_answer' ? 'Wrong Answer Review' : 'Extra Practice'}
            </span>
            <span
              className={`inline-block px-3 py-1 text-xs font-medium rounded-full ${
                currentQuestion.type === 'mcq'
                  ? 'bg-blue-100 text-blue-700'
                  : 'bg-teal-100 text-teal-700'
              }`}
            >
              {currentQuestion.type === 'mcq' ? 'Multiple Choice' : 'True / False'}
            </span>
          </div>

          {/* Chapter Context */}
          {currentQuestion.chapter_title && (
            <p className="text-sm text-gray-500 mb-2">
              Chapter {currentQuestion.chapter_number}: {currentQuestion.chapter_title}
            </p>
          )}
          {currentQuestion.target_concept && (
            <p className="text-sm text-gray-500 mb-2">
              Concept: {currentQuestion.target_concept}
            </p>
          )}

          {/* Question Text */}
          <h2 className="text-xl font-semibold text-gray-900 mb-6">
            {currentQuestion.question}
          </h2>

          {/* Previous Wrong Answer Note */}
          {currentQuestion.source === 'wrong_answer' && currentQuestion.user_previous_answer && !showFeedback && (
            <div className="mb-4 p-3 bg-orange-50 border border-orange-200 rounded-lg">
              <p className="text-sm text-orange-700">
                You previously answered: <strong>
                  {currentQuestion.type === 'true_false'
                    ? getTrueFalseLabel(currentQuestion.user_previous_answer, language)
                    : currentQuestion.user_previous_answer}
                </strong>
              </p>
            </div>
          )}

          {/* Hint */}
          {quiz.include_hints && currentQuestion.hint && !showFeedback && (
            <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-700">
                <strong>Hint:</strong> {currentQuestion.hint}
              </p>
            </div>
          )}

          {/* Answer Options */}
          <div className="space-y-3">
            {currentQuestion.type === 'mcq' ? (
              // MCQ Options
              currentQuestion.options?.map((option, idx) => {
                const optionLetter = String.fromCharCode(65 + idx); // A, B, C, D
                const isSelected = selectedAnswer === optionLetter;
                const isCorrect = optionLetter === currentQuestion.correct_answer;
                const showCorrect = showFeedback && isCorrect;
                const showIncorrect = showFeedback && isSelected && !isCorrect;

                return (
                  <button
                    key={idx}
                    onClick={() => handleAnswerSelect(optionLetter)}
                    disabled={showFeedback}
                    className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                      showCorrect
                        ? 'border-green-500 bg-green-50'
                        : showIncorrect
                        ? 'border-red-500 bg-red-50'
                        : isSelected
                        ? 'border-purple-500 bg-purple-50'
                        : 'border-gray-200 hover:border-gray-300'
                    } ${showFeedback ? 'cursor-default' : 'cursor-pointer'}`}
                  >
                    <div className="flex items-start gap-3">
                      <span
                        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center font-medium ${
                          showCorrect
                            ? 'bg-green-500 text-white'
                            : showIncorrect
                            ? 'bg-red-500 text-white'
                            : isSelected
                            ? 'bg-purple-500 text-white'
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {optionLetter}
                      </span>
                      <span className="text-gray-700 pt-1">{option}</span>
                    </div>
                  </button>
                );
              })
            ) : (
              // True/False Options
              getTrueFalseOptions(language).map((opt) => {
                const isSelected = selectedAnswer === opt.value;
                const isCorrect = opt.value === currentQuestion.correct_answer;
                const showCorrect = showFeedback && isCorrect;
                const showIncorrect = showFeedback && isSelected && !isCorrect;

                return (
                  <button
                    key={opt.value}
                    onClick={() => handleAnswerSelect(opt.value)}
                    disabled={showFeedback}
                    className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                      showCorrect
                        ? 'border-green-500 bg-green-50'
                        : showIncorrect
                        ? 'border-red-500 bg-red-50'
                        : isSelected
                        ? 'border-purple-500 bg-purple-50'
                        : 'border-gray-200 hover:border-gray-300'
                    } ${showFeedback ? 'cursor-default' : 'cursor-pointer'}`}
                  >
                    <div className="flex items-center gap-3">
                      <span
                        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center font-medium ${
                          showCorrect
                            ? 'bg-green-500 text-white'
                            : showIncorrect
                            ? 'bg-red-500 text-white'
                            : isSelected
                            ? 'bg-purple-500 text-white'
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {opt.value === 'True' ? 'T' : 'F'}
                      </span>
                      <span className="text-gray-700 font-medium">{opt.label}</span>
                    </div>
                  </button>
                );
              })
            )}
          </div>

          {/* Feedback / Explanation */}
          {showFeedback && currentQuestion.explanation && (
            <div
              className={`mt-6 p-4 rounded-lg ${
                answers[currentIndex]?.isCorrect ||
                selectedAnswer === currentQuestion.correct_answer
                  ? 'bg-green-50 border border-green-200'
                  : 'bg-red-50 border border-red-200'
              }`}
            >
              <p
                className={`font-medium mb-1 ${
                  answers[currentIndex]?.isCorrect ||
                  selectedAnswer === currentQuestion.correct_answer
                    ? 'text-green-700'
                    : 'text-red-700'
                }`}
              >
                {answers[currentIndex]?.isCorrect ||
                selectedAnswer === currentQuestion.correct_answer
                  ? 'Correct!'
                  : 'Incorrect'}
              </p>
              <p className="text-gray-600 text-sm">{currentQuestion.explanation}</p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="mt-6 flex justify-end gap-3">
            {!showFeedback ? (
              <button
                onClick={handleSubmitAnswer}
                disabled={selectedAnswer === null}
                className="px-6 py-3 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                Submit Answer
              </button>
            ) : (
              <button
                onClick={handleNextQuestion}
                className="px-6 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors"
              >
                {currentIndex < totalQuestions - 1 ? 'Next Question' : 'See Results'}
              </button>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default GapQuiz;
