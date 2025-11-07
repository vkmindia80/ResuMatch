import React, { useState, useEffect } from 'react';
import { resumeAPI, jobAPI } from '../services/api';
import { Plus, FileText, Download, Trash2, Eye } from 'lucide-react';

const Resumes = () => {
  const [resumes, setResumes] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [selectedJob, setSelectedJob] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState('template_1');
  const [templates, setTemplates] = useState([]);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [resumesRes, jobsRes, templatesRes] = await Promise.all([
        resumeAPI.getResumes(),
        jobAPI.getJobs(),
        resumeAPI.getTemplates()
      ]);
      // Backend returns paginated response for both resumes and jobs: { items: [...], total: X, skip: Y, limit: Z }
      const resumesData = resumesRes.data.items || resumesRes.data || [];
      const jobsData = jobsRes.data.items || jobsRes.data || [];
      setResumes(resumesData);
      setJobs(jobsData);
      setTemplates(templatesRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
      setResumes([]); // Set empty array on error
      setJobs([]); // Set empty array on error
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    setGenerating(true);
    try {
      await resumeAPI.generateResume({
        job_description_id: selectedJob || null,
        template_id: selectedTemplate
      });
      await fetchData();
      setShowForm(false);
      setSelectedJob('');
    } catch (error) {
      console.error('Error generating resume:', error);
      alert('Error generating resume. Please ensure your profile is complete.');
    } finally {
      setGenerating(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this resume?')) {
      try {
        await resumeAPI.deleteResume(id);
        await fetchData();
      } catch (error) {
        console.error('Error deleting resume:', error);
      }
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="inline-block w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="mt-4 text-secondary-600">Loading resumes...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8" data-testid="resumes-page">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-secondary-900">My Resumes</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          data-testid="generate-resume-button"
          className="btn-primary flex items-center space-x-2"
        >
          <Plus size={18} />
          <span>Generate Resume</span>
        </button>
      </div>

      {showForm && (
        <div className="card mb-6">
          <h2 className="text-xl font-semibold text-secondary-900 mb-4">Generate New Resume</h2>
          <form onSubmit={handleGenerate} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">
                Select Job Description (Optional)
              </label>
              <select
                value={selectedJob}
                onChange={(e) => setSelectedJob(e.target.value)}
                className="input-field"
              >
                <option value="">-- None (General Resume) --</option>
                {jobs.map((job) => (
                  <option key={job.id} value={job.id}>
                    {job.title} at {job.company}
                  </option>
                ))}
              </select>
              {jobs.length === 0 && (
                <p className="text-sm text-secondary-600 mt-2">
                  No job descriptions available. Add one first for a tailored resume.
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">
                Select Template
              </label>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {templates.map((template) => (
                  <div
                    key={template.id}
                    onClick={() => setSelectedTemplate(template.id)}
                    className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                      selectedTemplate === template.id
                        ? 'border-primary-600 bg-primary-50'
                        : 'border-secondary-200 hover:border-secondary-300'
                    }`}
                  >
                    <h3 className="font-semibold text-secondary-900 mb-1">{template.name}</h3>
                    <p className="text-sm text-secondary-600">{template.description}</p>
                  </div>
                ))}
              </div>
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
                disabled={generating}
                className="btn-primary disabled:opacity-50"
              >
                {generating ? 'Generating...' : 'Generate Resume'}
              </button>
            </div>
          </form>
        </div>
      )}

      {resumes.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {resumes.map((resume) => (
            <div key={resume.id} className="card hover:shadow-lg transition-shadow">
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                    <FileText className="text-primary-600" size={24} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-secondary-900">
                      Resume {new Date(resume.created_at).toLocaleDateString()}
                    </h3>
                    <p className="text-sm text-secondary-600">Template: {resume.template_id}</p>
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(resume.id)}
                  className="text-red-600 hover:text-red-700 transition-colors"
                >
                  <Trash2 size={18} />
                </button>
              </div>

              {resume.ats_score && (
                <div className="mb-4">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-secondary-600">ATS Score</span>
                    <span className="font-semibold text-secondary-900">{resume.ats_score}%</span>
                  </div>
                  <div className="w-full bg-secondary-200 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full transition-all"
                      style={{ width: `${resume.ats_score}%` }}
                    />
                  </div>
                </div>
              )}

              <div className="flex space-x-2">
                <button className="flex-1 btn-secondary text-sm py-2">
                  <Eye size={16} className="inline mr-1" />
                  Preview
                </button>
                <button className="flex-1 btn-primary text-sm py-2">
                  <Download size={16} className="inline mr-1" />
                  Download
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card text-center text-secondary-600 py-12">
          <FileText size={48} className="mx-auto mb-4 text-secondary-400" />
          <p className="text-lg mb-2">No resumes yet</p>
          <p className="text-sm">Click "Generate Resume" to create your first resume</p>
        </div>
      )}
    </div>
  );
};

export default Resumes;
