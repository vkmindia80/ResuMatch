import React, { useState, useEffect } from 'react';
import { interviewAPI, jobAPI, practiceSessionAPI } from '../services/api';
import { Plus, MessageSquare, ChevronDown, ChevronUp, Clock, BarChart2, Play } from 'lucide-react';

const InterviewPrep = () => {
  const [questions, setQuestions] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [categories, setCategories] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [selectedJob, setSelectedJob] = useState('');
  const [questionCount, setQuestionCount] = useState(25);
  const [generating, setGenerating] = useState(false);
  const [expandedQuestion, setExpandedQuestion] = useState(null);
  const [filterCategory, setFilterCategory] = useState('');
  const [isPracticing, setIsPracticing] = useState(false);
  const [practiceStartTime, setPracticeStartTime] = useState(null);
  const [practicedQuestions, setPracticedQuestions] = useState([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [questionsRes, jobsRes, categoriesRes] = await Promise.all([
        interviewAPI.getQuestions(),
        jobAPI.getJobs(),
        interviewAPI.getCategories()
      ]);
      setQuestions(questionsRes.data);
      setJobs(jobsRes.data);
      setCategories(categoriesRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!selectedJob) {
      alert('Please select a job description');
      return;
    }

    setGenerating(true);
    try {
      await interviewAPI.generateQuestions({
        job_description_id: selectedJob,
        count: questionCount
      });
      await fetchData();
      setShowForm(false);
      setSelectedJob('');
    } catch (error) {
      console.error('Error generating questions:', error);
      alert('Error generating questions. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  const filteredQuestions = filterCategory
    ? questions.filter(q => q.category === filterCategory)
    : questions;

  const getCategoryBadgeColor = (category) => {
    const colors = {
      behavioral: 'bg-blue-100 text-blue-700',
      technical: 'bg-green-100 text-green-700',
      culture_fit: 'bg-purple-100 text-purple-700',
      situational: 'bg-yellow-100 text-yellow-700',
      common: 'bg-gray-100 text-gray-700'
    };
    return colors[category] || 'bg-gray-100 text-gray-700';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="inline-block w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="mt-4 text-secondary-600">Loading interview prep...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8" data-testid="interview-prep-page">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-secondary-900">Interview Preparation</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          data-testid="generate-questions-button"
          className="btn-primary flex items-center space-x-2"
        >
          <Plus size={18} />
          <span>Generate Questions</span>
        </button>
      </div>

      {showForm && (
        <div className="card mb-6">
          <h2 className="text-xl font-semibold text-secondary-900 mb-4">Generate Interview Questions</h2>
          <form onSubmit={handleGenerate} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">
                Select Job Description
              </label>
              <select
                value={selectedJob}
                onChange={(e) => setSelectedJob(e.target.value)}
                className="input-field"
                required
              >
                <option value="">-- Select a job --</option>
                {jobs.map((job) => (
                  <option key={job.id} value={job.id}>
                    {job.title} at {job.company}
                  </option>
                ))}
              </select>
              {jobs.length === 0 && (
                <p className="text-sm text-red-600 mt-2">
                  Please add a job description first.
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">
                Number of Questions
              </label>
              <input
                type="number"
                value={questionCount}
                onChange={(e) => setQuestionCount(parseInt(e.target.value))}
                className="input-field"
                min="5"
                max="50"
              />
            </div>

            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={generating || jobs.length === 0}
                className="btn-primary disabled:opacity-50"
              >
                {generating ? 'Generating...' : 'Generate Questions'}
              </button>
            </div>
          </form>
        </div>
      )}

      {questions.length > 0 && (
        <div className="mb-6 card">
          <label className="block text-sm font-medium text-secondary-700 mb-2">
            Filter by Category
          </label>
          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="input-field"
          >
            <option value="">All Categories</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {filteredQuestions.length > 0 ? (
        <div className="space-y-4">
          {filteredQuestions.map((question, index) => (
            <div key={question.id} className="card hover:shadow-lg transition-shadow">
              <div
                className="flex justify-between items-start cursor-pointer"
                onClick={() => setExpandedQuestion(expandedQuestion === question.id ? null : question.id)}
              >
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <span className="text-lg font-semibold text-secondary-900">Q{index + 1}</span>
                    <span className={`px-2 py-1 text-xs rounded-full ${getCategoryBadgeColor(question.category)}`}>
                      {question.category}
                    </span>
                    <span className="px-2 py-1 text-xs bg-secondary-100 text-secondary-700 rounded-full">
                      {question.difficulty}
                    </span>
                  </div>
                  <p className="text-secondary-900 font-medium">{question.question}</p>
                </div>
                {expandedQuestion === question.id ? <ChevronUp /> : <ChevronDown />}
              </div>

              {expandedQuestion === question.id && question.ai_generated_answer && (
                <div className="mt-4 p-4 bg-secondary-50 rounded-lg">
                  <h4 className="font-semibold text-secondary-900 mb-2">AI-Generated STAR Answer:</h4>
                  <div className="space-y-2 text-sm text-secondary-700">
                    {question.ai_generated_answer.situation && (
                      <div>
                        <strong>Situation:</strong> {question.ai_generated_answer.situation}
                      </div>
                    )}
                    {question.ai_generated_answer.task && (
                      <div>
                        <strong>Task:</strong> {question.ai_generated_answer.task}
                      </div>
                    )}
                    {question.ai_generated_answer.action && (
                      <div>
                        <strong>Action:</strong> {question.ai_generated_answer.action}
                      </div>
                    )}
                    {question.ai_generated_answer.result && (
                      <div>
                        <strong>Result:</strong> {question.ai_generated_answer.result}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="card text-center text-secondary-600 py-12">
          <MessageSquare size={48} className="mx-auto mb-4 text-secondary-400" />
          <p className="text-lg mb-2">No interview questions yet</p>
          <p className="text-sm">Generate questions based on job descriptions to start practicing</p>
        </div>
      )}
    </div>
  );
};

export default InterviewPrep;
