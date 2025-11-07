import React, { useState, useEffect } from 'react';
import { interviewAPI, jobAPI } from '../services/api';
import { Plus, MessageSquare, ChevronDown, ChevronUp, FileText, FileDown } from 'lucide-react';
import jsPDF from 'jspdf';
import { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType } from 'docx';
import { saveAs } from 'file-saver';

const InterviewPrep = () => {
  const [groupedData, setGroupedData] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [selectedJob, setSelectedJob] = useState('');
  const [questionCount, setQuestionCount] = useState(25);
  const [generating, setGenerating] = useState(false);
  const [expandedGroups, setExpandedGroups] = useState({});
  const [expandedQuestions, setExpandedQuestions] = useState({});
  const [filterCategory, setFilterCategory] = useState('');
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filterCategory]);

  const fetchData = async () => {
    try {
      const [groupedRes, jobsRes, categoriesRes] = await Promise.all([
        interviewAPI.getQuestionsGrouped({ category: filterCategory || undefined }),
        jobAPI.getJobs(),
        interviewAPI.getCategories()
      ]);
      
      const grouped = groupedRes.data.groups || [];
      setGroupedData(grouped);
      
      const jobsData = jobsRes.data.items || jobsRes.data || [];
      setJobs(jobsData);
      setCategories(categoriesRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
      setGroupedData([]);
      setJobs([]);
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

  const toggleGroup = (jobId) => {
    setExpandedGroups(prev => ({
      ...prev,
      [jobId]: !prev[jobId]
    }));
  };

  const toggleQuestion = (questionId) => {
    setExpandedQuestions(prev => ({
      ...prev,
      [questionId]: !prev[questionId]
    }));
  };

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

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const exportToPDF = async () => {
    setExporting(true);
    try {
      const doc = new jsPDF();
      let yPosition = 20;
      const pageHeight = doc.internal.pageSize.height;
      const margin = 20;
      const lineHeight = 7;

      // Title
      doc.setFontSize(18);
      doc.setFont(undefined, 'bold');
      doc.text('Interview Questions Report', margin, yPosition);
      yPosition += 15;

      // Generate date
      doc.setFontSize(10);
      doc.setFont(undefined, 'normal');
      doc.text(`Generated on: ${new Date().toLocaleString()}`, margin, yPosition);
      yPosition += 10;

      // Iterate through grouped data
      for (const group of groupedData) {
        // Check if we need a new page
        if (yPosition > pageHeight - 40) {
          doc.addPage();
          yPosition = 20;
        }

        // Job header
        doc.setFontSize(14);
        doc.setFont(undefined, 'bold');
        doc.text(`${group.job.title} at ${group.job.company}`, margin, yPosition);
        yPosition += lineHeight;

        doc.setFontSize(10);
        doc.setFont(undefined, 'normal');
        if (group.job.location) {
          doc.text(`Location: ${group.job.location}`, margin, yPosition);
          yPosition += lineHeight;
        }
        doc.text(`Questions Generated: ${group.question_count}`, margin, yPosition);
        yPosition += lineHeight;
        doc.text(`Date: ${formatDate(group.job.created_at)}`, margin, yPosition);
        yPosition += 10;

        // Questions
        group.questions.forEach((question, index) => {
          // Check if we need a new page
          if (yPosition > pageHeight - 60) {
            doc.addPage();
            yPosition = 20;
          }

          // Question number and category
          doc.setFontSize(11);
          doc.setFont(undefined, 'bold');
          doc.text(`Q${index + 1}. [${question.category}] [${question.difficulty}]`, margin, yPosition);
          yPosition += lineHeight;

          // Question text
          doc.setFontSize(10);
          doc.setFont(undefined, 'normal');
          const questionLines = doc.splitTextToSize(question.question, 170);
          doc.text(questionLines, margin, yPosition);
          yPosition += questionLines.length * lineHeight;

          // AI-generated answer
          if (question.ai_generated_answer) {
            yPosition += 3;
            doc.setFont(undefined, 'bold');
            doc.text('AI-Generated STAR Answer:', margin, yPosition);
            yPosition += lineHeight;
            doc.setFont(undefined, 'normal');

            const answer = question.ai_generated_answer;
            if (answer.situation) {
              const situationLines = doc.splitTextToSize(`Situation: ${answer.situation}`, 170);
              doc.text(situationLines, margin, yPosition);
              yPosition += situationLines.length * lineHeight;
            }
            if (answer.task) {
              const taskLines = doc.splitTextToSize(`Task: ${answer.task}`, 170);
              doc.text(taskLines, margin, yPosition);
              yPosition += taskLines.length * lineHeight;
            }
            if (answer.action) {
              const actionLines = doc.splitTextToSize(`Action: ${answer.action}`, 170);
              doc.text(actionLines, margin, yPosition);
              yPosition += actionLines.length * lineHeight;
            }
            if (answer.result) {
              const resultLines = doc.splitTextToSize(`Result: ${answer.result}`, 170);
              doc.text(resultLines, margin, yPosition);
              yPosition += resultLines.length * lineHeight;
            }
          }

          yPosition += 8;
        });

        yPosition += 5;
      }

      doc.save('interview-questions.pdf');
    } catch (error) {
      console.error('Error exporting to PDF:', error);
      alert('Error exporting to PDF. Please try again.');
    } finally {
      setExporting(false);
    }
  };

  const exportToWord = async () => {
    setExporting(true);
    try {
      const sections = [];

      // Title section
      sections.push(
        new Paragraph({
          text: 'Interview Questions Report',
          heading: HeadingLevel.HEADING_1,
          alignment: AlignmentType.CENTER,
          spacing: { after: 200 }
        })
      );

      sections.push(
        new Paragraph({
          text: `Generated on: ${new Date().toLocaleString()}`,
          spacing: { after: 400 }
        })
      );

      // Iterate through grouped data
      for (const group of groupedData) {
        // Job header
        sections.push(
          new Paragraph({
            text: `${group.job.title} at ${group.job.company}`,
            heading: HeadingLevel.HEADING_2,
            spacing: { before: 400, after: 200 }
          })
        );

        if (group.job.location) {
          sections.push(
            new Paragraph({
              text: `Location: ${group.job.location}`,
              spacing: { after: 100 }
            })
          );
        }

        sections.push(
          new Paragraph({
            text: `Questions Generated: ${group.question_count}`,
            spacing: { after: 100 }
          })
        );

        sections.push(
          new Paragraph({
            text: `Date: ${formatDate(group.job.created_at)}`,
            spacing: { after: 300 }
          })
        );

        // Questions
        group.questions.forEach((question, index) => {
          // Question
          sections.push(
            new Paragraph({
              children: [
                new TextRun({
                  text: `Q${index + 1}. `,
                  bold: true
                }),
                new TextRun({
                  text: `[${question.category}] [${question.difficulty}]`,
                  bold: true,
                  italics: true
                })
              ],
              spacing: { before: 200, after: 100 }
            })
          );

          sections.push(
            new Paragraph({
              text: question.question,
              spacing: { after: 200 }
            })
          );

          // AI-generated answer
          if (question.ai_generated_answer) {
            sections.push(
              new Paragraph({
                text: 'AI-Generated STAR Answer:',
                bold: true,
                spacing: { after: 100 }
              })
            );

            const answer = question.ai_generated_answer;
            if (answer.situation) {
              sections.push(
                new Paragraph({
                  children: [
                    new TextRun({
                      text: 'Situation: ',
                      bold: true
                    }),
                    new TextRun({
                      text: answer.situation
                    })
                  ],
                  spacing: { after: 100 }
                })
              );
            }

            if (answer.task) {
              sections.push(
                new Paragraph({
                  children: [
                    new TextRun({
                      text: 'Task: ',
                      bold: true
                    }),
                    new TextRun({
                      text: answer.task
                    })
                  ],
                  spacing: { after: 100 }
                })
              );
            }

            if (answer.action) {
              sections.push(
                new Paragraph({
                  children: [
                    new TextRun({
                      text: 'Action: ',
                      bold: true
                    }),
                    new TextRun({
                      text: answer.action
                    })
                  ],
                  spacing: { after: 100 }
                })
              );
            }

            if (answer.result) {
              sections.push(
                new Paragraph({
                  children: [
                    new TextRun({
                      text: 'Result: ',
                      bold: true
                    }),
                    new TextRun({
                      text: answer.result
                    })
                  ],
                  spacing: { after: 200 }
                })
              );
            }
          }
        });
      }

      const doc = new Document({
        sections: [{
          properties: {},
          children: sections
        }]
      });

      const blob = await Packer.toBlob(doc);
      saveAs(blob, 'interview-questions.docx');
    } catch (error) {
      console.error('Error exporting to Word:', error);
      alert('Error exporting to Word. Please try again.');
    } finally {
      setExporting(false);
    }
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
        <div className="flex space-x-3">
          {groupedData.length > 0 && (
            <>
              <button
                onClick={exportToPDF}
                disabled={exporting}
                data-testid="export-pdf-button"
                className="btn-secondary flex items-center space-x-2"
              >
                <FileText size={18} />
                <span>{exporting ? 'Exporting...' : 'Export PDF'}</span>
              </button>
              <button
                onClick={exportToWord}
                disabled={exporting}
                data-testid="export-word-button"
                className="btn-secondary flex items-center space-x-2"
              >
                <FileDown size={18} />
                <span>{exporting ? 'Exporting...' : 'Export Word'}</span>
              </button>
            </>
          )}
          <button
            onClick={() => setShowForm(!showForm)}
            data-testid="generate-questions-button"
            className="btn-primary flex items-center space-x-2"
          >
            <Plus size={18} />
            <span>Generate Questions</span>
          </button>
        </div>
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

      {groupedData.length > 0 && (
        <div className="mb-6 card">
          <label className="block text-sm font-medium text-secondary-700 mb-2">
            Filter by Category
          </label>
          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="input-field"
            data-testid="category-filter"
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

      {groupedData.length > 0 ? (
        <div className="space-y-6">
          {groupedData.map((group) => (
            <div key={group.job.id} className="card" data-testid={`job-group-${group.job.id}`}>
              {/* Job Header - Expandable */}
              <div
                className="flex justify-between items-start cursor-pointer hover:bg-secondary-50 -m-6 p-6 rounded-lg transition-colors"
                onClick={() => toggleGroup(group.job.id)}
              >
                <div className="flex-1">
                  <h2 className="text-2xl font-bold text-secondary-900 mb-2">
                    {group.job.title} at {group.job.company}
                  </h2>
                  <div className="flex flex-wrap gap-3 text-sm text-secondary-600">
                    {group.job.location && (
                      <span>📍 {group.job.location}</span>
                    )}
                    <span>📝 {group.question_count} questions</span>
                    <span>🕒 Generated: {formatDate(group.job.created_at)}</span>
                  </div>
                </div>
                <div className="ml-4">
                  {expandedGroups[group.job.id] ? (
                    <ChevronUp className="text-secondary-400" size={24} />
                  ) : (
                    <ChevronDown className="text-secondary-400" size={24} />
                  )}
                </div>
              </div>

              {/* Questions List */}
              {expandedGroups[group.job.id] && (
                <div className="mt-6 space-y-4 border-t pt-6">
                  {group.questions.map((question, index) => (
                    <div
                      key={question.id}
                      className="bg-secondary-50 rounded-lg p-4 hover:shadow-md transition-shadow"
                      data-testid={`question-${question.id}`}
                    >
                      <div
                        className="flex justify-between items-start cursor-pointer"
                        onClick={() => toggleQuestion(question.id)}
                      >
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <span className="text-lg font-semibold text-secondary-900">
                              Q{index + 1}
                            </span>
                            <span className={`px-2 py-1 text-xs rounded-full ${getCategoryBadgeColor(question.category)}`}>
                              {question.category}
                            </span>
                            <span className="px-2 py-1 text-xs bg-secondary-200 text-secondary-700 rounded-full">
                              {question.difficulty}
                            </span>
                          </div>
                          <p className="text-secondary-900 font-medium">{question.question}</p>
                        </div>
                        <div className="ml-4">
                          {expandedQuestions[question.id] ? (
                            <ChevronUp className="text-secondary-400" size={20} />
                          ) : (
                            <ChevronDown className="text-secondary-400" size={20} />
                          )}
                        </div>
                      </div>

                      {expandedQuestions[question.id] && question.ai_generated_answer && (
                        <div className="mt-4 p-4 bg-white rounded-lg border border-secondary-200">
                          <h4 className="font-semibold text-secondary-900 mb-3">
                            AI-Generated STAR Answer:
                          </h4>
                          <div className="space-y-3 text-sm text-secondary-700">
                            {question.ai_generated_answer.situation && (
                              <div>
                                <strong className="text-secondary-900">Situation:</strong>{' '}
                                {question.ai_generated_answer.situation}
                              </div>
                            )}
                            {question.ai_generated_answer.task && (
                              <div>
                                <strong className="text-secondary-900">Task:</strong>{' '}
                                {question.ai_generated_answer.task}
                              </div>
                            )}
                            {question.ai_generated_answer.action && (
                              <div>
                                <strong className="text-secondary-900">Action:</strong>{' '}
                                {question.ai_generated_answer.action}
                              </div>
                            )}
                            {question.ai_generated_answer.result && (
                              <div>
                                <strong className="text-secondary-900">Result:</strong>{' '}
                                {question.ai_generated_answer.result}
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
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
