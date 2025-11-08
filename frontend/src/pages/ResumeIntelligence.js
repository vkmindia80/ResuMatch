import React, { useState, useEffect } from 'react';
import { resumeAPI } from '../services/api';
import { TrendingUp, GitCompare, Lightbulb, Target, Award, BarChart3, ChevronRight, FileText } from 'lucide-react';
import ResumeDiffViewer from '../components/ResumeDiffViewer';
import ProfileResumeDiff from '../components/ProfileResumeDiff';

const ResumeIntelligence = () => {
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedResume, setSelectedResume] = useState(null);
  const [activeTab, setActiveTab] = useState('performance');
  const [performanceData, setPerformanceData] = useState(null);
  const [abSuggestions, setABSuggestions] = useState(null);
  const [industryOptimization, setIndustryOptimization] = useState(null);
  const [selectedIndustry, setSelectedIndustry] = useState('tech');
  const [compareResumeA, setCompareResumeA] = useState('');
  const [compareResumeB, setCompareResumeB] = useState('');
  const [comparisonData, setComparisonData] = useState(null);
  const [profileComparisonData, setProfileComparisonData] = useState(null);
  const [selectedProfileCompareResume, setSelectedProfileCompareResume] = useState('');

  useEffect(() => {
    fetchResumes();
  }, []);

  useEffect(() => {
    if (selectedResume) {
      loadIntelligenceData();
    }
  }, [selectedResume, activeTab]);

  const fetchResumes = async () => {
    try {
      setLoading(true);
      const response = await resumeAPI.getResumes();
      const resumesData = response.data.items || response.data || [];
      setResumes(resumesData);
      if (resumesData.length > 0) {
        setSelectedResume(resumesData[0].id);
      }
    } catch (error) {
      console.error('Error fetching resumes:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadIntelligenceData = async () => {
    if (!selectedResume) return;

    try {
      if (activeTab === 'performance') {
        const response = await resumeAPI.getPerformanceAnalysis(selectedResume);
        setPerformanceData(response.data);
      } else if (activeTab === 'ab-testing') {
        const response = await resumeAPI.getABSuggestions(selectedResume);
        setABSuggestions(response.data);
      } else if (activeTab === 'industry') {
        const response = await resumeAPI.getIndustryOptimization(selectedResume, selectedIndustry);
        setIndustryOptimization(response.data);
      }
    } catch (error) {
      console.error('Error loading intelligence data:', error);
    }
  };

  const handleCompare = async () => {
    if (!compareResumeA || !compareResumeB) {
      alert('Please select two resumes to compare');
      return;
    }

    try {
      const response = await resumeAPI.compareResumes(compareResumeA, compareResumeB);
      setComparisonData(response.data);
    } catch (error) {
      console.error('Error comparing resumes:', error);
      alert('Failed to compare resumes');
    }
  };

  const handleProfileComparison = async () => {
    if (!selectedProfileCompareResume) {
      alert('Please select a resume to compare with your profile');
      return;
    }

    try {
      const response = await resumeAPI.compareWithProfile(selectedProfileCompareResume);
      setProfileComparisonData(response.data);
    } catch (error) {
      console.error('Error comparing with profile:', error);
      alert('Failed to compare with profile');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="inline-block w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="mt-4 text-secondary-600">Loading resume intelligence...</p>
        </div>
      </div>
    );
  }

  if (resumes.length === 0) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="card text-center py-12">
          <Award className="mx-auto text-secondary-400 mb-4" size={48} />
          <h3 className="text-lg font-semibold text-secondary-900 mb-2">No Resumes Yet</h3>
          <p className="text-secondary-600 mb-6">Generate some resumes first to access intelligence features</p>
          <a href="/resumes" className="btn-primary inline-block">
            Go to Resumes
          </a>
        </div>
      </div>
    );
  }

  const selectedResumeData = resumes.find(r => r.id === selectedResume);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-secondary-900">Resume Intelligence</h1>
        <p className="text-secondary-600 mt-2">Advanced analytics and optimization recommendations</p>
      </div>

      {/* Resume Selection */}
      <div className="card mb-6">
        <label className="block text-sm font-medium text-secondary-700 mb-2">
          Select Resume to Analyze
        </label>
        <select
          value={selectedResume}
          onChange={(e) => setSelectedResume(e.target.value)}
          className="input max-w-md"
        >
          {resumes.map((resume) => (
            <option key={resume.id} value={resume.id}>
              {resume.name || `Resume - ${new Date(resume.generated_at).toLocaleDateString()}`} 
              (Score: {resume.ats_score?.overall_score || 0}%)
            </option>
          ))}
        </select>
      </div>

      {/* Tabs */}
      <div className="mb-6">
        <div className="flex gap-2 border-b border-secondary-200">
          <button
            onClick={() => setActiveTab('performance')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors ${
              activeTab === 'performance'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-secondary-600 hover:text-secondary-900'
            }`}
          >
            <TrendingUp className="inline mr-2" size={18} />
            Performance
          </button>
          <button
            onClick={() => setActiveTab('ab-testing')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors ${
              activeTab === 'ab-testing'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-secondary-600 hover:text-secondary-900'
            }`}
          >
            <Lightbulb className="inline mr-2" size={18} />
            A/B Testing
          </button>
          <button
            onClick={() => setActiveTab('compare')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors ${
              activeTab === 'compare'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-secondary-600 hover:text-secondary-900'
            }`}
          >
            <GitCompare className="inline mr-2" size={18} />
            Compare
          </button>
          <button
            onClick={() => setActiveTab('industry')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors ${
              activeTab === 'industry'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-secondary-600 hover:text-secondary-900'
            }`}
          >
            <Target className="inline mr-2" size={18} />
            Industry
          </button>
          <button
            onClick={() => setActiveTab('profile-compare')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors ${
              activeTab === 'profile-compare'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-secondary-600 hover:text-secondary-900'
            }`}
          >
            <FileText className="inline mr-2" size={18} />
            Profile vs Resume
          </button>
        </div>
      </div>

      {/* Performance Tab */}
      {activeTab === 'performance' && performanceData && (
        <div className="space-y-6">
          {/* Score Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="card">
              <p className="text-sm text-secondary-600 mb-1">Current Score</p>
              <p className="text-3xl font-bold text-primary-600">{performanceData.current_score}%</p>
              <p className="text-xs text-secondary-500 mt-1">
                {performanceData.performance_level}
              </p>
            </div>
            <div className="card">
              <p className="text-sm text-secondary-600 mb-1">Your Average</p>
              <p className="text-3xl font-bold text-secondary-900">{performanceData.average_score}%</p>
              <p className="text-xs text-secondary-500 mt-1">
                {performanceData.better_than_average ? '✓ Above average' : '↓ Below average'}
              </p>
            </div>
            <div className="card">
              <p className="text-sm text-secondary-600 mb-1">Your Best</p>
              <p className="text-3xl font-bold text-green-600">{performanceData.best_score}%</p>
              <p className="text-xs text-secondary-500 mt-1">
                Top score achieved
              </p>
            </div>
            <div className="card">
              <p className="text-sm text-secondary-600 mb-1">Percentile</p>
              <p className="text-3xl font-bold text-purple-600">{performanceData.percentile}th</p>
              <p className="text-xs text-secondary-500 mt-1">
                Among your resumes
              </p>
            </div>
          </div>

          {/* Improvement Potential */}
          {performanceData.improvement_potential > 0 && (
            <div className="card bg-blue-50 border-blue-200">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-blue-100 rounded-lg">
                  <TrendingUp className="text-blue-600" size={24} />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-secondary-900 mb-2">Improvement Potential</h3>
                  <p className="text-secondary-700">
                    You can potentially improve this resume by <span className="font-bold text-blue-600">{performanceData.improvement_potential}%</span> to match your best score.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* A/B Testing Tab */}
      {activeTab === 'ab-testing' && abSuggestions && (
        <div className="space-y-6">
          <div className="card bg-primary-50 border-primary-200">
            <h3 className="font-semibold text-secondary-900 mb-2">What is A/B Testing?</h3>
            <p className="text-secondary-700">
              Test different versions of your resume to see what performs better. These suggestions help you create variations to compare.
            </p>
          </div>

          {abSuggestions.suggestions?.map((suggestion, idx) => (
            <div key={idx} className="card">
              <div className="flex items-start gap-4 mb-4">
                <div className="p-2 bg-primary-100 rounded">
                  <Lightbulb className="text-primary-600" size={20} />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-secondary-900">{suggestion.test_name}</h3>
                  <p className="text-sm text-secondary-600">Category: {suggestion.category}</p>
                </div>
                <span className="px-3 py-1 text-xs font-medium bg-green-100 text-green-700 rounded-full">
                  {suggestion.expected_impact}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div className="border border-secondary-200 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded">Variant A</span>
                    <span className="text-sm font-medium text-secondary-900">{suggestion.variant_a.type}</span>
                  </div>
                  <p className="text-sm text-secondary-600 mb-2">{suggestion.variant_a.description}</p>
                  <div className="bg-secondary-50 p-3 rounded text-sm text-secondary-700 italic">
                    {suggestion.variant_a.example}
                  </div>
                </div>

                <div className="border border-secondary-200 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-700 rounded">Variant B</span>
                    <span className="text-sm font-medium text-secondary-900">{suggestion.variant_b.type}</span>
                  </div>
                  <p className="text-sm text-secondary-600 mb-2">{suggestion.variant_b.description}</p>
                  <div className="bg-secondary-50 p-3 rounded text-sm text-secondary-700 italic">
                    {suggestion.variant_b.example}
                  </div>
                </div>
              </div>

              <div className="bg-yellow-50 p-3 rounded">
                <p className="text-sm text-secondary-700">
                  <span className="font-medium">Why test this:</span> {suggestion.why_test}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Compare Tab */}
      {activeTab === 'compare' && (
        <div className="space-y-6">
          <div className="card">
            <h3 className="font-semibold text-secondary-900 mb-4">Compare Two Resumes</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">Resume A</label>
                <select
                  value={compareResumeA}
                  onChange={(e) => setCompareResumeA(e.target.value)}
                  className="input"
                >
                  <option value="">-- Select resume --</option>
                  {resumes.map((resume) => (
                    <option key={resume.id} value={resume.id}>
                      {resume.name || `Resume - ${new Date(resume.generated_at).toLocaleDateString()}`} ({resume.ats_score?.overall_score || 0}%)
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">Resume B</label>
                <select
                  value={compareResumeB}
                  onChange={(e) => setCompareResumeB(e.target.value)}
                  className="input"
                >
                  <option value="">-- Select resume --</option>
                  {resumes.map((resume) => (
                    <option key={resume.id} value={resume.id}>
                      {resume.name || `Resume - ${new Date(resume.generated_at).toLocaleDateString()}`} ({resume.ats_score?.overall_score || 0}%)
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <button
              onClick={handleCompare}
              className="btn-primary"
              disabled={!compareResumeA || !compareResumeB}
            >
              Compare Resumes
            </button>
          </div>

          {comparisonData && (
            <div className="space-y-6">
              {/* Winner */}
              <div className="card bg-green-50 border-green-200">
                <h3 className="font-semibold text-secondary-900 mb-2">Overall Winner</h3>
                <p className="text-2xl font-bold text-green-600 mb-2">
                  {comparisonData.overall_winner === 'resume_a' ? 'Resume A' : comparisonData.overall_winner === 'resume_b' ? 'Resume B' : 'Tie'}
                </p>
                <p className="text-secondary-700">Score difference: {comparisonData.score_difference}%</p>
                <p className="text-secondary-600 mt-2">{comparisonData.recommendation}</p>
              </div>

              {/* Component Comparison */}
              <div className="card">
                <h3 className="font-semibold text-secondary-900 mb-4">Component Breakdown</h3>
                <div className="space-y-3">
                  {Object.entries(comparisonData.component_comparison).map(([key, data]) => (
                    <div key={key} className="border border-secondary-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-secondary-900">
                          {key.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                        </span>
                        <span className={`px-2 py-1 text-xs font-medium rounded ${
                          data.winner === 'a' ? 'bg-blue-100 text-blue-700' :
                          data.winner === 'b' ? 'bg-purple-100 text-purple-700' :
                          'bg-secondary-100 text-secondary-700'
                        }`}>
                          {data.winner === 'tie' ? 'Tie' : `Winner: ${data.winner.toUpperCase()}`}
                        </span>
                      </div>
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <p className="text-secondary-600">Resume A</p>
                          <p className="font-semibold text-blue-600">{data.resume_a}</p>
                        </div>
                        <div className="text-center">
                          <p className="text-secondary-600">Difference</p>
                          <p className={`font-semibold ${
                            data.difference > 0 ? 'text-purple-600' :
                            data.difference < 0 ? 'text-blue-600' :
                            'text-secondary-600'
                          }`}>
                            {data.difference > 0 ? '+' : ''}{data.difference}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-secondary-600">Resume B</p>
                          <p className="font-semibold text-purple-600">{data.resume_b}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Key Differences */}
              {comparisonData.key_differences?.length > 0 && (
                <div className="card">
                  <h3 className="font-semibold text-secondary-900 mb-4">Key Differences</h3>
                  <div className="space-y-3">
                    {comparisonData.key_differences.map((diff, idx) => (
                      <div key={idx} className="flex items-start gap-3">
                        <ChevronRight className="text-primary-600 mt-1 flex-shrink-0" size={20} />
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-medium text-secondary-900">{diff.category}</span>
                            <span className={`px-2 py-1 text-xs font-medium rounded ${
                              diff.impact === 'high' ? 'bg-red-100 text-red-700' :
                              diff.impact === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                              'bg-green-100 text-green-700'
                            }`}>
                              {diff.impact} impact
                            </span>
                          </div>
                          <p className="text-sm text-secondary-600">{diff.description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Industry Tab */}
      {activeTab === 'industry' && (
        <div className="space-y-6">
          <div className="card">
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              Select Target Industry
            </label>
            <select
              value={selectedIndustry}
              onChange={(e) => {
                setSelectedIndustry(e.target.value);
                setIndustryOptimization(null);
              }}
              className="input max-w-md"
            >
              <option value="tech">Technology / Software</option>
              <option value="finance">Finance / Banking</option>
              <option value="healthcare">Healthcare / Medical</option>
              <option value="marketing">Marketing / Advertising</option>
              <option value="general">General / Other</option>
            </select>
            <button
              onClick={loadIntelligenceData}
              className="btn-primary mt-4"
            >
              Get Recommendations
            </button>
          </div>

          {industryOptimization && (
            <div className="space-y-6">
              <div className="card bg-primary-50 border-primary-200">
                <h3 className="font-semibold text-secondary-900 mb-2">
                  Industry: {industryOptimization.target_industry}
                </h3>
                <p className="text-secondary-700">{industryOptimization.recommended_format}</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Key Sections */}
                <div className="card">
                  <h3 className="font-semibold text-secondary-900 mb-3 flex items-center gap-2">
                    <BarChart3 size={20} className="text-primary-600" />
                    Key Sections
                  </h3>
                  <p className="text-sm text-secondary-600 mb-3">Recommended section order:</p>
                  <ol className="space-y-2">
                    {industryOptimization.key_sections.map((section, idx) => (
                      <li key={idx} className="flex items-center gap-2 text-secondary-700">
                        <span className="flex-shrink-0 w-6 h-6 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center text-sm font-medium">
                          {idx + 1}
                        </span>
                        {section}
                      </li>
                    ))}
                  </ol>
                </div>

                {/* Power Words */}
                <div className="card">
                  <h3 className="font-semibold text-secondary-900 mb-3 flex items-center gap-2">
                    <Lightbulb size={20} className="text-primary-600" />
                    Power Words
                  </h3>
                  <p className="text-sm text-secondary-600 mb-3">Use these action verbs:</p>
                  <div className="flex flex-wrap gap-2">
                    {industryOptimization.power_words.map((word, idx) => (
                      <span key={idx} className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-medium">
                        {word}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Emphasis & Avoid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="card bg-green-50 border-green-200">
                  <h3 className="font-semibold text-green-900 mb-2">✓ Emphasize</h3>
                  <p className="text-secondary-700">{industryOptimization.emphasis_areas}</p>
                </div>
                <div className="card bg-red-50 border-red-200">
                  <h3 className="font-semibold text-red-900 mb-2">✗ Avoid</h3>
                  <p className="text-secondary-700">{industryOptimization.things_to_avoid}</p>
                </div>
              </div>

              {/* Tips */}
              <div className="card">
                <h3 className="font-semibold text-secondary-900 mb-3">Industry-Specific Tips</h3>
                <ul className="space-y-2">
                  {industryOptimization.customization_tips.map((tip, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-secondary-700">
                      <ChevronRight className="text-primary-600 mt-1 flex-shrink-0" size={18} />
                      {tip}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ResumeIntelligence;