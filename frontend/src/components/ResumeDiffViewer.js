import React from 'react';
import { CheckCircle, XCircle, AlertCircle } from 'lucide-react';

/**
 * ResumeDiffViewer Component
 * Displays two resumes side-by-side with color-coded differences
 */
const ResumeDiffViewer = ({ resumeA, resumeB, title = "Resume Comparison" }) => {
  
  // Helper to normalize text for comparison
  const normalizeText = (text) => {
    if (!text) return '';
    return text.toLowerCase().trim();
  };

  // Check if two arrays have different content
  const arraysAreDifferent = (arr1, arr2) => {
    if (!arr1 || !arr2) return arr1 !== arr2;
    if (arr1.length !== arr2.length) return true;
    
    const norm1 = arr1.map(normalizeText).sort();
    const norm2 = arr2.map(normalizeText).sort();
    
    return norm1.some((item, idx) => item !== norm2[idx]);
  };

  // Get difference type for styling
  const getDiffClass = (valueA, valueB, isArray = false) => {
    if (isArray) {
      return arraysAreDifferent(valueA, valueB) ? 'bg-yellow-50 border-yellow-200' : 'bg-white';
    }
    
    const normA = normalizeText(valueA);
    const normB = normalizeText(valueB);
    
    if (normA !== normB) {
      return 'bg-yellow-50 border-yellow-200';
    }
    return 'bg-white';
  };

  // Render header section
  const renderHeader = (header, label, isLeft = true) => {
    const otherHeader = isLeft ? resumeB?.content?.header : resumeA?.content?.header;
    
    return (
      <div className={`border rounded-lg p-4 ${getDiffClass(header?.full_name, otherHeader?.full_name)}`}>
        <h3 className="text-xl font-bold text-gray-900 mb-2">{header?.full_name || 'N/A'}</h3>
        <div className="text-sm text-gray-600 space-y-1">
          <div className={getDiffClass(header?.email, otherHeader?.email)}>
            <span className="font-medium">Email:</span> {header?.email || 'N/A'}
          </div>
          <div className={getDiffClass(header?.phone, otherHeader?.phone)}>
            <span className="font-medium">Phone:</span> {header?.phone || 'N/A'}
          </div>
          <div className={getDiffClass(header?.location, otherHeader?.location)}>
            <span className="font-medium">Location:</span> {header?.location || 'N/A'}
          </div>
          {header?.linkedin && (
            <div className={getDiffClass(header?.linkedin, otherHeader?.linkedin)}>
              <span className="font-medium">LinkedIn:</span> {header?.linkedin}
            </div>
          )}
        </div>
      </div>
    );
  };

  // Render summary section
  const renderSummary = (summary, label, isLeft = true) => {
    const otherSummary = isLeft ? resumeB?.content?.summary : resumeA?.content?.summary;
    const isDifferent = normalizeText(summary) !== normalizeText(otherSummary);
    
    return (
      <div className={`border rounded-lg p-4 ${isDifferent ? 'bg-yellow-50 border-yellow-200' : 'bg-white'}`}>
        <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
          Professional Summary
          {isDifferent && (
            <AlertCircle size={16} className="ml-2 text-yellow-600" />
          )}
        </h4>
        <p className="text-sm text-gray-700 leading-relaxed">{summary || 'No summary provided'}</p>
      </div>
    );
  };

  // Render experience section
  const renderExperience = (experiences, label, isLeft = true) => {
    const otherExperiences = isLeft ? resumeB?.content?.experience : resumeA?.content?.experience;
    
    return (
      <div className="space-y-4">
        <h4 className="font-semibold text-gray-900">Experience</h4>
        {experiences && experiences.length > 0 ? (
          experiences.map((exp, idx) => {
            const otherExp = otherExperiences?.[idx];
            const bullets = exp.optimized_responsibilities || exp.responsibilities || [];
            const otherBullets = otherExp?.optimized_responsibilities || otherExp?.responsibilities || [];
            const bulletsDifferent = arraysAreDifferent(bullets, otherBullets);
            
            return (
              <div key={idx} className={`border rounded-lg p-4 ${bulletsDifferent ? 'bg-yellow-50 border-yellow-200' : 'bg-white'}`}>
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h5 className="font-semibold text-gray-900">{exp.title}</h5>
                    <p className="text-sm text-gray-700">{exp.company}</p>
                  </div>
                  <span className="text-xs text-gray-600">
                    {exp.start_date} - {exp.is_current ? 'Present' : exp.end_date}
                  </span>
                </div>
                {exp.location && (
                  <p className="text-xs text-gray-600 mb-2">{exp.location}</p>
                )}
                {bullets.length > 0 && (
                  <ul className="space-y-1 mt-2">
                    {bullets.map((bullet, bidx) => {
                      const otherBullet = otherBullets?.[bidx];
                      const isDiff = normalizeText(bullet) !== normalizeText(otherBullet);
                      
                      return (
                        <li 
                          key={bidx} 
                          className={`text-sm flex items-start ${isDiff ? 'text-gray-900 font-medium' : 'text-gray-700'}`}
                        >
                          <span className={`mr-2 mt-1 ${isDiff ? 'text-yellow-600' : 'text-gray-400'}`}>•</span>
                          <span>{bullet}</span>
                        </li>
                      );
                    })}
                  </ul>
                )}
                {bulletsDifferent && (
                  <div className="mt-2 text-xs text-yellow-700 flex items-center">
                    <AlertCircle size={14} className="mr-1" />
                    Responsibilities differ from other resume
                  </div>
                )}
              </div>
            );
          })
        ) : (
          <p className="text-sm text-gray-500 italic">No experience listed</p>
        )}
      </div>
    );
  };

  // Render skills section
  const renderSkills = (skills, label, isLeft = true) => {
    const otherSkills = isLeft ? resumeB?.content?.skills : resumeA?.content?.skills;
    
    const technicalDiff = arraysAreDifferent(skills?.technical, otherSkills?.technical);
    const softDiff = arraysAreDifferent(skills?.soft, otherSkills?.soft);
    
    return (
      <div className="space-y-3">
        <h4 className="font-semibold text-gray-900">Skills</h4>
        
        {skills?.technical && skills.technical.length > 0 && (
          <div className={`border rounded-lg p-3 ${technicalDiff ? 'bg-yellow-50 border-yellow-200' : 'bg-white'}`}>
            <div className="flex items-center mb-2">
              <span className="text-sm font-medium text-gray-700">Technical Skills</span>
              {technicalDiff && <AlertCircle size={14} className="ml-2 text-yellow-600" />}
            </div>
            <div className="flex flex-wrap gap-1">
              {skills.technical.map((skill, idx) => {
                const skillName = typeof skill === 'object' ? skill.name || skill.skill : skill;
                const isInOther = otherSkills?.technical?.some(s => {
                  const otherName = typeof s === 'object' ? s.name || s.skill : s;
                  return normalizeText(otherName) === normalizeText(skillName);
                });
                
                return (
                  <span 
                    key={idx} 
                    className={`px-2 py-1 text-xs rounded ${
                      isInOther 
                        ? 'bg-blue-100 text-blue-700' 
                        : 'bg-green-100 text-green-700 font-medium'
                    }`}
                  >
                    {skillName}
                  </span>
                );
              })}
            </div>
          </div>
        )}
        
        {skills?.soft && skills.soft.length > 0 && (
          <div className={`border rounded-lg p-3 ${softDiff ? 'bg-yellow-50 border-yellow-200' : 'bg-white'}`}>
            <div className="flex items-center mb-2">
              <span className="text-sm font-medium text-gray-700">Soft Skills</span>
              {softDiff && <AlertCircle size={14} className="ml-2 text-yellow-600" />}
            </div>
            <div className="flex flex-wrap gap-1">
              {skills.soft.map((skill, idx) => {
                const skillName = typeof skill === 'object' ? skill.name || skill.skill : skill;
                const isInOther = otherSkills?.soft?.some(s => {
                  const otherName = typeof s === 'object' ? s.name || s.skill : s;
                  return normalizeText(otherName) === normalizeText(skillName);
                });
                
                return (
                  <span 
                    key={idx} 
                    className={`px-2 py-1 text-xs rounded ${
                      isInOther 
                        ? 'bg-purple-100 text-purple-700' 
                        : 'bg-green-100 text-green-700 font-medium'
                    }`}
                  >
                    {skillName}
                  </span>
                );
              })}
            </div>
          </div>
        )}
      </div>
    );
  };

  // Render education section
  const renderEducation = (education, label) => {
    return (
      <div className="space-y-3">
        <h4 className="font-semibold text-gray-900">Education</h4>
        {education && education.length > 0 ? (
          education.map((edu, idx) => (
            <div key={idx} className="border rounded-lg p-3 bg-white">
              <div className="flex justify-between items-start">
                <div>
                  <h5 className="font-semibold text-gray-900">{edu.degree} - {edu.field_of_study}</h5>
                  <p className="text-sm text-gray-700">{edu.institution}</p>
                </div>
                <span className="text-xs text-gray-600">{edu.graduation_year}</span>
              </div>
            </div>
          ))
        ) : (
          <p className="text-sm text-gray-500 italic">No education listed</p>
        )}
      </div>
    );
  };

  if (!resumeA || !resumeB) {
    return (
      <div className="text-center py-8 text-gray-600">
        <p>Unable to load resume comparison. Please try again.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with color legend */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h2 className="text-xl font-bold text-gray-900 mb-3">{title}</h2>
        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center">
            <div className="w-4 h-4 bg-yellow-100 border border-yellow-200 rounded mr-2"></div>
            <span className="text-gray-700">Different content</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-white border border-gray-200 rounded mr-2"></div>
            <span className="text-gray-700">Same content</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-green-100 rounded mr-2"></div>
            <span className="text-gray-700">Unique to this resume</span>
          </div>
        </div>
      </div>

      {/* Side-by-side comparison */}
      <div className="grid grid-cols-2 gap-6">
        {/* Left Resume (A) */}
        <div className="space-y-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <h3 className="font-bold text-blue-900">{resumeA.name || 'Resume A'}</h3>
            <div className="text-sm text-blue-700 mt-1">
              ATS Score: <span className="font-bold">{resumeA.ats_score?.overall_score || 0}%</span>
            </div>
            {resumeA.is_reoptimized && (
              <span className="inline-block mt-1 text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full">
                🎯 Re-optimized
              </span>
            )}
          </div>
          
          {renderHeader(resumeA.content?.header, 'Resume A', true)}
          {renderSummary(resumeA.content?.summary, 'Resume A', true)}
          {renderExperience(resumeA.content?.experience, 'Resume A', true)}
          {renderSkills(resumeA.content?.skills, 'Resume A', true)}
          {renderEducation(resumeA.content?.education, 'Resume A')}
        </div>

        {/* Right Resume (B) */}
        <div className="space-y-6">
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
            <h3 className="font-bold text-purple-900">{resumeB.name || 'Resume B'}</h3>
            <div className="text-sm text-purple-700 mt-1">
              ATS Score: <span className="font-bold">{resumeB.ats_score?.overall_score || 0}%</span>
            </div>
            {resumeB.is_reoptimized && (
              <span className="inline-block mt-1 text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full">
                🎯 Re-optimized
              </span>
            )}
          </div>
          
          {renderHeader(resumeB.content?.header, 'Resume B', false)}
          {renderSummary(resumeB.content?.summary, 'Resume B', false)}
          {renderExperience(resumeB.content?.experience, 'Resume B', false)}
          {renderSkills(resumeB.content?.skills, 'Resume B', false)}
          {renderEducation(resumeB.content?.education, 'Resume B')}
        </div>
      </div>
    </div>
  );
};

export default ResumeDiffViewer;
