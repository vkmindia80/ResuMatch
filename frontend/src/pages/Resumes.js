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
  const [showPreview, setShowPreview] = useState(false);
  const [previewResume, setPreviewResume] = useState(null);

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

  const handlePreview = (resume) => {
    console.log('Preview clicked for resume:', resume);
    if (!resume || !resume.content) {
      alert('Resume content is not available. Please try again.');
      return;
    }
    setPreviewResume(resume);
    setShowPreview(true);
  };

  const handleDownload = (resume) => {
    try {
      console.log('Download clicked for resume:', resume);
      
      // Validate resume and content
      if (!resume) {
        throw new Error('Resume data is missing');
      }
      
      if (!resume.content) {
        throw new Error('Resume content is not available');
      }
      
      // Create a simple text version of the resume
      const content = resume.content;
      let resumeText = '';
      
      // Header
      if (content.header) {
        resumeText += `${content.header.full_name || ''}\n`;
        resumeText += `${content.header.email || ''} | ${content.header.phone || ''}\n`;
        resumeText += `${content.header.location || ''}\n`;
        if (content.header.linkedin) resumeText += `LinkedIn: ${content.header.linkedin}\n`;
        resumeText += '\n';
      }
      
      // Summary
      if (content.summary) {
        resumeText += `PROFESSIONAL SUMMARY\n`;
        resumeText += `${content.summary}\n\n`;
      }
      
      // Experience
      if (content.experience && content.experience.length > 0) {
        resumeText += `EXPERIENCE\n`;
        content.experience.forEach(exp => {
          resumeText += `\n${exp.title} - ${exp.company}\n`;
          resumeText += `${exp.location || ''} | ${exp.start_date || ''} - ${exp.is_current ? 'Present' : exp.end_date || ''}\n`;
          if (exp.responsibilities && exp.responsibilities.length > 0) {
            exp.responsibilities.forEach(resp => {
              resumeText += `• ${resp}\n`;
            });
          }
        });
        resumeText += '\n';
      }
      
      // Education
      if (content.education && content.education.length > 0) {
        resumeText += `EDUCATION\n`;
        content.education.forEach(edu => {
          resumeText += `\n${edu.degree || ''} - ${edu.field_of_study || ''}\n`;
          resumeText += `${edu.institution || ''} | ${edu.graduation_year || ''}\n`;
        });
        resumeText += '\n';
      }
      
      // Skills
      if (content.skills) {
        resumeText += `SKILLS\n`;
        if (content.skills.technical && content.skills.technical.length > 0) {
          const technicalSkills = content.skills.technical.map(skill => 
            typeof skill === 'object' ? skill.name || skill.skill || '' : skill
          ).filter(Boolean);
          if (technicalSkills.length > 0) {
            resumeText += `Technical: ${technicalSkills.join(', ')}\n`;
          }
        }
        if (content.skills.soft && content.skills.soft.length > 0) {
          const softSkills = content.skills.soft.map(skill => 
            typeof skill === 'object' ? skill.name || skill.skill || '' : skill
          ).filter(Boolean);
          if (softSkills.length > 0) {
            resumeText += `Soft Skills: ${softSkills.join(', ')}\n`;
          }
        }
      }
      
      // Ensure we have some content to download
      if (!resumeText.trim()) {
        throw new Error('Resume content is empty');
      }
      
      // Create and download file
      const blob = new Blob([resumeText], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `resume_${new Date(resume.created_at).toLocaleDateString().replace(/\//g, '-')}.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading resume:', error);
      alert(`Error downloading resume: ${error.message}`);
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
                      Resume {new Date(resume.created_at).toLocaleString()}
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

              {resume.ats_score && typeof resume.ats_score === 'object' && resume.ats_score.overall_score && (
                <div className="mb-4">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-secondary-600">ATS Score</span>
                    <span className="font-semibold text-secondary-900">{resume.ats_score.overall_score}%</span>
                  </div>
                  <div className="w-full bg-secondary-200 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full transition-all"
                      style={{ width: `${resume.ats_score.overall_score}%` }}
                    />
                  </div>
                </div>
              )}

              <div className="flex space-x-2">
                <button 
                  onClick={() => handlePreview(resume)}
                  className="flex-1 btn-secondary text-sm py-2"
                  data-testid={`preview-resume-${resume.id}`}
                >
                  <Eye size={16} className="inline mr-1" />
                  Preview
                </button>
                <button 
                  onClick={() => handleDownload(resume)}
                  className="flex-1 btn-primary text-sm py-2"
                  data-testid={`download-resume-${resume.id}`}
                >
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

      {/* Preview Modal */}
      {showPreview && previewResume && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto p-6">
            <div className="flex justify-between items-start mb-6">
              <h2 className="text-2xl font-bold text-secondary-900">Resume Preview</h2>
              <button
                onClick={() => setShowPreview(false)}
                className="text-secondary-400 hover:text-secondary-600 text-2xl"
              >
                ✕
              </button>
            </div>

            {!previewResume.content ? (
              <div className="text-center py-8 text-secondary-600">
                <p className="text-lg mb-2">Resume content is not available</p>
                <p className="text-sm">Please try regenerating this resume</p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Header */}
                {previewResume.content.header && (
                <div className="text-center border-b pb-4">
                  <h1 className="text-3xl font-bold text-secondary-900 mb-2">
                    {previewResume.content.header.full_name}
                  </h1>
                  <div className="text-secondary-600 space-x-3">
                    <span>{previewResume.content.header.email}</span>
                    <span>•</span>
                    <span>{previewResume.content.header.phone}</span>
                    <span>•</span>
                    <span>{previewResume.content.header.location}</span>
                  </div>
                  {previewResume.content.header.linkedin && (
                    <div className="text-primary-600 mt-1">{previewResume.content.header.linkedin}</div>
                  )}
                </div>
              )}

              {/* Summary */}
              {previewResume.content.summary && (
                <div>
                  <h3 className="text-lg font-semibold text-secondary-900 mb-2">Professional Summary</h3>
                  <p className="text-secondary-700 leading-relaxed">{previewResume.content.summary}</p>
                </div>
              )}

              {/* Experience */}
              {previewResume.content.experience && previewResume.content.experience.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-secondary-900 mb-3">Experience</h3>
                  {previewResume.content.experience.map((exp, idx) => (
                    <div key={idx} className="mb-4">
                      <div className="flex justify-between items-start mb-1">
                        <div>
                          <h4 className="font-semibold text-secondary-900">{exp.title}</h4>
                          <p className="text-secondary-700">{exp.company}</p>
                        </div>
                        <span className="text-sm text-secondary-600">
                          {exp.start_date} - {exp.is_current ? 'Present' : exp.end_date}
                        </span>
                      </div>
                      {exp.location && (
                        <p className="text-sm text-secondary-600 mb-2">{exp.location}</p>
                      )}
                      {exp.responsibilities && exp.responsibilities.length > 0 && (
                        <ul className="list-disc list-inside text-secondary-700 space-y-1">
                          {exp.responsibilities.slice(0, 5).map((resp, ridx) => (
                            <li key={ridx} className="text-sm">{resp}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Education */}
              {previewResume.content.education && previewResume.content.education.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-secondary-900 mb-3">Education</h3>
                  {previewResume.content.education.map((edu, idx) => (
                    <div key={idx} className="mb-2">
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="font-semibold text-secondary-900">{edu.degree} - {edu.field_of_study}</h4>
                          <p className="text-secondary-700">{edu.institution}</p>
                        </div>
                        <span className="text-sm text-secondary-600">{edu.graduation_year}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Skills */}
              {previewResume.content.skills && (
                <div>
                  <h3 className="text-lg font-semibold text-secondary-900 mb-3">Skills</h3>
                  {previewResume.content.skills.technical && previewResume.content.skills.technical.length > 0 && (
                    <div className="mb-2">
                      <span className="font-medium text-secondary-800">Technical: </span>
                      <span className="text-secondary-700">
                        {previewResume.content.skills.technical.map(skill => 
                          typeof skill === 'object' ? skill.name || skill.skill || '' : skill
                        ).filter(Boolean).join(', ')}
                      </span>
                    </div>
                  )}
                  {previewResume.content.skills.soft && previewResume.content.skills.soft.length > 0 && (
                    <div>
                      <span className="font-medium text-secondary-800">Soft Skills: </span>
                      <span className="text-secondary-700">
                        {previewResume.content.skills.soft.map(skill => 
                          typeof skill === 'object' ? skill.name || skill.skill || '' : skill
                        ).filter(Boolean).join(', ')}
                      </span>
                    </div>
                  )}
                </div>
              )}

              {/* ATS Score */}
              {previewResume.ats_score && previewResume.ats_score.overall_score && (
                <div className="border-t pt-4">
                  <h3 className="text-lg font-semibold text-secondary-900 mb-3">ATS Score</h3>
                  <div className="flex items-center space-x-4">
                    <div className="text-4xl font-bold text-primary-600">
                      {previewResume.ats_score.overall_score}%
                    </div>
                    <div className="flex-1">
                      <div className="w-full bg-secondary-200 rounded-full h-4">
                        <div
                          className="bg-primary-600 h-4 rounded-full transition-all"
                          style={{ width: `${previewResume.ats_score.overall_score}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}
              </div>
            )}

            <div className="flex justify-end space-x-3 mt-6 pt-4 border-t">
              <button
                onClick={() => handleDownload(previewResume)}
                className="btn-primary flex items-center space-x-2"
                disabled={!previewResume.content}
              >
                <Download size={18} />
                <span>Download</span>
              </button>
              <button
                onClick={() => setShowPreview(false)}
                className="btn-secondary"
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

export default Resumes;
