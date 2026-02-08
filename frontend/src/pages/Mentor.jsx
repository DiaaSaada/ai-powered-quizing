import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import { mentorAPI, courseAPI } from '../services/api';

function Mentor() {
  const { courseSlug } = useParams();
  const navigate = useNavigate();

  // State
  const [analysis, setAnalysis] = useState(null);
  const [feedbackText, setFeedbackText] = useState('');
  const [quiz, setQuiz] = useState(null);
  const [course, setCourse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);

  // Quiz options
  const [includeHints, setIncludeHints] = useState(false);
  const [generateExtra, setGenerateExtra] = useState(false);
  const [extraCount, setExtraCount] = useState(5);

  // Fetch analysis on mount
  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        setLoading(true);
        setError(null);

        // First get analysis
        const analysisData = await mentorAPI.getAnalysis(courseSlug);
        setAnalysis(analysisData);

        // Extract course info from slug to find the course
        // Slug format: topic-difficulty-id (e.g., "design-patterns-intermediate-abc123")
        // We'll use the analysis data which contains course info
        if (analysisData.course_topic) {
          setCourse({
            topic: analysisData.course_topic,
            difficulty: analysisData.difficulty,
            slug: courseSlug,
          });
        }
      } catch (err) {
        console.error('Failed to fetch mentor analysis:', err);
        setError(err.response?.data?.detail || 'Failed to load mentor analysis');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysis();
  }, [courseSlug]);

  // Generate gap quiz
  const handleGenerateQuiz = async () => {
    try {
      setGenerating(true);
      setError(null);

      const response = await mentorAPI.generateQuiz(
        courseSlug,
        includeHints,
        generateExtra,
        extraCount
      );

      setAnalysis(response.analysis);
      setFeedbackText(response.feedback_text);
      setQuiz(response.quiz);
    } catch (err) {
      console.error('Failed to generate gap quiz:', err);
      setError(err.response?.data?.detail || 'Failed to generate quiz');
    } finally {
      setGenerating(false);
    }
  };

  // Start the quiz
  const handleStartQuiz = () => {
    navigate(`/app/mentor/${courseSlug}/quiz`, {
      state: {
        quiz,
        analysis,
        feedbackText,
        course,
      },
    });
  };

  // Score color helper
  const getScoreColor = (score) => {
    const percent = score * 100;
    if (percent >= 80) return 'text-green-600 bg-green-100';
    if (percent >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getScoreBarColor = (score) => {
    const percent = score * 100;
    if (percent >= 80) return 'bg-green-500';
    if (percent >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="flex flex-col items-center justify-center py-16">
          <div className="w-12 h-12 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin"></div>
          <p className="mt-4 text-gray-600">Analyzing your progress...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error && !analysis) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-4xl mx-auto px-4 py-16 text-center">
          <div className="text-red-500 text-5xl mb-4">!</div>
          <p className="text-red-600 mb-4">{error}</p>
          <Link
            to="/app/my-courses"
            className="text-purple-600 hover:underline"
          >
            Back to My Courses
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Page Header */}
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl shadow-lg p-6 mb-6 text-white">
          <div className="flex items-center gap-3 mb-2">
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <h1 className="text-2xl font-bold">AI Mentor</h1>
          </div>
          <p className="text-purple-100">
            {analysis?.course_topic || 'Course'} • {analysis?.difficulty || 'Unknown'} level
          </p>
        </div>

        {/* Overall Stats */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Your Progress Overview</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-3xl font-bold text-purple-600">
                {Math.round((analysis?.average_score || 0) * 100)}%
              </p>
              <p className="text-sm text-gray-500">Average Score</p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-3xl font-bold text-blue-600">
                {analysis?.total_chapters_completed || 0}/{analysis?.total_chapters || 0}
              </p>
              <p className="text-sm text-gray-500">Chapters Done</p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-3xl font-bold text-orange-600">
                {analysis?.weak_areas?.length || 0}
              </p>
              <p className="text-sm text-gray-500">Weak Areas</p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-3xl font-bold text-red-600">
                {analysis?.total_wrong_answers || 0}
              </p>
              <p className="text-sm text-gray-500">To Review</p>
            </div>
          </div>
        </div>

        {/* Weak Areas */}
        {analysis?.weak_areas?.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Weak Areas</h2>
            <div className="space-y-4">
              {analysis.weak_areas.map((area) => (
                <div key={area.chapter_number} className="border border-gray-100 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <span className="text-xs text-gray-400">Chapter {area.chapter_number}</span>
                      <h3 className="font-medium text-gray-900">{area.chapter_title}</h3>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-sm font-medium ${getScoreColor(area.score)}`}>
                      {Math.round(area.score * 100)}%
                    </span>
                  </div>
                  {/* Score bar */}
                  <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                    <div
                      className={`h-2 rounded-full transition-all ${getScoreBarColor(area.score)}`}
                      style={{ width: `${area.score * 100}%` }}
                    />
                  </div>
                  <p className="text-sm text-gray-500">
                    {area.questions_wrong} wrong out of {area.questions_total} questions
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* AI Feedback (shown after generating quiz) */}
        {feedbackText && (
          <div className="bg-purple-50 border border-purple-200 rounded-xl p-6 mb-6">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-purple-900 mb-2">Mentor Feedback</h3>
                <p className="text-purple-800 whitespace-pre-line">{feedbackText}</p>
              </div>
            </div>
          </div>
        )}

        {/* Quiz Options & Generate Button */}
        {!quiz && (
          <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Generate Gap Quiz</h2>
            <p className="text-gray-600 mb-4">
              Practice your weak areas with a personalized quiz. Wrong answers from your previous attempts are always included for free.
            </p>

            {/* Options */}
            <div className="space-y-4 mb-6">
              {/* Include Hints */}
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={includeHints}
                  onChange={(e) => setIncludeHints(e.target.checked)}
                  className="w-5 h-5 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                />
                <div>
                  <span className="font-medium text-gray-900">Include hints</span>
                  <p className="text-sm text-gray-500">Show hints for difficult questions</p>
                </div>
              </label>

              {/* Generate Extra Questions */}
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={generateExtra}
                  onChange={(e) => setGenerateExtra(e.target.checked)}
                  className="w-5 h-5 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                />
                <div>
                  <span className="font-medium text-gray-900">Generate extra AI questions</span>
                  <p className="text-sm text-gray-500">Add new practice questions targeting your weak concepts (uses AI tokens)</p>
                </div>
              </label>

              {/* Extra Question Count */}
              {generateExtra && (
                <div className="ml-8 flex items-center gap-3">
                  <label className="text-sm text-gray-600">Number of extra questions:</label>
                  <select
                    value={extraCount}
                    onChange={(e) => setExtraCount(Number(e.target.value))}
                    className="px-3 py-1 border border-gray-300 rounded-lg text-sm focus:ring-purple-500 focus:border-purple-500"
                  >
                    {[3, 5, 10, 15, 20].map((n) => (
                      <option key={n} value={n}>{n}</option>
                    ))}
                  </select>
                </div>
              )}
            </div>

            {/* Error message */}
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                {error}
              </div>
            )}

            {/* Generate Button */}
            <button
              onClick={handleGenerateQuiz}
              disabled={generating || (analysis?.total_wrong_answers === 0 && !generateExtra)}
              className="w-full px-6 py-3 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              {generating ? (
                <span className="flex items-center justify-center gap-2">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Generating Quiz...
                </span>
              ) : (
                'Generate Gap Quiz'
              )}
            </button>

            {analysis?.total_wrong_answers === 0 && !generateExtra && (
              <p className="mt-2 text-sm text-gray-500 text-center">
                No wrong answers to review. Enable "Generate extra AI questions" to practice more.
              </p>
            )}
          </div>
        )}

        {/* Quiz Ready Card */}
        {quiz && (
          <div className="bg-green-50 border border-green-200 rounded-xl p-6 mb-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-green-900">Quiz Ready!</h3>
                <p className="text-green-700 mt-1">
                  {quiz.wrong_answers_count} wrong answer{quiz.wrong_answers_count !== 1 ? 's' : ''} to retry
                  {quiz.extra_questions_count > 0 && (
                    <span> + {quiz.extra_questions_count} extra question{quiz.extra_questions_count !== 1 ? 's' : ''}</span>
                  )}
                </p>
                {quiz.cache_hit && (
                  <span className="inline-block mt-2 px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                    Using cached questions
                  </span>
                )}
              </div>
              <button
                onClick={handleStartQuiz}
                className="px-6 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors"
              >
                Start Quiz
              </button>
            </div>
          </div>
        )}

        {/* Back Link */}
        <div className="text-center">
          <Link
            to="/app/my-courses"
            className="text-gray-500 hover:text-gray-700"
          >
            Back to My Courses
          </Link>
        </div>
      </main>
    </div>
  );
}

export default Mentor;
