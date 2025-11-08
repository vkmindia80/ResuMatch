import React, { useState, useEffect } from 'react';
import { practiceSessionAPI, interviewAPI, jobAPI } from '../services/api';
import { Play, StopCircle, Clock, CheckCircle, TrendingUp, Calendar, BarChart3, Target } from 'lucide-react';

const PracticeSessions = () => {
  const [sessions, setSessions] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showStartModal, setShowStartModal] = useState(false);
  const [selectedJob, setSelectedJob] = useState('');
  const [selectedQuestions, setSelectedQuestions] = useState([]);
  const [activeSession, setActiveSession] = useState(null);
  const [sessionTime, setSessionTime] = useState(0);
  const [timerInterval, setTimerInterval] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (activeSession && !timerInterval) {
      const interval = setInterval(() => {
        setSessionTime(prev => prev + 1);
      }, 1000);
      setTimerInterval(interval);
    }
    
    return () => {
      if (timerInterval) {
        clearInterval(timerInterval);
      }
    };
  }, [activeSession]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [sessionsRes, analyticsRes, jobsRes] = await Promise.all([
        practiceSessionAPI.getAll(),
        practiceSessionAPI.getAnalytics(),
        jobAPI.getJobs()
      ]);
      
      setSessions(sessionsRes.data.items || sessionsRes.data || []);
      setAnalytics(analyticsRes.data);
      setJobs(jobsRes.data.items || jobsRes.data || []);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchQuestionsForJob = async (jobId) => {
    try {
      const response = await interviewAPI.getQuestions({ job_description_id: jobId });
      setQuestions(response.data.items || response.data || []);
    } catch (error) {
      console.error('Error fetching questions:', error);
    }
  };

  const handleStartSession = () => {
    setShowStartModal(true);
  };

  const handleJobSelect = (jobId) => {
    setSelectedJob(jobId);
    if (jobId) {
      fetchQuestionsForJob(jobId);
    } else {
      setQuestions([]);
      setSelectedQuestions([]);
    }
  };

  const handleQuestionToggle = (questionId) => {
    setSelectedQuestions(prev => 
      prev.includes(questionId)
        ? prev.filter(id => id !== questionId)
        : [...prev, questionId]
    );
  };

  const handleBeginPractice = async () => {
    if (!selectedJob || selectedQuestions.length === 0) {
      alert('Please select a job and at least one question');
      return;
    }

    try {
      const response = await practiceSessionAPI.create({
        job_description_id: selectedJob,
        question_ids: selectedQuestions,
        duration_seconds: 0,
        notes: ''
      });
      
      setActiveSession(response.data);
      setSessionTime(0);
      setShowStartModal(false);
      alert('Practice session started! Timer is running.');
    } catch (error) {
      console.error('Error creating session:', error);
      alert('Failed to start practice session');
    }
  };

  const handleStopSession = async () => {
    if (!activeSession) return;

    const notes = prompt('Add any notes about this practice session (optional):');

    try {
      await practiceSessionAPI.update(activeSession.id, {
        duration_seconds: sessionTime,
        completed: true,
        notes: notes || ''
      });
      
      if (timerInterval) {
        clearInterval(timerInterval);
        setTimerInterval(null);
      }
      
      setActiveSession(null);
      setSessionTime(0);
      await fetchData();
      alert('Practice session completed!');
    } catch (error) {
      console.error('Error completing session:', error);
      alert('Failed to complete session');
    }
  };

  const formatDuration = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="inline-block w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="mt-4 text-secondary-600">Loading practice sessions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-secondary-900">Interview Practice</h1>
          <p className="text-secondary-600 mt-2">Track your preparation and improve over time</p>
        </div>
        {!activeSession ? (
          <button
            onClick={handleStartSession}
            className="btn-primary flex items-center gap-2"
            data-testid="start-practice-btn"
          >
            <Play size={20} />
            Start Practice
          </button>
        ) : (
          <button
            onClick={handleStopSession}
            className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg font-semibold flex items-center gap-2"
            data-testid="stop-practice-btn"
          >
            <StopCircle size={20} />
            Stop Session ({formatDuration(sessionTime)})
          </button>
        )}
      </div>

      {/* Analytics Cards */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="card">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-primary-100 rounded-lg">
                <Target className="text-primary-600" size={24} />
              </div>
              <div>
                <p className="text-sm text-secondary-600">Total Sessions</p>
                <p className="text-2xl font-bold text-secondary-900">{analytics.total_sessions}</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-green-100 rounded-lg">
                <CheckCircle className="text-green-600" size={24} />
              </div>
              <div>
                <p className="text-sm text-secondary-600">Completed</p>
                <p className="text-2xl font-bold text-secondary-900">{analytics.completed_sessions}</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-blue-100 rounded-lg">
                <BarChart3 className="text-blue-600" size={24} />
              </div>
              <div>
                <p className="text-sm text-secondary-600">Questions Practiced</p>
                <p className="text-2xl font-bold text-secondary-900">{analytics.total_questions_practiced}</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-purple-100 rounded-lg">
                <Clock className="text-purple-600" size={24} />
              </div>
              <div>
                <p className="text-sm text-secondary-600">Total Time</p>
                <p className="text-2xl font-bold text-secondary-900">{analytics.total_time_formatted}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recent Activity */}
      {analytics?.recent_activity && (
        <div className="card mb-8">
          <h3 className="text-lg font-semibold text-secondary-900 mb-4">Recent Activity (Last 7 Days)</h3>
          <div className="flex items-center gap-6">
            <div>
              <p className="text-sm text-secondary-600">Sessions</p>
              <p className="text-2xl font-bold text-primary-600">{analytics.recent_activity.last_7_days}</p>
            </div>
            <div>
              <p className="text-sm text-secondary-600">Questions</p>
              <p className="text-2xl font-bold text-primary-600">{analytics.recent_activity.questions_last_7_days}</p>
            </div>
            <div className="flex-1 text-right">
              <span className="text-sm font-medium text-green-600">
                {analytics.completion_rate}% Completion Rate
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Sessions History */}
      <div className="card">
        <h3 className="text-lg font-semibold text-secondary-900 mb-4">Practice History</h3>
        
        {sessions.length === 0 ? (
          <div className="text-center py-12">
            <Calendar className="mx-auto text-secondary-400 mb-4" size={48} />
            <h3 className="text-lg font-semibold text-secondary-900 mb-2">No Practice Sessions Yet</h3>
            <p className="text-secondary-600 mb-6">Start practicing to track your progress</p>
            <button
              onClick={handleStartSession}
              className="btn-primary"
            >
              Start Your First Session
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {sessions.map((session) => {
              const job = jobs.find(j => j.id === session.job_description_id);
              return (
                <div key={session.id} className="border border-secondary-200 rounded-lg p-4 hover:border-primary-300 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h4 className="font-semibold text-secondary-900">
                          {job?.title || 'Practice Session'}
                        </h4>
                        {session.completed ? (
                          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-700 rounded-full flex items-center gap-1">
                            <CheckCircle size={12} />
                            Completed
                          </span>
                        ) : (
                          <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-700 rounded-full">
                            In Progress
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-secondary-600 mb-2">{job?.company || 'Company'}</p>
                      <div className="flex items-center gap-4 text-sm text-secondary-500">
                        <span className="flex items-center gap-1">
                          <BarChart3 size={14} />
                          {session.questions_count} questions
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock size={14} />
                          {formatDuration(session.duration_seconds)}
                        </span>
                        <span className="flex items-center gap-1">
                          <Calendar size={14} />
                          {new Date(session.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      {session.notes && (
                        <p className="text-sm text-secondary-600 mt-2 italic">"{session.notes}"</p>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Start Practice Modal */}
      {showStartModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6">
            <h2 className="text-2xl font-bold text-secondary-900 mb-4">Start Practice Session</h2>
            
            <div className="space-y-6">
              {/* Job Selection */}
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Select Job Description *
                </label>
                <select
                  value={selectedJob}
                  onChange={(e) => handleJobSelect(e.target.value)}
                  className="input"
                  data-testid="practice-job-select"
                >
                  <option value="">-- Select a job --</option>
                  {jobs.map((job) => (
                    <option key={job.id} value={job.id}>
                      {job.title} at {job.company}
                    </option>
                  ))}
                </select>
              </div>

              {/* Question Selection */}
              {selectedJob && questions.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Select Questions to Practice * ({selectedQuestions.length} selected)
                  </label>
                  <div className="max-h-64 overflow-y-auto border border-secondary-200 rounded-lg p-4 space-y-2">
                    {questions.map((question) => (
                      <label key={question.id} className="flex items-start gap-3 p-2 hover:bg-secondary-50 rounded cursor-pointer">
                        <input
                          type="checkbox"
                          checked={selectedQuestions.includes(question.id)}
                          onChange={() => handleQuestionToggle(question.id)}
                          className="mt-1"
                        />
                        <div className="flex-1">
                          <p className="text-sm text-secondary-900">{question.question}</p>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-xs px-2 py-1 bg-primary-100 text-primary-700 rounded">
                              {question.category}
                            </span>
                            <span className="text-xs px-2 py-1 bg-secondary-100 text-secondary-700 rounded">
                              {question.difficulty}
                            </span>
                          </div>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>
              )}

              {selectedJob && questions.length === 0 && (
                <div className="text-center py-8 bg-secondary-50 rounded-lg">
                  <p className="text-secondary-600">No questions available for this job.</p>
                  <p className="text-sm text-secondary-500 mt-2">Generate questions first from the Interview Prep page.</p>
                </div>
              )}
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => {
                  setShowStartModal(false);
                  setSelectedJob('');
                  setSelectedQuestions([]);
                  setQuestions([]);
                }}
                className="flex-1 btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={handleBeginPractice}
                className="flex-1 btn-primary"
                disabled={!selectedJob || selectedQuestions.length === 0}
                data-testid="begin-practice-btn"
              >
                Begin Practice
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PracticeSessions;
