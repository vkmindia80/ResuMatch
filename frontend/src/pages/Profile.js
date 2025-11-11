import React, { useState, useEffect, useRef } from 'react';
import { profileAPI } from '../services/api';
import { 
  Save, Plus, Trash2, User, Briefcase, GraduationCap, Code, Upload, 
  FileText, CheckCircle, XCircle, Sparkles, Calendar, MapPin, 
  Building2, Loader2, X, Download, Eye
} from 'lucide-react';

const Profile = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [activeTab, setActiveTab] = useState('personal');
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState('');
  const [uploadStatus, setUploadStatus] = useState('');
  const [loadingAchievements, setLoadingAchievements] = useState({});
  const [loadingResponsibilities, setLoadingResponsibilities] = useState({});
  const [loadingTechnologies, setLoadingTechnologies] = useState({});
  const [loadingSkills, setLoadingSkills] = useState(false);
  const [uploadingCert, setUploadingCert] = useState({});
  const fileInputRef = useRef(null);
  const certInputRefs = useRef({});

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await profileAPI.getProfile();
      setProfile(response.data);
    } catch (error) {
      if (error.response?.status === 404) {
        setProfile({
          personal_info: {
            full_name: '',
            email: '',
            phone: '',
            location: '',
            title: '',
            linkedin: '',
            portfolio: ''
          },
          education: [],
          experience: [],
          skills: {
            technical: [],
            soft: [],
            languages: [],
            tools: []
          },
          projects: [],
          certifications: []
        });
      }
    } finally {
      setLoading(false);
    }
  };

  // Helper function to clean data before sending
  const cleanProfileData = (data) => {
    const cleaned = JSON.parse(JSON.stringify(data)); // Deep clone
    
    // Clean education
    if (cleaned.education) {
      cleaned.education = cleaned.education.map(edu => ({
        ...edu,
        field: edu.field || '',
        start_date: edu.start_date || null,
        end_date: edu.end_date || null,
        gpa: edu.gpa ? parseFloat(edu.gpa) : null,
        achievements: Array.isArray(edu.achievements) ? edu.achievements.filter(a => a && a.trim()) : []
      }));
    }
    
    // Clean experience
    if (cleaned.experience) {
      cleaned.experience = cleaned.experience.map(exp => ({
        ...exp,
        start_date: exp.start_date || null,
        end_date: exp.end_date || null,
        location: exp.location || null,
        responsibilities: Array.isArray(exp.responsibilities) ? exp.responsibilities.filter(r => r && r.trim()) : [],
        achievements: Array.isArray(exp.achievements) ? exp.achievements.filter(a => a && a.trim()) : [],
        technologies: Array.isArray(exp.technologies) ? exp.technologies.filter(t => t && t.trim()) : []
      }));
    }
    
    // Clean skills - ensure technical skills have proper structure
    if (cleaned.skills) {
      if (cleaned.skills.technical) {
        cleaned.skills.technical = cleaned.skills.technical
          .filter(skill => skill && (typeof skill === 'string' ? skill.trim() : skill.name && skill.name.trim()))
          .map(skill => {
            if (typeof skill === 'string') {
              return { name: skill, level: null };
            }
            return { name: skill.name, level: skill.level || null };
          });
      }
      
      if (cleaned.skills.soft) {
        cleaned.skills.soft = cleaned.skills.soft.filter(skill => skill && skill.trim());
      }
    }
    
    return cleaned;
  };

  const handleSaveProfile = async () => {
    setSaving(true);
    setMessage('');
    try {
      if (profile.id) {
        // Prepare update data - only send fields that should be updated
        const updateData = cleanProfileData({
          personal_info: profile.personal_info,
          education: profile.education,
          experience: profile.experience,
          skills: profile.skills,
          projects: profile.projects || [],
          certifications: profile.certifications || []
        });
        
        await profileAPI.updateProfile(updateData);
        setMessage('Profile updated successfully!');
        await fetchProfile(); // Refresh to get latest data
      } else {
        await profileAPI.createProfile(profile.personal_info);
        await fetchProfile();
        setMessage('Profile created successfully!');
      }
    } catch (error) {
      console.error('Save error:', error);
      const errorDetail = error.response?.data?.detail;
      let errorMessage = 'Error saving profile';
      
      if (typeof errorDetail === 'string') {
        errorMessage += ': ' + errorDetail;
      } else if (Array.isArray(errorDetail)) {
        // Validation errors from FastAPI
        const errors = errorDetail.map(err => `${err.loc.join('.')}: ${err.msg}`).join(', ');
        errorMessage += ': ' + errors;
      } else if (error.message) {
        errorMessage += ': ' + error.message;
      }
      
      setMessage(errorMessage);
    } finally {
      setSaving(false);
      setTimeout(() => setMessage(''), 5000);
    }
  };

  const addExperience = () => {
    setProfile({
      ...profile,
      experience: [...profile.experience, {
        id: `temp-${Date.now()}`,
        company: '',
        title: '',
        employment_type: 'Full-time',
        start_date: '',
        end_date: '',
        is_current: false,
        location: '',
        responsibilities: [],
        achievements: [],
        technologies: []
      }]
    });
  };

  const removeExperience = (index) => {
    const newExp = [...profile.experience];
    newExp.splice(index, 1);
    setProfile({ ...profile, experience: newExp });
  };

  const updateExperience = (index, field, value) => {
    const newExp = [...profile.experience];
    newExp[index][field] = value;
    setProfile({ ...profile, experience: newExp });
  };

  const addArrayItem = (expIndex, arrayName) => {
    const newExp = [...profile.experience];
    newExp[expIndex][arrayName] = [...(newExp[expIndex][arrayName] || []), ''];
    setProfile({ ...profile, experience: newExp });
  };

  const updateArrayItem = (expIndex, arrayName, itemIndex, value) => {
    const newExp = [...profile.experience];
    newExp[expIndex][arrayName][itemIndex] = value;
    setProfile({ ...profile, experience: newExp });
  };

  const removeArrayItem = (expIndex, arrayName, itemIndex) => {
    const newExp = [...profile.experience];
    newExp[expIndex][arrayName].splice(itemIndex, 1);
    setProfile({ ...profile, experience: newExp });
  };

  const getAISuggestions = async (expIndex) => {
    const exp = profile.experience[expIndex];
    if (!exp.title || !exp.company) {
      alert('Please fill in job title and company name first');
      return;
    }

    setLoadingAchievements(prev => ({ ...prev, [expIndex]: true }));
    
    try {
      const response = await profileAPI.suggestAchievements({
        job_title: exp.title,
        company: exp.company,
        responsibilities: exp.responsibilities || [],
        technologies: exp.technologies || []
      });

      if (response.data.success && response.data.suggestions.length > 0) {
        const newExp = [...profile.experience];
        newExp[expIndex].achievements = [
          ...(newExp[expIndex].achievements || []),
          ...response.data.suggestions
        ];
        setProfile({ ...profile, experience: newExp });
      }
    } catch (error) {
      console.error('Error getting suggestions:', error);
      alert('Failed to get AI suggestions. Please try again.');
    } finally {
      setLoadingAchievements(prev => ({ ...prev, [expIndex]: false }));
    }
  };

  const getResponsibilitySuggestions = async (expIndex) => {
    const exp = profile.experience[expIndex];
    if (!exp.title || !exp.company) {
      alert('Please fill in job title and company name first');
      return;
    }

    setLoadingResponsibilities(prev => ({ ...prev, [expIndex]: true }));
    
    try {
      const response = await profileAPI.suggestResponsibilities({
        job_title: exp.title,
        company: exp.company,
        current_responsibilities: exp.responsibilities || [],
        technologies: exp.technologies || [],
        job_description: null // Can be enhanced to fetch from saved job descriptions
      });

      if (response.data.success && response.data.suggestions.length > 0) {
        const newExp = [...profile.experience];
        newExp[expIndex].responsibilities = [
          ...(newExp[expIndex].responsibilities || []),
          ...response.data.suggestions
        ];
        setProfile({ ...profile, experience: newExp });
      }
    } catch (error) {
      console.error('Error getting responsibility suggestions:', error);
      alert('Failed to get AI suggestions. Please try again.');
    } finally {
      setLoadingResponsibilities(prev => ({ ...prev, [expIndex]: false }));
    }
  };

  const getTechnologySuggestions = async (expIndex) => {
    const exp = profile.experience[expIndex];
    if (!exp.title) {
      alert('Please fill in job title first');
      return;
    }

    setLoadingTechnologies(prev => ({ ...prev, [expIndex]: true }));
    
    try {
      const response = await profileAPI.suggestTechnologies({
        job_title: exp.title,
        company: exp.company || null,
        current_technologies: exp.technologies || [],
        industry: null, // Can be enhanced to include industry field
        job_description: null // Can be enhanced to fetch from saved job descriptions
      });

      if (response.data.success && response.data.suggestions.length > 0) {
        const newExp = [...profile.experience];
        newExp[expIndex].technologies = [
          ...(newExp[expIndex].technologies || []),
          ...response.data.suggestions
        ];
        setProfile({ ...profile, experience: newExp });
      }
    } catch (error) {
      console.error('Error getting technology suggestions:', error);
      alert('Failed to get AI suggestions. Please try again.');
    } finally {
      setLoadingTechnologies(prev => ({ ...prev, [expIndex]: false }));
    }
  };

  const addEducation = () => {
    setProfile({
      ...profile,
      education: [...profile.education, {
        id: `temp-${Date.now()}`,
        institution: '',
        degree: '',
        field: '',
        start_date: '',
        end_date: '',
        gpa: '',
        achievements: [],
        certificate_url: null
      }]
    });
  };

  const removeEducation = (index) => {
    const newEdu = [...profile.education];
    newEdu.splice(index, 1);
    setProfile({ ...profile, education: newEdu });
  };

  const updateEducation = (index, field, value) => {
    const newEdu = [...profile.education];
    newEdu[index][field] = value;
    setProfile({ ...profile, education: newEdu });
  };

  const handleCertificateUpload = async (eduIndex, event) => {
    const file = event.target.files[0];
    if (!file) return;

    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png'];
    if (!allowedTypes.includes(file.type)) {
      alert('Invalid file type. Please upload PDF, JPG, or PNG file.');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      alert('File size too large. Maximum size is 10MB.');
      return;
    }

    setUploadingCert(prev => ({ ...prev, [eduIndex]: true }));

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('education_id', profile.education[eduIndex].id);

      const response = await profileAPI.uploadCertificate(formData);
      
      if (response.data.success) {
        const newEdu = [...profile.education];
        newEdu[eduIndex].certificate_url = response.data.storage_info.url;
        setProfile({ ...profile, education: newEdu });
        await fetchProfile(); // Refresh to get updated data
      }
    } catch (error) {
      alert('Error uploading certificate: ' + (error.response?.data?.detail || error.message));
    } finally {
      setUploadingCert(prev => ({ ...prev, [eduIndex]: false }));
    }
  };

  const deleteCertificate = async (eduIndex) => {
    const eduId = profile.education[eduIndex].id;
    
    try {
      await profileAPI.deleteCertificate(eduId);
      const newEdu = [...profile.education];
      newEdu[eduIndex].certificate_url = null;
      setProfile({ ...profile, education: newEdu });
    } catch (error) {
      alert('Error deleting certificate: ' + (error.response?.data?.detail || error.message));
    }
  };

  const getSkillSuggestions = async () => {
    setLoadingSkills(true);
    
    try {
      const currentTechnical = profile.skills.technical?.map(s => typeof s === 'string' ? s : s.name) || [];
      const currentSoft = profile.skills.soft || [];
      
      const response = await profileAPI.suggestSkills({
        job_title: profile.personal_info?.title || '',
        current_skills: [...currentTechnical, ...currentSoft],
        experience_level: 'Intermediate'
      });

      if (response.data.success) {
        const { technical, soft } = response.data.suggestions;
        
        // Add suggested skills (avoid duplicates)
        const existingTechnical = new Set(currentTechnical);
        const existingSoft = new Set(currentSoft);
        
        const newTechnical = technical
          .filter(skill => !existingTechnical.has(skill))
          .map(skill => ({ name: skill, level: null }));
        
        const newSoft = soft.filter(skill => !existingSoft.has(skill));
        
        setProfile({
          ...profile,
          skills: {
            ...profile.skills,
            technical: [...(profile.skills.technical || []), ...newTechnical],
            soft: [...(profile.skills.soft || []), ...newSoft]
          }
        });
      }
    } catch (error) {
      console.error('Error getting skill suggestions:', error);
      alert('Failed to get skill suggestions. Please try again.');
    } finally {
      setLoadingSkills(false);
    }
  };

  const addTechnicalSkill = () => {
    setProfile({
      ...profile,
      skills: {
        ...profile.skills,
        technical: [...(profile.skills.technical || []), { name: '', level: null }]
      }
    });
  };

  const updateTechnicalSkill = (index, field, value) => {
    const newSkills = [...(profile.skills.technical || [])];
    newSkills[index] = { ...newSkills[index], [field]: value };
    setProfile({
      ...profile,
      skills: { ...profile.skills, technical: newSkills }
    });
  };

  const removeTechnicalSkill = (index) => {
    const newSkills = [...(profile.skills.technical || [])];
    newSkills.splice(index, 1);
    setProfile({
      ...profile,
      skills: { ...profile.skills, technical: newSkills }
    });
  };

  const addSoftSkill = () => {
    setProfile({
      ...profile,
      skills: {
        ...profile.skills,
        soft: [...(profile.skills.soft || []), '']
      }
    });
  };

  const updateSoftSkill = (index, value) => {
    const newSkills = [...(profile.skills.soft || [])];
    newSkills[index] = value;
    setProfile({
      ...profile,
      skills: { ...profile.skills, soft: newSkills }
    });
  };

  const removeSoftSkill = (index) => {
    const newSkills = [...(profile.skills.soft || [])];
    newSkills.splice(index, 1);
    setProfile({
      ...profile,
      skills: { ...profile.skills, soft: newSkills }
    });
  };

  const handleResumeUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword', 'text/plain'];
    if (!allowedTypes.includes(file.type)) {
      setUploadStatus('error');
      setUploadMessage('Invalid file type. Please upload PDF, DOCX, or TXT file.');
      setTimeout(() => {
        setUploadMessage('');
        setUploadStatus('');
      }, 5000);
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setUploadStatus('error');
      setUploadMessage('File size too large. Maximum size is 10MB.');
      setTimeout(() => {
        setUploadMessage('');
        setUploadStatus('');
      }, 5000);
      return;
    }

    setUploading(true);
    setUploadMessage('');
    setUploadStatus('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await profileAPI.parseResume(formData);
      
      if (response.data.success) {
        setProfile(response.data.profile);
        setUploadStatus('success');
        setUploadMessage('Resume parsed successfully! Your profile has been updated with all information.');
        
        setTimeout(() => {
          setUploadMessage('');
          setUploadStatus('');
        }, 5000);
      }
    } catch (error) {
      setUploadStatus('error');
      setUploadMessage('Error parsing resume: ' + (error.response?.data?.detail || error.message));
      setTimeout(() => {
        setUploadMessage('');
        setUploadStatus('');
      }, 5000);
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const triggerFileUpload = () => {
    fileInputRef.current?.click();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="inline-block w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="mt-4 text-secondary-600">Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8" data-testid="profile-page">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-secondary-900">My Profile</h1>
          <p className="text-secondary-600 mt-1">Build your professional profile with AI assistance</p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={triggerFileUpload}
            disabled={uploading}
            data-testid="import-resume-button"
            className="btn-secondary flex items-center space-x-2 disabled:opacity-50"
          >
            <Upload size={18} />
            <span>{uploading ? 'Uploading...' : 'Import Resume'}</span>
          </button>
          <button
            onClick={handleSaveProfile}
            disabled={saving}
            data-testid="save-profile-button"
            className="btn-primary flex items-center space-x-2 disabled:opacity-50"
          >
            <Save size={18} />
            <span>{saving ? 'Saving...' : 'Save Profile'}</span>
          </button>
        </div>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.docx,.doc,.txt"
        onChange={handleResumeUpload}
        style={{ display: 'none' }}
        data-testid="resume-file-input"
      />

      {/* Messages */}
      {message && (
        <div className={`mb-4 p-4 rounded-lg ${message.includes('Error') ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'}`}>
          {message}
        </div>
      )}

      {uploadMessage && (
        <div className={`mb-4 p-4 rounded-lg flex items-center space-x-3 ${
          uploadStatus === 'success' ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
        }`}>
          {uploadStatus === 'success' ? (
            <CheckCircle className="text-green-600" size={24} />
          ) : (
            <XCircle className="text-red-600" size={24} />
          )}
          <span className={uploadStatus === 'success' ? 'text-green-700' : 'text-red-700'}>
            {uploadMessage}
          </span>
        </div>
      )}

      {/* Tabs */}
      <div className="mb-6 border-b border-secondary-200">
        <div className="flex space-x-8">
          {[
            { id: 'personal', label: 'Personal Info', icon: User },
            { id: 'experience', label: 'Experience', icon: Briefcase },
            { id: 'education', label: 'Education', icon: GraduationCap },
            { id: 'skills', label: 'Skills', icon: Code }
          ].map(tab => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                data-testid={`tab-${tab.id}`}
                className={`flex items-center space-x-2 py-4 border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-primary-600 text-primary-600'
                    : 'border-transparent text-secondary-600 hover:text-secondary-900'
                }`}
              >
                <Icon size={18} />
                <span className="font-medium">{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Personal Info Tab */}
      {activeTab === 'personal' && (
        <div className="card space-y-6">
          <h2 className="text-xl font-semibold text-secondary-900">Personal Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">Full Name *</label>
              <input
                type="text"
                data-testid="fullname-input"
                value={profile.personal_info.full_name}
                onChange={(e) => setProfile({
                  ...profile,
                  personal_info: { ...profile.personal_info, full_name: e.target.value }
                })}
                className="input-field"
                placeholder="John Doe"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">Email *</label>
              <input
                type="email"
                data-testid="email-input"
                value={profile.personal_info.email}
                onChange={(e) => setProfile({
                  ...profile,
                  personal_info: { ...profile.personal_info, email: e.target.value }
                })}
                className="input-field"
                placeholder="john@example.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">Phone</label>
              <input
                type="tel"
                value={profile.personal_info.phone || ''}
                onChange={(e) => setProfile({
                  ...profile,
                  personal_info: { ...profile.personal_info, phone: e.target.value }
                })}
                className="input-field"
                placeholder="+1 (555) 123-4567"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">Location</label>
              <input
                type="text"
                value={profile.personal_info.location || ''}
                onChange={(e) => setProfile({
                  ...profile,
                  personal_info: { ...profile.personal_info, location: e.target.value }
                })}
                className="input-field"
                placeholder="San Francisco, CA"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">Professional Title</label>
              <input
                type="text"
                value={profile.personal_info.title || ''}
                onChange={(e) => setProfile({
                  ...profile,
                  personal_info: { ...profile.personal_info, title: e.target.value }
                })}
                className="input-field"
                placeholder="Software Engineer"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">LinkedIn URL</label>
              <input
                type="url"
                value={profile.personal_info.linkedin || ''}
                onChange={(e) => setProfile({
                  ...profile,
                  personal_info: { ...profile.personal_info, linkedin: e.target.value }
                })}
                className="input-field"
                placeholder="https://linkedin.com/in/johndoe"
              />
            </div>
          </div>
        </div>
      )}

      {/* Experience Tab */}
      {activeTab === 'experience' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-xl font-semibold text-secondary-900">Work Experience</h2>
              <p className="text-sm text-secondary-600 mt-1">Add your professional experience with AI-powered achievement suggestions</p>
            </div>
            <button
              onClick={addExperience}
              data-testid="add-experience-button"
              className="btn-secondary flex items-center space-x-2"
            >
              <Plus size={18} />
              <span>Add Experience</span>
            </button>
          </div>

          {profile.experience && profile.experience.length > 0 ? (
            profile.experience.map((exp, index) => (
              <div key={exp.id || index} className="card space-y-4 relative" data-testid={`experience-item-${index}`}>
                {/* Delete Button */}
                <button
                  onClick={() => removeExperience(index)}
                  className="absolute top-4 right-4 text-red-600 hover:text-red-700 p-2 hover:bg-red-50 rounded-lg transition-colors"
                  data-testid={`delete-experience-${index}`}
                >
                  <Trash2 size={18} />
                </button>

                {/* Basic Info */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pr-12">
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 mb-2">
                      <Building2 size={14} className="inline mr-1" />
                      Company Name *
                    </label>
                    <input
                      type="text"
                      value={exp.company}
                      onChange={(e) => updateExperience(index, 'company', e.target.value)}
                      className="input-field"
                      placeholder="Google"
                      data-testid={`exp-company-${index}`}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 mb-2">
                      <Briefcase size={14} className="inline mr-1" />
                      Job Title *
                    </label>
                    <input
                      type="text"
                      value={exp.title}
                      onChange={(e) => updateExperience(index, 'title', e.target.value)}
                      className="input-field"
                      placeholder="Senior Software Engineer"
                      data-testid={`exp-title-${index}`}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 mb-2">
                      <Calendar size={14} className="inline mr-1" />
                      Start Date *
                    </label>
                    <input
                      type="date"
                      value={exp.start_date || ''}
                      onChange={(e) => updateExperience(index, 'start_date', e.target.value)}
                      className="input-field"
                      data-testid={`exp-start-date-${index}`}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 mb-2">
                      <Calendar size={14} className="inline mr-1" />
                      End Date
                    </label>
                    <input
                      type="date"
                      value={exp.end_date || ''}
                      onChange={(e) => updateExperience(index, 'end_date', e.target.value)}
                      className="input-field"
                      disabled={exp.is_current}
                      data-testid={`exp-end-date-${index}`}
                    />
                    <label className="flex items-center mt-2">
                      <input
                        type="checkbox"
                        checked={exp.is_current || false}
                        onChange={(e) => {
                          updateExperience(index, 'is_current', e.target.checked);
                          if (e.target.checked) {
                            updateExperience(index, 'end_date', '');
                          }
                        }}
                        className="mr-2"
                      />
                      <span className="text-sm text-secondary-700">Currently working here</span>
                    </label>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 mb-2">
                      <MapPin size={14} className="inline mr-1" />
                      Location
                    </label>
                    <input
                      type="text"
                      value={exp.location || ''}
                      onChange={(e) => updateExperience(index, 'location', e.target.value)}
                      className="input-field"
                      placeholder="San Francisco, CA"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 mb-2">Employment Type</label>
                    <select
                      value={exp.employment_type}
                      onChange={(e) => updateExperience(index, 'employment_type', e.target.value)}
                      className="input-field"
                    >
                      <option value="Full-time">Full-time</option>
                      <option value="Part-time">Part-time</option>
                      <option value="Contract">Contract</option>
                      <option value="Freelance">Freelance</option>
                      <option value="Internship">Internship</option>
                    </select>
                  </div>
                </div>

                {/* Achievements with AI Suggestions */}
                <div className="border-t pt-4">
                  <div className="flex justify-between items-center mb-3">
                    <label className="block text-sm font-medium text-secondary-700">
                      <Sparkles size={14} className="inline mr-1 text-primary-600" />
                      Key Achievements
                    </label>
                    <button
                      onClick={() => getAISuggestions(index)}
                      disabled={loadingAchievements[index]}
                      className="btn-secondary text-sm py-1 px-3 flex items-center space-x-2"
                      data-testid={`ai-suggest-achievements-${index}`}
                    >
                      {loadingAchievements[index] ? (
                        <>
                          <Loader2 size={14} className="animate-spin" />
                          <span>Generating...</span>
                        </>
                      ) : (
                        <>
                          <Sparkles size={14} />
                          <span>AI Suggest</span>
                        </>
                      )}
                    </button>
                  </div>
                  {(exp.achievements || []).map((achievement, achIndex) => (
                    <div key={achIndex} className="flex items-start space-x-2 mb-2">
                      <textarea
                        value={achievement}
                        onChange={(e) => updateArrayItem(index, 'achievements', achIndex, e.target.value)}
                        className="input-field flex-1 min-h-[60px]"
                        placeholder="Describe a key achievement with measurable results..."
                        rows="2"
                      />
                      <button
                        onClick={() => removeArrayItem(index, 'achievements', achIndex)}
                        className="text-red-600 hover:text-red-700 p-2"
                      >
                        <X size={18} />
                      </button>
                    </div>
                  ))}
                  <button
                    onClick={() => addArrayItem(index, 'achievements')}
                    className="text-primary-600 hover:text-primary-700 text-sm font-medium flex items-center space-x-1"
                  >
                    <Plus size={14} />
                    <span>Add Achievement</span>
                  </button>
                </div>

                {/* Responsibilities */}
                <div className="border-t pt-4">
                  <div className="flex justify-between items-center mb-3">
                    <label className="block text-sm font-medium text-secondary-700">
                      <Sparkles size={14} className="inline mr-1 text-primary-600" />
                      Responsibilities
                    </label>
                    <button
                      onClick={() => getResponsibilitySuggestions(index)}
                      disabled={loadingResponsibilities[index]}
                      className="btn-secondary text-sm py-1 px-3 flex items-center space-x-2"
                      data-testid={`ai-suggest-responsibilities-${index}`}
                    >
                      {loadingResponsibilities[index] ? (
                        <>
                          <Loader2 size={14} className="animate-spin" />
                          <span>Generating...</span>
                        </>
                      ) : (
                        <>
                          <Sparkles size={14} />
                          <span>AI Suggest</span>
                        </>
                      )}
                    </button>
                  </div>
                  {(exp.responsibilities || []).map((resp, respIndex) => (
                    <div key={respIndex} className="flex items-start space-x-2 mb-2">
                      <input
                        type="text"
                        value={resp}
                        onChange={(e) => updateArrayItem(index, 'responsibilities', respIndex, e.target.value)}
                        className="input-field flex-1"
                        placeholder="Describe a responsibility..."
                      />
                      <button
                        onClick={() => removeArrayItem(index, 'responsibilities', respIndex)}
                        className="text-red-600 hover:text-red-700 p-2"
                      >
                        <X size={18} />
                      </button>
                    </div>
                  ))}
                  <button
                    onClick={() => addArrayItem(index, 'responsibilities')}
                    className="text-primary-600 hover:text-primary-700 text-sm font-medium flex items-center space-x-1"
                  >
                    <Plus size={14} />
                    <span>Add Responsibility</span>
                  </button>
                </div>

                {/* Technologies */}
                <div className="border-t pt-4">
                  <div className="flex justify-between items-center mb-3">
                    <label className="block text-sm font-medium text-secondary-700">
                      <Sparkles size={14} className="inline mr-1 text-primary-600" />
                      Technologies Used
                    </label>
                    <button
                      onClick={() => getTechnologySuggestions(index)}
                      disabled={loadingTechnologies[index]}
                      className="btn-secondary text-sm py-1 px-3 flex items-center space-x-2"
                      data-testid={`ai-suggest-technologies-${index}`}
                    >
                      {loadingTechnologies[index] ? (
                        <>
                          <Loader2 size={14} className="animate-spin" />
                          <span>Generating...</span>
                        </>
                      ) : (
                        <>
                          <Sparkles size={14} />
                          <span>AI Suggest</span>
                        </>
                      )}
                    </button>
                  </div>
                  {(exp.technologies || []).map((tech, techIndex) => (
                    <div key={techIndex} className="flex items-center space-x-2 mb-2">
                      <input
                        type="text"
                        value={tech}
                        onChange={(e) => updateArrayItem(index, 'technologies', techIndex, e.target.value)}
                        className="input-field flex-1"
                        placeholder="e.g., React, Python, AWS"
                      />
                      <button
                        onClick={() => removeArrayItem(index, 'technologies', techIndex)}
                        className="text-red-600 hover:text-red-700 p-2"
                      >
                        <X size={18} />
                      </button>
                    </div>
                  ))}
                  <button
                    onClick={() => addArrayItem(index, 'technologies')}
                    className="text-primary-600 hover:text-primary-700 text-sm font-medium flex items-center space-x-1"
                  >
                    <Plus size={14} />
                    <span>Add Technology</span>
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="card text-center text-secondary-600 py-12">
              <Briefcase size={48} className="mx-auto mb-4 text-secondary-400" />
              <p className="font-medium">No work experience added yet</p>
              <p className="text-sm mt-2">Click "Add Experience" to get started or import from your resume</p>
            </div>
          )}
        </div>
      )}

      {/* Education Tab */}
      {activeTab === 'education' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-xl font-semibold text-secondary-900">Education</h2>
              <p className="text-sm text-secondary-600 mt-1">Add your educational background and upload certificates</p>
            </div>
            <button
              onClick={addEducation}
              data-testid="add-education-button"
              className="btn-secondary flex items-center space-x-2"
            >
              <Plus size={18} />
              <span>Add Education</span>
            </button>
          </div>

          {profile.education && profile.education.length > 0 ? (
            profile.education.map((edu, index) => (
              <div key={edu.id || index} className="card space-y-4 relative" data-testid={`education-item-${index}`}>
                <button
                  onClick={() => removeEducation(index)}
                  className="absolute top-4 right-4 text-red-600 hover:text-red-700 p-2 hover:bg-red-50 rounded-lg transition-colors"
                  data-testid={`delete-education-${index}`}
                >
                  <Trash2 size={18} />
                </button>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pr-12">
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 mb-2">
                      <GraduationCap size={14} className="inline mr-1" />
                      Institution Name *
                    </label>
                    <input
                      type="text"
                      value={edu.institution}
                      onChange={(e) => updateEducation(index, 'institution', e.target.value)}
                      className="input-field"
                      placeholder="Stanford University"
                      data-testid={`edu-institution-${index}`}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 mb-2">Degree *</label>
                    <input
                      type="text"
                      value={edu.degree}
                      onChange={(e) => updateEducation(index, 'degree', e.target.value)}
                      className="input-field"
                      placeholder="Bachelor of Science"
                      data-testid={`edu-degree-${index}`}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 mb-2">Field of Study</label>
                    <input
                      type="text"
                      value={edu.field || ''}
                      onChange={(e) => updateEducation(index, 'field', e.target.value)}
                      className="input-field"
                      placeholder="Computer Science"
                      data-testid={`edu-field-${index}`}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 mb-2">GPA (Optional)</label>
                    <input
                      type="number"
                      step="0.01"
                      value={edu.gpa || ''}
                      onChange={(e) => updateEducation(index, 'gpa', e.target.value)}
                      className="input-field"
                      placeholder="3.8"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 mb-2">
                      <Calendar size={14} className="inline mr-1" />
                      Start Date (Optional)
                    </label>
                    <input
                      type="date"
                      value={edu.start_date || ''}
                      onChange={(e) => updateEducation(index, 'start_date', e.target.value)}
                      className="input-field"
                      data-testid={`edu-start-date-${index}`}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 mb-2">
                      <Calendar size={14} className="inline mr-1" />
                      End Date (Optional)
                    </label>
                    <input
                      type="date"
                      value={edu.end_date || ''}
                      onChange={(e) => updateEducation(index, 'end_date', e.target.value)}
                      className="input-field"
                      data-testid={`edu-end-date-${index}`}
                    />
                  </div>
                </div>

                {/* Certificate Upload */}
                <div className="border-t pt-4">
                  <label className="block text-sm font-medium text-secondary-700 mb-3">Certificate (Optional)</label>
                  {edu.certificate_url ? (
                    <div className="flex items-center space-x-3 bg-green-50 border border-green-200 rounded-lg p-3">
                      <CheckCircle className="text-green-600" size={20} />
                      <span className="text-sm text-green-700 flex-1">Certificate uploaded successfully</span>
                      <a
                        href={edu.certificate_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary-600 hover:text-primary-700 p-2"
                        title="View Certificate"
                      >
                        <Eye size={18} />
                      </a>
                      <button
                        onClick={() => deleteCertificate(index)}
                        className="text-red-600 hover:text-red-700 p-2"
                        title="Delete Certificate"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  ) : (
                    <div>
                      <input
                        ref={el => certInputRefs.current[index] = el}
                        type="file"
                        accept=".pdf,.jpg,.jpeg,.png"
                        onChange={(e) => handleCertificateUpload(index, e)}
                        style={{ display: 'none' }}
                        data-testid={`cert-input-${index}`}
                      />
                      <button
                        onClick={() => certInputRefs.current[index]?.click()}
                        disabled={uploadingCert[index]}
                        className="btn-secondary flex items-center space-x-2"
                        data-testid={`upload-cert-${index}`}
                      >
                        {uploadingCert[index] ? (
                          <>
                            <Loader2 size={18} className="animate-spin" />
                            <span>Uploading...</span>
                          </>
                        ) : (
                          <>
                            <Upload size={18} />
                            <span>Upload Certificate</span>
                          </>
                        )}
                      </button>
                      <p className="text-xs text-secondary-500 mt-2">Supported: PDF, JPG, PNG (Max 10MB)</p>
                    </div>
                  )}
                </div>
              </div>
            ))
          ) : (
            <div className="card text-center text-secondary-600 py-12">
              <GraduationCap size={48} className="mx-auto mb-4 text-secondary-400" />
              <p className="font-medium">No education added yet</p>
              <p className="text-sm mt-2">Click "Add Education" to get started or import from your resume</p>
            </div>
          )}
        </div>
      )}

      {/* Skills Tab */}
      {activeTab === 'skills' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-xl font-semibold text-secondary-900">Skills</h2>
              <p className="text-sm text-secondary-600 mt-1">Organize your skills with AI-powered suggestions</p>
            </div>
            <button
              onClick={getSkillSuggestions}
              disabled={loadingSkills}
              className="btn-primary flex items-center space-x-2"
              data-testid="ai-suggest-skills"
            >
              {loadingSkills ? (
                <>
                  <Loader2 size={18} className="animate-spin" />
                  <span>Generating...</span>
                </>
              ) : (
                <>
                  <Sparkles size={18} />
                  <span>AI Suggest Skills</span>
                </>
              )}
            </button>
          </div>

          {/* Technical Skills */}
          <div className="card space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-secondary-900">Technical Skills</h3>
              <button
                onClick={addTechnicalSkill}
                className="btn-secondary text-sm py-1 px-3 flex items-center space-x-1"
                data-testid="add-technical-skill"
              >
                <Plus size={14} />
                <span>Add Skill</span>
              </button>
            </div>
            {(profile.skills?.technical || []).length > 0 ? (
              <div className="space-y-3">
                {profile.skills.technical.map((skill, index) => (
                  <div key={index} className="flex items-center space-x-3" data-testid={`technical-skill-${index}`}>
                    <input
                      type="text"
                      value={typeof skill === 'string' ? skill : skill.name}
                      onChange={(e) => updateTechnicalSkill(index, 'name', e.target.value)}
                      className="input-field flex-1"
                      placeholder="e.g., Python, React, AWS"
                    />
                    <select
                      value={typeof skill === 'string' ? '' : (skill.level || '')}
                      onChange={(e) => updateTechnicalSkill(index, 'level', e.target.value)}
                      className="input-field w-40"
                    >
                      <option value="">Select Level</option>
                      <option value="Beginner">Beginner</option>
                      <option value="Intermediate">Intermediate</option>
                      <option value="Advanced">Advanced</option>
                      <option value="Expert">Expert</option>
                    </select>
                    <button
                      onClick={() => removeTechnicalSkill(index)}
                      className="text-red-600 hover:text-red-700 p-2"
                    >
                      <X size={18} />
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-secondary-500 text-sm">No technical skills added yet</p>
            )}
          </div>

          {/* Soft Skills */}
          <div className="card space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-secondary-900">Soft Skills</h3>
              <button
                onClick={addSoftSkill}
                className="btn-secondary text-sm py-1 px-3 flex items-center space-x-1"
                data-testid="add-soft-skill"
              >
                <Plus size={14} />
                <span>Add Skill</span>
              </button>
            </div>
            {(profile.skills?.soft || []).length > 0 ? (
              <div className="space-y-3">
                {profile.skills.soft.map((skill, index) => (
                  <div key={index} className="flex items-center space-x-3" data-testid={`soft-skill-${index}`}>
                    <input
                      type="text"
                      value={skill}
                      onChange={(e) => updateSoftSkill(index, e.target.value)}
                      className="input-field flex-1"
                      placeholder="e.g., Leadership, Communication, Problem Solving"
                    />
                    <button
                      onClick={() => removeSoftSkill(index)}
                      className="text-red-600 hover:text-red-700 p-2"
                    >
                      <X size={18} />
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-secondary-500 text-sm">No soft skills added yet</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Profile;
