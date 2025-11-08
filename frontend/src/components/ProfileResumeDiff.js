import React from 'react';
import { ArrowRight, Zap, AlertCircle } from 'lucide-react';

/**
 * ProfileResumeDiff Component
 * Shows differences between profile data and AI-generated resume
 */
const ProfileResumeDiff = ({ comparisonData }) => {
  if (!comparisonData) {
    return (
      <div className="text-center py-8 text-gray-600">
        <p>Loading comparison...</p>
      </div>
    );
  }

  const { profile_data, resume_data, differences, resume_info } = comparisonData;

  // Helper to normalize arrays for comparison
  const normalizeArray = (arr) => {
    if (!arr) return [];
    return arr.map(item => {
      if (typeof item === 'string') return item.toLowerCase().trim();
      if (typeof item === 'object' && item.name) return item.name.toLowerCase().trim();
      if (typeof item === 'object' && item.skill) return item.skill.toLowerCase().trim();
      return '';
    }).filter(Boolean);
  };

  // Render summary comparison
  const renderSummaryComparison = () => {
    return (
      <div className="bg-white border rounded-lg p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Zap className="mr-2 text-yellow-500" size={20} />
          Professional Summary (AI-Generated)
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Profile */}
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Profile Data</h4>
            <p className="text-sm text-gray-600 italic">
              Your profile doesn't include a summary. The AI generated one based on your experience and skills.
            </p>
          </div>
          
          {/* Resume */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h4 className="text-sm font-medium text-green-700 mb-2 flex items-center">
              AI-Generated Summary
              <span className="ml-2 text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">NEW</span>
            </h4>
            <p className="text-sm text-gray-700 leading-relaxed">
              {resume_data?.summary || 'No summary generated'}
            </p>
          </div>
        </div>
        <div className="mt-3 bg-blue-50 border border-blue-200 rounded-lg p-3">
          <p className="text-xs text-blue-800">
            <strong>AI Enhancement:</strong> Created a compelling professional summary that highlights your key achievements, 
            skills, and experience to grab recruiters' attention.
          </p>
        </div>
      </div>
    );
  };

  // Render experience comparison
  const renderExperienceComparison = () => {
    if (!differences?.experience_changes || differences.experience_changes.length === 0) {
      return null;
    }

    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <Zap className="mr-2 text-yellow-500" size={20} />
          Experience - AI Optimizations
        </h3>
        
        {differences.experience_changes.map((change, idx) => {
          const hasChanges = change.profile_bullets && change.resume_bullets && 
                            normalizeArray(change.profile_bullets).join('') !== normalizeArray(change.resume_bullets).join('');
          
          if (!hasChanges) return null;
          
          return (
            <div key={idx} className="bg-white border rounded-lg shadow-sm overflow-hidden">
              <div className="bg-gray-100 px-4 py-3 border-b">
                <h4 className="font-semibold text-gray-900">{change.title}</h4>
                <p className="text-sm text-gray-600">{change.company}</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-0 divide-x">
                {/* Profile bullets */}
                <div className="p-4">
                  <h5 className="text-sm font-medium text-gray-700 mb-3 flex items-center">
                    Original (Profile)
                  </h5>
                  <ul className="space-y-2">
                    {(change.profile_bullets || []).map((bullet, bidx) => (
                      <li key={bidx} className="text-sm text-gray-700 flex items-start">
                        <span className="text-gray-400 mr-2">•</span>
                        <span>{bullet}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                
                {/* Resume bullets (optimized) */}
                <div className="p-4 bg-green-50">
                  <h5 className="text-sm font-medium text-green-700 mb-3 flex items-center">
                    AI-Optimized (Resume)
                    <ArrowRight size={16} className="ml-2 text-green-600" />
                  </h5>
                  <ul className="space-y-2">
                    {(change.resume_bullets || []).map((bullet, bidx) => (
                      <li key={bidx} className="text-sm text-gray-800 flex items-start font-medium">
                        <span className="text-green-600 mr-2">•</span>
                        <span>{bullet}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
              
              <div className="bg-blue-50 border-t border-blue-200 px-4 py-3">
                <p className="text-xs text-blue-800">
                  <strong>Improvements:</strong> Added powerful action verbs, quantifiable metrics, 
                  and ATS-friendly keywords while maintaining accuracy.
                </p>
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  // Render skills comparison
  const renderSkillsComparison = () => {
    if (!differences?.skills_changes) return null;

    const { profile_technical, resume_technical, profile_soft, resume_soft } = differences.skills_changes;
    
    const techAdded = normalizeArray(resume_technical).filter(
      skill => !normalizeArray(profile_technical).includes(skill)
    );
    const techRemoved = normalizeArray(profile_technical).filter(
      skill => !normalizeArray(resume_technical).includes(skill)
    );
    const techReordered = normalizeArray(profile_technical).join(',') !== normalizeArray(resume_technical).join(',');

    const hasSkillChanges = techAdded.length > 0 || techRemoved.length > 0 || techReordered;

    if (!hasSkillChanges) {
      return (
        <div className="bg-white border rounded-lg p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-2 flex items-center">
            <Zap className="mr-2 text-yellow-500" size={20} />
            Skills
          </h3>
          <p className="text-sm text-green-700">
            ✓ All your profile skills are retained in the resume (no changes needed)
          </p>
        </div>
      );
    }

    return (
      <div className="bg-white border rounded-lg p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Zap className="mr-2 text-yellow-500" size={20} />
          Skills - AI Optimization
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Profile Skills */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-3">Original (Profile)</h4>
            <div className="space-y-3">
              {profile_technical && profile_technical.length > 0 && (
                <div>
                  <p className="text-xs text-gray-600 mb-2">Technical</p>
                  <div className="flex flex-wrap gap-1">
                    {profile_technical.map((skill, idx) => {
                      const skillName = typeof skill === 'object' ? skill.name || skill.skill : skill;
                      const isRemoved = techRemoved.includes(skillName.toLowerCase().trim());
                      
                      return (
                        <span 
                          key={idx} 
                          className={`px-2 py-1 text-xs rounded ${
                            isRemoved 
                              ? 'bg-red-100 text-red-700 line-through' 
                              : 'bg-gray-100 text-gray-700'
                          }`}
                        >
                          {skillName}
                        </span>
                      );
                    })}
                  </div>
                </div>
              )}
              
              {profile_soft && profile_soft.length > 0 && (
                <div>
                  <p className="text-xs text-gray-600 mb-2">Soft Skills</p>
                  <div className="flex flex-wrap gap-1">
                    {profile_soft.map((skill, idx) => {
                      const skillName = typeof skill === 'object' ? skill.name || skill.skill : skill;
                      return (
                        <span key={idx} className="px-2 py-1 text-xs rounded bg-gray-100 text-gray-700">
                          {skillName}
                        </span>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          </div>
          
          {/* Resume Skills */}
          <div className="bg-green-50 rounded-lg p-4">
            <h4 className="text-sm font-medium text-green-700 mb-3 flex items-center">
              AI-Optimized (Resume)
              <ArrowRight size={16} className="ml-2 text-green-600" />
            </h4>
            <div className="space-y-3">
              {resume_technical && resume_technical.length > 0 && (
                <div>
                  <p className="text-xs text-gray-600 mb-2">Technical</p>
                  <div className="flex flex-wrap gap-1">
                    {resume_technical.map((skill, idx) => {
                      const skillName = typeof skill === 'object' ? skill.name || skill.skill : skill;
                      const isNew = techAdded.includes(skillName.toLowerCase().trim());
                      
                      return (
                        <span 
                          key={idx} 
                          className={`px-2 py-1 text-xs rounded font-medium ${
                            isNew 
                              ? 'bg-green-200 text-green-900 ring-2 ring-green-400' 
                              : 'bg-blue-100 text-blue-700'
                          }`}
                        >
                          {skillName} {isNew && '✨'}
                        </span>
                      );
                    })}
                  </div>
                </div>
              )}
              
              {resume_soft && resume_soft.length > 0 && (
                <div>
                  <p className="text-xs text-gray-600 mb-2">Soft Skills</p>
                  <div className="flex flex-wrap gap-1">
                    {resume_soft.map((skill, idx) => {
                      const skillName = typeof skill === 'object' ? skill.name || skill.skill : skill;
                      return (
                        <span key={idx} className="px-2 py-1 text-xs rounded bg-blue-100 text-blue-700 font-medium">
                          {skillName}
                        </span>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
        
        {(techAdded.length > 0 || techReordered) && (
          <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-3">
            <p className="text-xs text-blue-800">
              <strong>AI Enhancements:</strong>
              {techAdded.length > 0 && ` Added ${techAdded.length} relevant keyword(s) to match job requirements.`}
              {techReordered && ' Reordered skills to prioritize most relevant ones for ATS optimization.'}
            </p>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-2">Profile vs Resume Comparison</h2>
        <p className="text-sm text-gray-700 mb-4">
          See how AI transformed your profile data into an ATS-optimized resume
        </p>
        <div className="flex items-center gap-4">
          <div className="bg-white border border-gray-200 rounded-lg px-4 py-2">
            <span className="text-xs text-gray-600">Resume:</span>
            <span className="ml-2 text-sm font-bold text-gray-900">{resume_info?.name}</span>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg px-4 py-2">
            <span className="text-xs text-gray-600">ATS Score:</span>
            <span className="ml-2 text-lg font-bold text-green-600">
              {resume_info?.ats_score?.overall_score || 0}%
            </span>
          </div>
        </div>
      </div>

      {/* Color legend */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-gray-900 mb-2">Legend:</h3>
        <div className="flex flex-wrap gap-4 text-xs">
          <div className="flex items-center">
            <div className="w-4 h-4 bg-green-50 border border-green-200 rounded mr-2"></div>
            <span className="text-gray-700">AI-Generated / Enhanced</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-green-200 rounded mr-2"></div>
            <span className="text-gray-700">New Addition ✨</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-red-100 rounded mr-2"></div>
            <span className="text-gray-700">Removed / Updated</span>
          </div>
        </div>
      </div>

      {/* Comparisons */}
      {renderSummaryComparison()}
      {renderExperienceComparison()}
      {renderSkillsComparison()}

      {/* Summary of changes */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-green-900 mb-3">🎉 Summary of AI Enhancements</h3>
        <ul className="space-y-2 text-sm text-green-800">
          <li className="flex items-start">
            <span className="mr-2">✓</span>
            <span><strong>Professional Summary:</strong> Created compelling summary highlighting key achievements</span>
          </li>
          <li className="flex items-start">
            <span className="mr-2">✓</span>
            <span><strong>Experience Bullets:</strong> Enhanced with power verbs, metrics, and ATS keywords</span>
          </li>
          <li className="flex items-start">
            <span className="mr-2">✓</span>
            <span><strong>Skills Optimization:</strong> Prioritized and added relevant keywords for job match</span>
          </li>
          <li className="flex items-start">
            <span className="mr-2">✓</span>
            <span><strong>ATS Score:</strong> Achieved {resume_info?.ats_score?.overall_score || 0}% match score</span>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default ProfileResumeDiff;
