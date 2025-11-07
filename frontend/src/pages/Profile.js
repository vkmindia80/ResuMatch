import React, { useState, useEffect } from 'react';
import { profileAPI } from '../services/api';
import { Save, Plus, Trash2, User, Briefcase, GraduationCap, Award, Code } from 'lucide-react';

const Profile = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [activeTab, setActiveTab] = useState('personal');

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await profileAPI.getProfile();
      setProfile(response.data);
    } catch (error) {
      if (error.response?.status === 404) {
        // Profile doesn't exist yet
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

  const handleSaveProfile = async () => {
    setSaving(true);
    setMessage('');
    try {
      if (profile.id) {
        await profileAPI.updateProfile(profile);
        setMessage('Profile updated successfully!');
      } else {
        await profileAPI.createProfile(profile.personal_info);
        await fetchProfile();
        setMessage('Profile created successfully!');
      }
    } catch (error) {
      setMessage('Error saving profile: ' + (error.response?.data?.detail || error.message));
    } finally {
      setSaving(false);
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const addExperience = () => {
    setProfile({
      ...profile,
      experience: [...profile.experience, {
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

  const addEducation = () => {
    setProfile({
      ...profile,
      education: [...profile.education, {
        institution: '',
        degree: '',
        field: '',
        start_date: '',
        end_date: '',
        gpa: '',
        achievements: []
      }]
    });
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
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-secondary-900">My Profile</h1>
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

      {message && (
        <div className={`mb-4 p-4 rounded-lg ${message.includes('Error') ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'}`}>
          {message}
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
              <label className="block text-sm font-medium text-secondary-700 mb-2">Full Name</label>
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
              <label className="block text-sm font-medium text-secondary-700 mb-2">Email</label>
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
            <h2 className="text-xl font-semibold text-secondary-900">Work Experience</h2>
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
              <div key={index} className="card space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <input
                    type="text"
                    value={exp.company}
                    onChange={(e) => {
                      const newExp = [...profile.experience];
                      newExp[index].company = e.target.value;
                      setProfile({ ...profile, experience: newExp });
                    }}
                    className="input-field"
                    placeholder="Company Name"
                  />
                  <input
                    type="text"
                    value={exp.title}
                    onChange={(e) => {
                      const newExp = [...profile.experience];
                      newExp[index].title = e.target.value;
                      setProfile({ ...profile, experience: newExp });
                    }}
                    className="input-field"
                    placeholder="Job Title"
                  />
                </div>
              </div>
            ))
          ) : (
            <div className="card text-center text-secondary-600 py-12">
              <p>No work experience added yet.</p>
              <p className="text-sm mt-2">Click "Add Experience" to get started.</p>
            </div>
          )}
        </div>
      )}

      {/* Education Tab */}
      {activeTab === 'education' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-secondary-900">Education</h2>
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
              <div key={index} className="card space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <input
                    type="text"
                    value={edu.institution}
                    onChange={(e) => {
                      const newEdu = [...profile.education];
                      newEdu[index].institution = e.target.value;
                      setProfile({ ...profile, education: newEdu });
                    }}
                    className="input-field"
                    placeholder="Institution Name"
                  />
                  <input
                    type="text"
                    value={edu.degree}
                    onChange={(e) => {
                      const newEdu = [...profile.education];
                      newEdu[index].degree = e.target.value;
                      setProfile({ ...profile, education: newEdu });
                    }}
                    className="input-field"
                    placeholder="Degree"
                  />
                </div>
              </div>
            ))
          ) : (
            <div className="card text-center text-secondary-600 py-12">
              <p>No education added yet.</p>
              <p className="text-sm mt-2">Click "Add Education" to get started.</p>
            </div>
          )}
        </div>
      )}

      {/* Skills Tab */}
      {activeTab === 'skills' && (
        <div className="card space-y-6">
          <h2 className="text-xl font-semibold text-secondary-900">Skills</h2>
          <p className="text-secondary-600 text-sm">Add your technical and soft skills to showcase your abilities.</p>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">Technical Skills</label>
              <input
                type="text"
                className="input-field"
                placeholder="e.g., Python, JavaScript, React (comma separated)"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">Soft Skills</label>
              <input
                type="text"
                className="input-field"
                placeholder="e.g., Leadership, Communication, Problem-solving"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Profile;
