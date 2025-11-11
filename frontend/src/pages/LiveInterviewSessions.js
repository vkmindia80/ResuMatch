import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Play, Clock, MessageSquare, BarChart3, Trash2,
  Plus, AlertCircle, CheckCircle, Loader
} from 'lucide-react';
import api from '../services/api';

const LiveInterviewSessions = () => {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deletingId, setDeletingId] = useState(null);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/live-interview/sessions');
      const sessionsData = Array.isArray(response.data)
        ? response.data
        : (response.data?.items || []);
      setSessions(sessionsData);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load sessions');
      setSessions([]); // Ensure sessions is always an array
    } finally {
      setLoading(false);
    }
  };

  const deleteSession = async (sessionId) => {
    if (!window.confirm('Are you sure you want to delete this session? This action cannot be undone.')) {
      return;
    }

    try {
      setDeletingId(sessionId);
      await api.delete(`/api/live-interview/sessions/${sessionId}`);
      setSessions(sessions.filter(s => s.id !== sessionId));
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to delete session');
    } finally {
      setDeletingId(null);
    }
  };

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const getStatusBadge = (status) => {
    const styles = {
      active: 'bg-green-100 text-green-700 border-green-300',
      completed: 'bg-blue-100 text-blue-700 border-blue-300',
      paused: 'bg-yellow-100 text-yellow-700 border-yellow-300',
      cancelled: 'bg-red-100 text-red-700 border-red-300'
    };
    
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium border ${styles[status] || styles.completed}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-secondary-50 py-8 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
              <p className="text-secondary-600">Loading sessions...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-secondary-50 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-secondary-900">Interview Sessions</h1>
            <p className="text-secondary-600 mt-1">View and manage your live interview sessions</p>
          </div>
          <button
            onClick={() => navigate('/live-interview')}
            data-testid="new-session-button"
            className="btn-primary"
          >
            <Plus size={20} className="mr-2" />
            New Session
          </button>
        </div>

        {error && (
          <div className="mb-6 card bg-red-50 border-2 border-red-200">
            <div className="flex items-center space-x-3 text-red-700">
              <AlertCircle size={24} />
              <div>
                <p className="font-medium">Error loading sessions</p>
                <p className="text-sm">{error}</p>
              </div>
            </div>
          </div>
        )}

        {sessions.length === 0 ? (
          <div className="card text-center py-16">
            <Play size={48} className="text-secondary-300 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-secondary-900 mb-2">
              No Sessions Yet
            </h2>
            <p className="text-secondary-600 mb-6">
              Start your first live interview session to get real-time AI assistance
            </p>
            <button
              onClick={() => navigate('/live-interview')}
              className="btn-primary"
            >
              <Plus size={20} className="mr-2" />
              Start Your First Session
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {sessions.map((session) => (
              <div key={session.id} className="card hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-secondary-900">
                        {session.title}
                      </h3>
                      {getStatusBadge(session.status)}
                    </div>
                    
                    <div className="flex flex-wrap items-center gap-4 text-sm text-secondary-600 mb-4">
                      <span className="flex items-center space-x-1">
                        <Clock size={16} />
                        <span>{formatDuration(session.duration_seconds)}</span>
                      </span>
                      <span className="flex items-center space-x-1">
                        <MessageSquare size={16} />
                        <span>{new Date(session.started_at).toLocaleDateString()}</span>
                      </span>
                      <span className="text-xs bg-secondary-100 px-2 py-1 rounded">
                        {session.model_preference === 'gpt-4' ? 'GPT-4' : 'Claude Sonnet'}
                      </span>
                      <span className="text-xs bg-primary-100 text-primary-700 px-2 py-1 rounded">
                        {session.resume_source === 'profile' ? 'Profile Resume' : 'Generated Resume'}
                      </span>
                    </div>

                    <div className="flex items-center space-x-3">
                      <button
                        onClick={() => navigate(`/live-interview/session/${session.id}/analysis`)}
                        data-testid={`view-analysis-${session.id}`}
                        className="btn-outline text-sm"
                      >
                        <BarChart3 size={16} className="mr-2" />
                        View Analysis
                      </button>
                      
                      <button
                        onClick={() => deleteSession(session.id)}
                        disabled={deletingId === session.id}
                        className="btn-outline-danger text-sm"
                      >
                        {deletingId === session.id ? (
                          <Loader size={16} className="mr-2 animate-spin" />
                        ) : (
                          <Trash2 size={16} className="mr-2" />
                        )}
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default LiveInterviewSessions;
