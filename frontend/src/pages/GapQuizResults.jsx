import { useLocation, Link, Navigate, useNavigate } from 'react-router-dom';
import Header from '../components/Header';

function GapQuizResults() {
  const location = useLocation();
  const navigate = useNavigate();
  const { quiz, questions, answers, analysis, course } = location.state || {};

  // Redirect if no data
  if (!questions || !answers) {
    return <Navigate to="/app/my-courses" replace />;
  }

  // Calculate scores
  const totalQuestions = questions.length;
  const correctCount = Object.values(answers).filter((a) => a.isCorrect).length;
  const scorePercent = Math.round((correctCount / totalQuestions) * 100);

  // Separate stats for wrong answers vs extra questions
  const wrongAnswerQuestions = questions.filter((q) => q.source === 'wrong_answer');
  const extraQuestions = questions.filter((q) => q.source === 'extra');

  const wrongAnswerCorrect = wrongAnswerQuestions.filter((q, idx) => {
    const originalIdx = questions.indexOf(q);
    return answers[originalIdx]?.isCorrect;
  }).length;

  const extraCorrect = extraQuestions.filter((q, idx) => {
    const originalIdx = questions.indexOf(q);
    return answers[originalIdx]?.isCorrect;
  }).length;

  // Get score message and color
  const getScoreInfo = () => {
    if (scorePercent >= 80) {
      return { message: 'Excellent improvement!', color: 'text-green-600', bg: 'bg-green-100' };
    } else if (scorePercent >= 60) {
      return { message: 'Good progress!', color: 'text-yellow-600', bg: 'bg-yellow-100' };
    } else {
      return { message: 'Keep practicing!', color: 'text-red-600', bg: 'bg-red-100' };
    }
  };

  const scoreInfo = getScoreInfo();

  const handleRetakeQuiz = () => {
    navigate(`/app/mentor/${quiz?.course_slug || course?.slug}`, {
      state: { course },
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="max-w-2xl mx-auto px-4 py-8">
        {/* Score Card */}
        <div className="bg-white rounded-xl shadow-sm p-8 text-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Gap Quiz Complete</h1>
          <p className="text-gray-500 mb-6">{analysis?.course_topic || course?.topic || 'Course Review'}</p>

          {/* Score Circle */}
          <div
            className={`inline-flex items-center justify-center w-32 h-32 rounded-full ${scoreInfo.bg} mb-4`}
          >
            <span className={`text-4xl font-bold ${scoreInfo.color}`}>{scorePercent}%</span>
          </div>

          <p className={`text-xl font-semibold ${scoreInfo.color} mb-2`}>{scoreInfo.message}</p>
          <p className="text-gray-600">
            You got {correctCount} out of {totalQuestions} questions correct
          </p>
        </div>

        {/* Breakdown Stats */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          {wrongAnswerQuestions.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm p-4 text-center">
              <div className="text-3xl font-bold text-orange-600 mb-1">
                {wrongAnswerCorrect}/{wrongAnswerQuestions.length}
              </div>
              <p className="text-sm text-gray-500">Wrong Answers Fixed</p>
            </div>
          )}
          {extraQuestions.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm p-4 text-center">
              <div className="text-3xl font-bold text-purple-600 mb-1">
                {extraCorrect}/{extraQuestions.length}
              </div>
              <p className="text-sm text-gray-500">Extra Questions</p>
            </div>
          )}
        </div>

        {/* Improvement Message */}
        {wrongAnswerQuestions.length > 0 && wrongAnswerCorrect > 0 && (
          <div className="bg-green-50 border border-green-200 rounded-xl p-4 mb-6">
            <div className="flex items-center gap-3">
              <div className="flex-shrink-0 w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                <svg
                  className="w-5 h-5 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
              <div>
                <p className="font-medium text-green-900">
                  You corrected {wrongAnswerCorrect} of your previous mistakes!
                </p>
                <p className="text-sm text-green-700">Great job learning from your errors.</p>
              </div>
            </div>
          </div>
        )}

        {/* Question Review */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-900">Review Answers</h2>

          {questions.map((question, index) => {
            const answer = answers[index];
            const isCorrect = answer?.isCorrect;

            return (
              <div
                key={index}
                className={`bg-white rounded-xl shadow-sm p-5 border-l-4 ${
                  isCorrect ? 'border-green-500' : 'border-red-500'
                }`}
              >
                {/* Question Number, Type & Source */}
                <div className="flex items-center gap-2 mb-2 flex-wrap">
                  <span
                    className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium text-white ${
                      isCorrect ? 'bg-green-500' : 'bg-red-500'
                    }`}
                  >
                    {index + 1}
                  </span>
                  <span
                    className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                      question.source === 'wrong_answer'
                        ? 'bg-orange-100 text-orange-700'
                        : 'bg-purple-100 text-purple-700'
                    }`}
                  >
                    {question.source === 'wrong_answer' ? 'Review' : 'Extra'}
                  </span>
                  <span className="text-xs text-gray-400 uppercase">
                    {question.type === 'mcq' ? 'Multiple Choice' : 'True/False'}
                  </span>
                </div>

                {/* Chapter/Concept Context */}
                {question.chapter_title && (
                  <p className="text-xs text-gray-400 mb-2">
                    Ch. {question.chapter_number}: {question.chapter_title}
                  </p>
                )}
                {question.target_concept && (
                  <p className="text-xs text-gray-400 mb-2">Concept: {question.target_concept}</p>
                )}

                {/* Question Text */}
                <p className="text-gray-900 font-medium mb-3">{question.question}</p>

                {/* Answer Details */}
                <div className="space-y-2 text-sm">
                  <div className="flex items-start gap-2">
                    <span className="text-gray-500 w-24 flex-shrink-0">Your answer:</span>
                    <span className={isCorrect ? 'text-green-600' : 'text-red-600'}>
                      {question.type === 'mcq' ? (
                        <>
                          {answer?.selected}
                          {answer?.selected &&
                            question.options?.[answer.selected.charCodeAt(0) - 65] && (
                              <span className="text-gray-500 ml-1">
                                - {question.options[answer.selected.charCodeAt(0) - 65]}
                              </span>
                            )}
                        </>
                      ) : (
                        answer?.selected
                      )}
                    </span>
                  </div>

                  {!isCorrect && (
                    <div className="flex items-start gap-2">
                      <span className="text-gray-500 w-24 flex-shrink-0">Correct:</span>
                      <span className="text-green-600">
                        {question.type === 'mcq' ? (
                          <>
                            {question.correct_answer}
                            {question.options?.[question.correct_answer.charCodeAt(0) - 65] && (
                              <span className="text-gray-500 ml-1">
                                - {question.options[question.correct_answer.charCodeAt(0) - 65]}
                              </span>
                            )}
                          </>
                        ) : (
                          question.correct_answer
                        )}
                      </span>
                    </div>
                  )}

                  {/* Previous wrong answer note */}
                  {question.source === 'wrong_answer' && question.user_previous_answer && (
                    <div className="flex items-start gap-2">
                      <span className="text-gray-500 w-24 flex-shrink-0">Previously:</span>
                      <span className="text-orange-600">{question.user_previous_answer}</span>
                    </div>
                  )}

                  {/* Explanation */}
                  {question.explanation && (
                    <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                      <p className="text-gray-600">{question.explanation}</p>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Action Buttons */}
        <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={handleRetakeQuiz}
            className="px-6 py-3 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 transition-colors text-center"
          >
            Practice Again
          </button>
          <Link
            to="/app/my-courses"
            className="px-6 py-3 bg-gray-200 text-gray-700 font-medium rounded-lg hover:bg-gray-300 transition-colors text-center"
          >
            Back to Courses
          </Link>
        </div>
      </main>
    </div>
  );
}

export default GapQuizResults;
