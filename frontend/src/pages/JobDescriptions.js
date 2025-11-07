import React, { useState, useEffect } from 'react';
import { jobAPI, matchScoreAPI } from '../services/api';
import { Plus, Trash2, Briefcase, MapPin, Building, Target, TrendingUp } from 'lucide-react';

const JobDescriptions = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [showMatchScore, setShowMatchScore] = useState(false);
  const [matchScoreData, setMatchScoreData] = useState(null);
  const [loadingMatchScore, setLoadingMatchScore] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    company: '',
    location: '',
    job_type: 'Full-time',
    description: ''
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      const response = await jobAPI.getJobs();
      setJobs(response.data);
    } catch (error) {
      console.error('Error fetching jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await jobAPI.createJob(formData);
      await fetchJobs();
      setShowForm(false);
      setFormData({
        title: '',
        company: '',
        location: '',
        job_type: 'Full-time',
        description: ''
      });
    } catch (error) {
      console.error('Error creating job:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this job description?')) {
      try {
        await jobAPI.deleteJob(id);
        await fetchJobs();
      } catch (error) {
        console.error('Error deleting job:', error);
      }
    }
  };

  const handleViewMatchScore = async (jobId) => {
    try {
      setLoadingMatchScore(true);
      setShowMatchScore(true);
      const response = await matchScoreAPI.getScore(jobId);
      setMatchScoreData(response.data);
    } catch (error) {
      console.error('Error fetching match score:', error);
      alert('Failed to calculate match score. Please ensure your profile is complete.');
      setShowMatchScore(false);
    } finally {
      setLoadingMatchScore(false);
    }
  };

  const getMatchColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="inline-block w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="mt-4 text-secondary-600">Loading jobs...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8" data-testid="jobs-page">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-secondary-900">Job Descriptions</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          data-testid="add-job-button"
          className="btn-primary flex items-center space-x-2"
        >
          <Plus size={18} />
          <span>Add Job</span>
        </button>
      </div>

      {showForm && (
        <div className="card mb-6">
          <h2 className="text-xl font-semibold text-secondary-900 mb-4">Add New Job Description</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">Job Title</label>
                <input
                  type="text"
                  data-testid="job-title-input"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="input-field"
                  placeholder="e.g., Senior Software Engineer"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">Company</label>
                <input
                  type="text"
                  data-testid="job-company-input"
                  value={formData.company}
                  onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                  className="input-field"
                  placeholder="e.g., Google"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">Location</label>
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  className="input-field"
                  placeholder="e.g., San Francisco, CA"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">Job Type</label>
                <select
                  value={formData.job_type}
                  onChange={(e) => setFormData({ ...formData, job_type: e.target.value })}
                  className="input-field"
                >
                  <option value="Full-time">Full-time</option>
                  <option value="Part-time">Part-time</option>
                  <option value="Contract">Contract</option>
                  <option value="Internship">Internship</option>
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">Job Description</label>
              <textarea
                data-testid="job-description-input"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="input-field"
                rows="10"
                placeholder="Paste the job description here..."
                required
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
                data-testid="save-job-button"
                disabled={saving}
                className="btn-primary disabled:opacity-50"
              >
                {saving ? 'Saving...' : 'Save Job'}
              </button>
            </div>
          </form>
        </div>
      )}

      {jobs.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {jobs.map((job) => (
            <div key={job.id} className="card hover:shadow-lg transition-shadow">
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-secondary-900 mb-2">{job.title}</h3>
                  <div className="space-y-1 text-sm text-secondary-600">
                    <div className="flex items-center space-x-2">
                      <Building size={16} />
                      <span>{job.company}</span>
                    </div>
                    {job.location && (
                      <div className="flex items-center space-x-2">
                        <MapPin size={16} />
                        <span>{job.location}</span>
                      </div>
                    )}
                    {job.job_type && (
                      <div className="flex items-center space-x-2">
                        <Briefcase size={16} />
                        <span>{job.job_type}</span>
                      </div>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(job.id)}
                  className="text-red-600 hover:text-red-700 transition-colors"
                >
                  <Trash2 size={18} />
                </button>
              </div>
              {job.parsed_keywords && job.parsed_keywords.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-4">
                  {job.parsed_keywords.slice(0, 5).map((keyword, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 bg-primary-100 text-primary-700 text-xs rounded-full"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              )}
              <button
                onClick={() => handleViewMatchScore(job.id)}
                className="mt-4 w-full btn-secondary text-sm flex items-center justify-center gap-2"
                data-testid={`match-score-btn-${job.id}`}
              >
                <Target size={16} />
                View Match Score
              </button>
            </div>
          ))}
        </div>
      ) : (
        <div className="card text-center text-secondary-600 py-12">
          <Briefcase size={48} className="mx-auto mb-4 text-secondary-400" />
          <p className="text-lg mb-2">No job descriptions yet</p>
          <p className="text-sm">Click "Add Job" to start analyzing job postings</p>
        </div>
      )}

      {/* Match Score Modal */}
      {showMatchScore && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto p-6">
            <div className="flex justify-between items-start mb-6">
              <h2 className="text-2xl font-bold text-secondary-900">Job Match Score</h2>
              <button
                onClick={() => setShowMatchScore(false)}
                className="text-secondary-400 hover:text-secondary-600"
              >
                ✕
              </button>
            </div>

            {loadingMatchScore ? (
              <div className="text-center py-12">
                <div className="inline-block w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
                <p className="mt-4 text-secondary-600">Calculating match score...</p>
              </div>
            ) : matchScoreData ? (
              <div className="space-y-6">
                {/* Overall Score */}
                <div className="text-center pb-6 border-b">
                  <div className={`inline-flex items-center justify-center w-32 h-32 rounded-full text-4xl font-bold ${getMatchColor(matchScoreData.overall_score)}`}>
                    {matchScoreData.overall_score}%
                  </div>
                  <p className="text-lg font-semibold text-secondary-900 mt-4">{matchScoreData.match_level}</p>
                  <p className="text-sm text-secondary-600">Confidence: {matchScoreData.confidence}</p>
                </div>

                {/* Score Breakdown */}
                <div>
                  <h3 className="text-lg font-semibold text-secondary-900 mb-4">Score Breakdown</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.entries(matchScoreData.breakdown).map(([category, data]) => (
                      <div key={category} className="card">
                        <div className="flex justify-between items-center mb-2">
                          <span className="font-medium text-secondary-900 capitalize">{category}</span>
                          <span className={`px-3 py-1 rounded-full text-sm font-bold ${getMatchColor(data.score)}`}>
                            {data.score}%
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${data.score >= 80 ? 'bg-green-600' : data.score >= 60 ? 'bg-yellow-600' : 'bg-red-600'}`}
                            style={{ width: `${data.score}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Skills Gap */}
                {matchScoreData.skills_gap && (
                  <div>
                    <h3 className="text-lg font-semibold text-secondary-900 mb-4">Skills Gap Analysis</h3>
                    {matchScoreData.skills_gap.critical_missing_skills?.length > 0 && (
                      <div className="card mb-4">
                        <h4 className="font-medium text-red-700 mb-2">Critical Missing Skills</h4>
                        <div className="flex flex-wrap gap-2">
                          {matchScoreData.skills_gap.critical_missing_skills.map((skill, idx) => (
                            <span key={idx} className="px-3 py-1 bg-red-100 text-red-700 text-sm rounded-full">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {matchScoreData.skills_gap.nice_to_have_missing_skills?.length > 0 && (
                      <div className="card">
                        <h4 className="font-medium text-yellow-700 mb-2">Nice-to-Have Skills</h4>
                        <div className="flex flex-wrap gap-2">
                          {matchScoreData.skills_gap.nice_to_have_missing_skills.map((skill, idx) => (
                            <span key={idx} className="px-3 py-1 bg-yellow-100 text-yellow-700 text-sm rounded-full">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Recommendations */}
                {matchScoreData.recommendations && matchScoreData.recommendations.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-secondary-900 mb-4">Recommendations</h3>
                    <div className="space-y-3">
                      {matchScoreData.recommendations.map((rec, idx) => (
                        <div key={idx} className="card border-l-4 border-primary-600">
                          <div className="flex items-start gap-3">
                            <TrendingUp className="text-primary-600 flex-shrink-0 mt-1" size={20} />
                            <div>
                              <h4 className="font-medium text-secondary-900 mb-1">{rec.title}</h4>
                              <p className="text-sm text-secondary-700 mb-2">{rec.description}</p>
                              <p className="text-sm text-primary-600">{rec.action}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : null}

            <div className="flex justify-end mt-6">
              <button
                onClick={() => setShowMatchScore(false)}
                className="btn-primary"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default JobDescriptions;
