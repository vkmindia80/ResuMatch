import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  TrendingUp, MessageSquare, Brain, Clock, Award,
  CheckCircle, AlertCircle, ArrowLeft, Download, Sparkles
} from 'lucide-react';
import api from '../services/api';

const LiveInterviewAnalysis = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [session, setSession] = useState(null);
  const [transcript, setTranscript] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadSessionData();
  }, [sessionId]);

  const loadSessionData = async () => {
    try {
      setLoading(true);
      
      // Load session
      const sessionResponse = await api.get(`/api/live-interview/sessions/${sessionId}`);
      setSession(sessionResponse.data);
      
      // Load transcript
      const transcriptResponse = await api.get(`/api/live-interview/sessions/${sessionId}/transcript`);
      setTranscript(transcriptResponse.data);
      
      // Try to load existing analysis
      try {
        const analysisResponse = await api.get(`/api/live-interview/sessions/${sessionId}/analysis`);
        setAnalysis(analysisResponse.data);
      } catch (err) {
        // Analysis doesn't exist yet, will need to generate
        console.log('No existing analysis, will generate new one');
      }
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load session data');
    } finally {
      setLoading(false);
    }
  };

  const generateAnalysis = async () => {
    try {
      setAnalyzing(true);
      const response = await api.post(`/api/live-interview/sessions/${sessionId}/analyze`);
      setAnalysis(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate analysis');
    } finally {
      setAnalyzing(false);
    }
  };

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score) => {
    if (score >= 80) return 'bg-green-100 border-green-300';
    if (score >= 60) return 'bg-yellow-100 border-yellow-300';
    return 'bg-red-100 border-red-300';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-secondary-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-secondary-600">Loading session data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-secondary-50 py-8 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="card">
            <div className="flex items-center space-x-3 text-red-600 mb-4">
              <AlertCircle size={24} />
              <h2 className="text-xl font-semibold">Error</h2>
            </div>
            <p className="text-secondary-700 mb-4">{error}</p>
            <button onClick={() => navigate('/live-interview')} className="btn-outline">
              <ArrowLeft size={16} className="mr-2" />
              Back to Live Interview
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-secondary-50 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate('/live-interview/sessions')}
            className="btn-outline mb-4"
          >
            <ArrowLeft size={16} className="mr-2" />
            Back to Sessions
          </button>
          
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-secondary-900">{session?.title}</h1>
              <p className="text-secondary-600 mt-1">
                {session?.started_at && new Date(session.started_at).toLocaleString()}
              </p>
            </div>
            {session && (
              <div className="text-right">
                <div className="text-2xl font-bold text-primary-600">
                  {formatDuration(session.duration_seconds)}
                </div>
                <div className="text-sm text-secondary-600">Duration</div>
              </div>
            )}
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="card bg-gradient-to-br from-blue-50 to-white border-2 border-blue-200">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center">
                <MessageSquare className="text-white" size={24} />
              </div>
              <div>
                <div className="text-2xl font-bold text-secondary-900">
                  {transcript?.entries?.length || 0}
                </div>
                <div className="text-sm text-secondary-600">Questions Detected</div>
              </div>
            </div>
          </div>

          <div className="card bg-gradient-to-br from-green-50 to-white border-2 border-green-200">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center">
                <Brain className="text-white" size={24} />
              </div>
              <div>
                <div className="text-2xl font-bold text-secondary-900">
                  {transcript?.ai_answers?.length || 0}
                </div>
                <div className="text-sm text-secondary-600">AI Answers Generated</div>
              </div>
            </div>
          </div>

          <div className="card bg-gradient-to-br from-purple-50 to-white border-2 border-purple-200">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-purple-500 rounded-lg flex items-center justify-center">
                <Sparkles className="text-white" size={24} />
              </div>
              <div>
                <div className="text-2xl font-bold text-secondary-900">
                  {session?.model_preference === 'gpt-4' ? 'GPT-4' : 'Claude'}
                </div>
                <div className="text-sm text-secondary-600">AI Model Used</div>
              </div>
            </div>
          </div>
        </div>

        {/* Analysis Section */}
        {!analysis && !analyzing && (
          <div className="card bg-gradient-to-br from-primary-50 to-white border-2 border-primary-200 mb-6">
            <div className="text-center py-8">
              <Award size={48} className="text-primary-600 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-secondary-900 mb-2">
                Generate Performance Analysis
              </h2>
              <p className="text-secondary-600 mb-6 max-w-2xl mx-auto">
                Get AI-powered insights on your interview performance including scoring,
                strengths, and personalized improvement recommendations.
              </p>
              <button
                onClick={generateAnalysis}
                data-testid="generate-analysis-button"
                className="btn-primary"
              >
                <Sparkles size={20} className="mr-2" />
                Generate Analysis
              </button>
            </div>
          </div>
        )}

        {analyzing && (
          <div className="card mb-6">
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
              <p className="text-secondary-600">Analyzing your performance...</p>
            </div>
          </div>
        )}

        {analysis && (
          <>
            {/* Performance Scores */}
            <div className="card mb-6">
              <h2 className="text-xl font-semibold text-secondary-900 mb-6">Performance Scores</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {/* Overall Score */}
                <div className={`rounded-lg border-2 p-6 text-center ${getScoreBgColor(analysis.overall_score)}`}>
                  <div className={`text-4xl font-bold mb-2 ${getScoreColor(analysis.overall_score)}`}>
                    {Math.round(analysis.overall_score)}
                  </div>
                  <div className="text-sm font-medium text-secondary-700">Overall</div>
                </div>

                {/* Communication Score */}
                <div className={`rounded-lg border-2 p-6 text-center ${getScoreBgColor(analysis.communication_score)}`}>
                  <div className={`text-4xl font-bold mb-2 ${getScoreColor(analysis.communication_score)}`}>
                    {Math.round(analysis.communication_score)}
                  </div>
                  <div className="text-sm font-medium text-secondary-700">Communication</div>
                </div>

                {/* Technical Score */}
                <div className={`rounded-lg border-2 p-6 text-center ${getScoreBgColor(analysis.technical_score)}`}>
                  <div className={`text-4xl font-bold mb-2 ${getScoreColor(analysis.technical_score)}`}>
                    {Math.round(analysis.technical_score)}
                  </div>
                  <div className="text-sm font-medium text-secondary-700">Technical</div>
                </div>

                {/* Behavioral Score */}
                <div className={`rounded-lg border-2 p-6 text-center ${getScoreBgColor(analysis.behavioral_score)}`}>
                  <div className={`text-4xl font-bold mb-2 ${getScoreColor(analysis.behavioral_score)}`}>
                    {Math.round(analysis.behavioral_score)}
                  </div>
                  <div className="text-sm font-medium text-secondary-700">Behavioral</div>
                </div>
              </div>
            </div>

            {/* Strengths and Improvements */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              {/* Strengths */}
              <div className="card bg-gradient-to-br from-green-50 to-white">
                <div className="flex items-center space-x-2 mb-4">
                  <CheckCircle className="text-green-600" size={24} />
                  <h3 className="text-lg font-semibold text-secondary-900">Strengths</h3>
                </div>
                <ul className="space-y-3">
                  {analysis.strengths?.map((strength, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <CheckCircle className="text-green-500 flex-shrink-0 mt-1" size={16} />
                      <span className="text-secondary-700">{strength}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Areas for Improvement */}
              <div className="card bg-gradient-to-br from-yellow-50 to-white">
                <div className="flex items-center space-x-2 mb-4">
                  <TrendingUp className="text-yellow-600" size={24} />
                  <h3 className="text-lg font-semibold text-secondary-900">Areas for Improvement</h3>
                </div>
                <ul className="space-y-3">
                  {analysis.areas_for_improvement?.map((area, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <TrendingUp className="text-yellow-500 flex-shrink-0 mt-1" size={16} />
                      <span className="text-secondary-700">{area}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Detailed Feedback */}
            <div className="card mb-6">
              <h2 className="text-xl font-semibold text-secondary-900 mb-4">Detailed Feedback</h2>
              <div className="prose prose-secondary max-w-none">
                <p className="text-secondary-700 leading-relaxed whitespace-pre-wrap">
                  {analysis.detailed_feedback}
                </p>
              </div>
            </div>
          </>
        )}

        {/* Transcript */}
        <div className="card">
          <h2 className="text-xl font-semibold text-secondary-900 mb-4">Full Transcript</h2>
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {transcript?.entries?.length === 0 ? (
              <p className="text-center text-secondary-500 py-8">No transcript available</p>
            ) : (
              transcript?.entries?.map((entry, index) => (
                <div key={index} className="bg-secondary-50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-secondary-700">
                      Question {index + 1}
                    </span>
                    <span className="text-xs text-secondary-500">
                      {new Date(entry.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-secondary-800">{entry.text}</p>
                  
                  {/* Show AI answer if available */}
                  {transcript.ai_answers?.[index] && (
                    <div className="mt-3 pt-3 border-t border-secondary-200">
                      <div className="flex items-center space-x-2 mb-2">
                        <Brain size={16} className="text-green-600" />
                        <span className="text-sm font-medium text-green-700">AI Answer:</span>
                      </div>
                      <p className="text-secondary-700 text-sm">
                        {transcript.ai_answers[index].answer}
                      </p>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveInterviewAnalysis;
