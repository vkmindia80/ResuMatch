import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { profileAPI, resumeAPI, jobAPI, interviewAPI, coverLetterAPI } from '../services/api';
import { User, FileText, Briefcase, MessageSquare, TrendingUp, Plus, Mail } from 'lucide-react';

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    completeness: 0,
    resumes: 0,
    jobs: 0,
    questions: 0,
    coverLetters: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [completeness, resumes, jobs, questions, coverLetters] = await Promise.all([
        profileAPI.getCompleteness(),
        resumeAPI.getResumes(),
        jobAPI.getJobs(),
        interviewAPI.getQuestions(),
        coverLetterAPI.getAll()
      ]);

      setStats({
        completeness: completeness.data.score,
        resumes: resumes.data.items?.length || resumes.data.length || 0,
        jobs: jobs.data.items?.length || jobs.data.length || 0,
        questions: questions.data.items?.length || questions.data.length || 0,
        coverLetters: coverLetters.data.items?.length || coverLetters.data.length || 0
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const quickActions = [
    {
      icon: User,
      title: 'Complete Profile',
      description: 'Build your professional profile',
      action: () => navigate('/profile'),
      color: 'primary'
    },
    {
      icon: Briefcase,
      title: 'Add Job Description',
      description: 'Paste a job posting to analyze',
      action: () => navigate('/jobs'),
      color: 'primary'
    },
    {
      icon: FileText,
      title: 'Generate Resume',
      description: 'Create an ATS-optimized resume',
      action: () => navigate('/resumes'),
      color: 'primary'
    },
    {
      icon: Mail,
      title: 'Create Cover Letter',
      description: 'AI-powered personalized letters',
      action: () => navigate('/cover-letters'),
      color: 'primary'
    },
    {
      icon: MessageSquare,
      title: 'Practice Interviews',
      description: 'Prepare with AI-generated questions',
      action: () => navigate('/interview-prep'),
      color: 'primary'
    }
  ];

  const statCards = [
    {
      icon: TrendingUp,
      label: 'Profile Completeness',
      value: `${stats.completeness}%`,
      color: stats.completeness >= 80 ? 'green' : stats.completeness >= 50 ? 'yellow' : 'red'
    },
    {
      icon: FileText,
      label: 'Resumes Created',
      value: stats.resumes,
      color: 'blue'
    },
    {
      icon: Briefcase,
      label: 'Jobs Analyzed',
      value: stats.jobs,
      color: 'purple'
    },
    {
      icon: MessageSquare,
      label: 'Interview Questions',
      value: stats.questions,
      color: 'pink'
    }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="inline-block w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="mt-4 text-secondary-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8" data-testid="dashboard">
      {/* Welcome Section */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-secondary-900 mb-2">
          Welcome back, {user?.full_name}!
        </h1>
        <p className="text-secondary-600">
          Let's continue building your path to success
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statCards.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div key={index} className="card hover:shadow-lg transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-secondary-600 mb-1">{stat.label}</p>
                  <p className="text-3xl font-bold text-secondary-900">{stat.value}</p>
                </div>
                <div className={`w-12 h-12 bg-${stat.color}-100 rounded-lg flex items-center justify-center`}>
                  <Icon className={`text-${stat.color}-600`} size={24} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-secondary-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {quickActions.map((action, index) => {
            const Icon = action.icon;
            return (
              <button
                key={index}
                onClick={action.action}
                data-testid={`quick-action-${action.title.toLowerCase().replace(/\s+/g, '-')}`}
                className="card hover:shadow-lg transition-all hover:scale-105 text-left"
              >
                <div className="flex flex-col items-start space-y-3">
                  <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                    <Icon className="text-primary-600" size={24} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-secondary-900 mb-1">{action.title}</h3>
                    <p className="text-sm text-secondary-600">{action.description}</p>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Getting Started Guide */}
      {stats.completeness < 50 && (
        <div className="card bg-primary-50 border-2 border-primary-200">
          <div className="flex items-start space-x-4">
            <div className="flex-shrink-0 w-12 h-12 bg-primary-600 rounded-full flex items-center justify-center">
              <TrendingUp className="text-white" size={24} />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-secondary-900 mb-2">
                Complete Your Profile to Get Started
              </h3>
              <p className="text-secondary-700 mb-4">
                Your profile is only {stats.completeness}% complete. Complete it to unlock the full power of ResuMatch AI.
              </p>
              <button
                onClick={() => navigate('/profile')}
                className="btn-primary"
              >
                Complete Profile Now
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
