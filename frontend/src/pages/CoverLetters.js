import React, { useState, useEffect } from 'react';
import { coverLetterAPI, jobAPI } from '../services/api';
import { FileText, Download, Trash2, Plus, Edit2, Eye } from 'lucide-react';
import jsPDF from 'jspdf';

const CoverLetters = () => {
  const [coverLetters, setCoverLetters] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [selectedJob, setSelectedJob] = useState('');
  const [selectedTone, setSelectedTone] = useState('professional');
  const [viewingLetter, setViewingLetter] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [lettersRes, jobsRes] = await Promise.all([
        coverLetterAPI.getAll(),
        jobAPI.getJobs()
      ]);
      
      setCoverLetters(lettersRes.data.items || lettersRes.data || []);
      setJobs(jobsRes.data.items || jobsRes.data || []);
    } catch (error) {
      console.error('Error fetching data:', error);
      alert('Failed to load cover letters');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!selectedJob) {
      alert('Please select a job description');
      return;
    }

    try {
      setGenerating(true);
      await coverLetterAPI.generate({
        job_description_id: selectedJob,
        tone: selectedTone,
        template: 'standard'
      });
      
      setShowGenerateModal(false);
      setSelectedJob('');
      setSelectedTone('professional');
      await fetchData();
      alert('Cover letter generated successfully!');
    } catch (error) {
      console.error('Error generating cover letter:', error);
      alert('Failed to generate cover letter. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this cover letter?')) {
      return;
    }

    try {
      await coverLetterAPI.delete(id);
      await fetchData();
      alert('Cover letter deleted successfully');
    } catch (error) {
      console.error('Error deleting cover letter:', error);
      alert('Failed to delete cover letter');
    }
  };

  const handleView = (letter) => {
    setViewingLetter(letter);
    setShowViewModal(true);
  };

  const handleDownloadPDF = (letter) => {
    try {
      const doc = new jsPDF();
      const content = letter.content;
      const job = jobs.find(j => j.id === letter.job_description_id);
      
      // Set up document
      doc.setFontSize(12);
      const pageWidth = doc.internal.pageSize.width;
      const margin = 20;
      const maxWidth = pageWidth - 2 * margin;
      
      let yPos = 20;
      
      // Date
      doc.text(new Date().toLocaleDateString(), margin, yPos);
      yPos += 15;
      
      // Company info
      if (job) {
        doc.text(job.company, margin, yPos);
        yPos += 7;
        if (job.location) {
          doc.text(job.location, margin, yPos);
          yPos += 7;
        }
        yPos += 10;
      }
      
      // Salutation
      doc.text('Dear Hiring Manager,', margin, yPos);
      yPos += 15;
      
      // Opening
      if (content.opening) {
        const openingLines = doc.splitTextToSize(content.opening, maxWidth);
        doc.text(openingLines, margin, yPos);
        yPos += openingLines.length * 7 + 10;
      }
      
      // Body paragraphs
      if (content.body && Array.isArray(content.body)) {
        content.body.forEach((paragraph) => {
          if (yPos > 250) {
            doc.addPage();
            yPos = 20;
          }
          const lines = doc.splitTextToSize(paragraph, maxWidth);
          doc.text(lines, margin, yPos);
          yPos += lines.length * 7 + 10;
        });
      }
      
      // Closing
      if (content.closing) {
        if (yPos > 240) {
          doc.addPage();
          yPos = 20;
        }
        const closingLines = doc.splitTextToSize(content.closing, maxWidth);
        doc.text(closingLines, margin, yPos);
        yPos += closingLines.length * 7 + 15;
      }
      
      // Signature
      doc.text('Sincerely,', margin, yPos);
      yPos += 7;
      doc.text('[Your Name]', margin, yPos);
      
      // Save PDF
      doc.save(`cover-letter-${job?.company || 'document'}.pdf`);
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Failed to generate PDF');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="inline-block w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="mt-4 text-secondary-600">Loading cover letters...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-secondary-900">Cover Letters</h1>
          <p className="text-secondary-600 mt-2">AI-powered cover letters tailored to each job</p>
        </div>
        <button
          onClick={() => setShowGenerateModal(true)}
          className="btn-primary flex items-center gap-2"
          data-testid="generate-cover-letter-btn"
        >
          <Plus size={20} />
          Generate Cover Letter
        </button>
      </div>

      {/* Cover Letters Grid */}
      {coverLetters.length === 0 ? (
        <div className="text-center py-12 card">
          <FileText className="mx-auto text-secondary-400 mb-4" size={48} />
          <h3 className="text-lg font-semibold text-secondary-900 mb-2">No Cover Letters Yet</h3>
          <p className="text-secondary-600 mb-6">Generate your first AI-powered cover letter</p>
          <button
            onClick={() => setShowGenerateModal(true)}
            className="btn-primary"
          >
            Generate Cover Letter
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {coverLetters.map((letter) => {
            const job = jobs.find(j => j.id === letter.job_description_id);
            return (
              <div key={letter.id} className="card hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="font-semibold text-secondary-900 mb-1">
                      {job?.title || 'Cover Letter'}
                    </h3>
                    <p className="text-sm text-secondary-600">{job?.company || 'Company'}</p>
                    <p className="text-xs text-secondary-500 mt-2">
                      {new Date(letter.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <span className="px-3 py-1 text-xs font-medium bg-primary-100 text-primary-700 rounded-full">
                    {letter.tone}
                  </span>
                </div>
                
                <div className="flex gap-2 mt-4">
                  <button
                    onClick={() => handleView(letter)}
                    className="flex-1 btn-secondary text-sm flex items-center justify-center gap-2"
                    data-testid={`view-letter-${letter.id}`}
                  >
                    <Eye size={16} />
                    View
                  </button>
                  <button
                    onClick={() => handleDownloadPDF(letter)}
                    className="flex-1 btn-primary text-sm flex items-center justify-center gap-2"
                    data-testid={`download-letter-${letter.id}`}
                  >
                    <Download size={16} />
                    PDF
                  </button>
                  <button
                    onClick={() => handleDelete(letter.id)}
                    className="btn-secondary text-red-600 hover:bg-red-50 text-sm p-2"
                    data-testid={`delete-letter-${letter.id}`}
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Generate Modal */}
      {showGenerateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h2 className="text-2xl font-bold text-secondary-900 mb-4">Generate Cover Letter</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Select Job Description *
                </label>
                <select
                  value={selectedJob}
                  onChange={(e) => setSelectedJob(e.target.value)}
                  className="input"
                  data-testid="job-select"
                >
                  <option value="">-- Select a job --</option>
                  {jobs.map((job) => (
                    <option key={job.id} value={job.id}>
                      {job.title} at {job.company}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Tone
                </label>
                <select
                  value={selectedTone}
                  onChange={(e) => setSelectedTone(e.target.value)}
                  className="input"
                  data-testid="tone-select"
                >
                  <option value="professional">Professional</option>
                  <option value="enthusiastic">Enthusiastic</option>
                  <option value="formal">Formal</option>
                </select>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowGenerateModal(false)}
                className="flex-1 btn-secondary"
                disabled={generating}
              >
                Cancel
              </button>
              <button
                onClick={handleGenerate}
                className="flex-1 btn-primary"
                disabled={generating || !selectedJob}
                data-testid="generate-submit-btn"
              >
                {generating ? 'Generating...' : 'Generate'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* View Modal */}
      {showViewModal && viewingLetter && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto p-6">
            <div className="flex justify-between items-start mb-4">
              <h2 className="text-2xl font-bold text-secondary-900">Cover Letter</h2>
              <button
                onClick={() => setShowViewModal(false)}
                className="text-secondary-400 hover:text-secondary-600"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-4 text-secondary-800">
              <div className="border-b pb-4">
                <p className="font-medium">
                  {jobs.find(j => j.id === viewingLetter.job_description_id)?.title || 'Position'}
                </p>
                <p className="text-sm text-secondary-600">
                  {jobs.find(j => j.id === viewingLetter.job_description_id)?.company || 'Company'}
                </p>
              </div>

              <div className="whitespace-pre-wrap">
                <p className="mb-4">{new Date().toLocaleDateString()}</p>
                <p className="mb-4">Dear Hiring Manager,</p>
                
                {viewingLetter.content.opening && (
                  <p className="mb-4">{viewingLetter.content.opening}</p>
                )}
                
                {viewingLetter.content.body && Array.isArray(viewingLetter.content.body) && (
                  viewingLetter.content.body.map((paragraph, idx) => (
                    <p key={idx} className="mb-4">{paragraph}</p>
                  ))
                )}
                
                {viewingLetter.content.closing && (
                  <p className="mb-4">{viewingLetter.content.closing}</p>
                )}
                
                <p className="mb-2">Sincerely,</p>
                <p>[Your Name]</p>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => handleDownloadPDF(viewingLetter)}
                className="btn-primary flex items-center gap-2"
              >
                <Download size={20} />
                Download PDF
              </button>
              <button
                onClick={() => setShowViewModal(false)}
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

export default CoverLetters;
