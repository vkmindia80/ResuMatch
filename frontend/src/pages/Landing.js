import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Target, Briefcase, TrendingUp, Check } from 'lucide-react';

const Landing = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: Sparkles,
      title: 'Live Interview Assistant',
      description: 'Real-time AI answers during your actual interviews with speech recognition and instant responses.',
      featured: true
    },
    {
      icon: Target,
      title: 'ATS-Optimized Resumes',
      description: 'Create resumes that pass Applicant Tracking Systems with intelligent keyword optimization.'
    },
    {
      icon: Briefcase,
      title: 'Interview Preparation',
      description: 'Get personalized interview questions and STAR-format answers based on your profile.'
    },
    {
      icon: TrendingUp,
      title: 'Smart Matching',
      description: 'See how well your profile matches job requirements with our compatibility scoring.'
    }
  ];

  const benefits = [
    'Save hours of resume writing time',
    'Increase interview callbacks by 3x',
    'Practice with AI-generated interview questions',
    'Track multiple job applications',
    'Get instant ATS compatibility scores'
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center fade-in">
          <h1 className="text-5xl md:text-6xl font-bold text-secondary-900 mb-6">
            Land Your Dream Job with
            <span className="text-primary-600"> AI-Powered</span> Resumes
          </h1>
          <p className="text-xl text-secondary-600 mb-8 max-w-3xl mx-auto">
            Transform your profile into ATS-optimized resumes tailored to specific job descriptions,
            with comprehensive interview preparation including STAR-format Q&A.
          </p>
          <div className="flex justify-center space-x-4">
            <button
              onClick={() => navigate('/register')}
              data-testid="get-started-button"
              className="btn-primary px-8 py-3 text-lg"
            >
              Get Started Free
            </button>
            <button
              onClick={() => navigate('/login')}
              data-testid="login-button"
              className="btn-outline px-8 py-3 text-lg"
            >
              Sign In
            </button>
          </div>
        </div>

        {/* Features Section */}
        <div className="mt-24 grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div
                key={index}
                className={`card hover:shadow-lg transition-shadow duration-300 text-center ${
                  feature.featured ? 'ring-2 ring-primary-500 bg-gradient-to-br from-primary-50 to-white' : ''
                }`}
              >
                {feature.featured && (
                  <span className="inline-block px-3 py-1 bg-primary-500 text-white text-xs font-bold rounded-full mb-3">
                    NEW
                  </span>
                )}
                <div className="inline-flex items-center justify-center w-12 h-12 bg-primary-100 rounded-lg mb-4">
                  <Icon className="text-primary-600" size={24} />
                </div>
                <h3 className="text-lg font-semibold text-secondary-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-secondary-600 text-sm">{feature.description}</p>
              </div>
            );
          })}
        </div>

        {/* Benefits Section */}
        <div className="mt-24 card max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-secondary-900 text-center mb-8">
            Why Choose ResuMatch AI?
          </h2>
          <div className="grid md:grid-cols-2 gap-4">
            {benefits.map((benefit, index) => (
              <div key={index} className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-6 h-6 bg-primary-100 rounded-full flex items-center justify-center mt-1">
                  <Check className="text-primary-600" size={16} />
                </div>
                <span className="text-secondary-700">{benefit}</span>
              </div>
            ))}
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-24 text-center">
          <h2 className="text-3xl font-bold text-secondary-900 mb-4">
            Ready to Transform Your Job Search?
          </h2>
          <p className="text-lg text-secondary-600 mb-8">
            Join thousands of professionals who have landed their dream jobs with ResuMatch AI
          </p>
          <button
            onClick={() => navigate('/register')}
            className="btn-primary px-8 py-3 text-lg"
          >
            Start Building Your Resume Now
          </button>
        </div>
      </div>
    </div>
  );
};

export default Landing;
