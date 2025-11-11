import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Mic, MicOff, Play, Pause, Square, Sparkles, 
  MessageSquare, Brain, Clock, Check, AlertCircle,
  Settings, ChevronDown, ChevronUp, Loader
} from 'lucide-react';
import api from '../services/api';

const LiveInterview = () => {
  const navigate = useNavigate();
  const [isListening, setIsListening] = useState(false);
  const [sessionActive, setSessionActive] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [transcript, setTranscript] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [aiAnswer, setAiAnswer] = useState(null);
  const [isGeneratingAnswer, setIsGeneratingAnswer] = useState(false);
  const [sessionTime, setSessionTime] = useState(0);
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState('');
  const [resumes, setResumes] = useState([]);
  const [selectedResume, setSelectedResume] = useState('');
  const [resumeSource, setResumeSource] = useState('profile');
  const [sessionTitle, setSessionTitle] = useState('');
  const [showSettings, setShowSettings] = useState(false);
  const [modelPreference, setModelPreference] = useState('gpt-4');
  const [language, setLanguage] = useState('en-US');
  const [showContext, setShowContext] = useState(true);
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState(null);
  const [sessionData, setSessionData] = useState(null);
  
  const recognitionRef = useRef(null);
  const timerRef = useRef(null);
  const transcriptEndRef = useRef(null);

  useEffect(() => {
    loadJobs();
    loadResumes();
    loadProfile();
    
    // Check for Web Speech API support
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      setError('Speech recognition is not supported in your browser. Please use Chrome or Edge.');
    }
    
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  useEffect(() => {
    // Auto-scroll transcript
    transcriptEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [transcript]);

  const loadJobs = async () => {
    try {
      const response = await api.get('/api/jobs/');
      // Handle both array and object with items property
      const jobsData = Array.isArray(response.data) 
        ? response.data 
        : (response.data?.items || []);
      setJobs(jobsData);
    } catch (error) {
      console.error('Error loading jobs:', error);
      setJobs([]); // Ensure jobs is always an array
    }
  };

  const loadResumes = async () => {
    try {
      const response = await api.get('/api/resumes/');
      // Handle both array and object with items property
      const resumesData = Array.isArray(response.data) 
        ? response.data 
        : (response.data?.items || []);
      setResumes(resumesData);
    } catch (error) {
      console.error('Error loading resumes:', error);
      setResumes([]); // Ensure resumes is always an array
    }
  };

  const loadProfile = async () => {
    try {
      const response = await api.get('/api/profiles/me');
      setProfile(response.data);
    } catch (error) {
      console.error('Error loading profile:', error);
    }
  };

  const startSession = async () => {
    if (!sessionTitle.trim()) {
      setError('Please enter a session title');
      return;
    }

    try {
      const response = await api.post('/api/live-interview/sessions/start', {
        title: sessionTitle,
        job_description_id: selectedJob || null,
        resume_id: resumeSource === 'generated' ? selectedResume : null,
        resume_source: resumeSource,
        language: language,
        model_preference: modelPreference
      });
      
      setSessionId(response.data.id);
      setSessionData(response.data);
      setSessionActive(true);
      setError(null);
      
      // Start timer
      timerRef.current = setInterval(() => {
        setSessionTime(prev => prev + 1);
      }, 1000);
      
      // Initialize speech recognition
      initializeSpeechRecognition();
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to start session');
    }
  };

  const initializeSpeechRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = language;
    
    recognition.onresult = async (event) => {
      let interimTranscript = '';
      let finalTranscript = '';
      
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript + ' ';
          
          // Add to transcript
          const entry = {
            timestamp: new Date(),
            text: transcript,
            type: 'question',
            confidence: event.results[i][0].confidence
          };
          
          setTranscript(prev => [...prev, entry]);
          setCurrentQuestion(transcript);
          
          // Save to backend
          try {
            await api.post(`/api/live-interview/sessions/${sessionId}/transcript`, {
              text: transcript,
              type: 'question',
              confidence: event.results[i][0].confidence
            });
            
            // Auto-generate AI answer
            generateAIAnswer(transcript);
          } catch (error) {
            console.error('Error saving transcript:', error);
          }
        } else {
          interimTranscript += transcript;
        }
      }
      
      if (interimTranscript) {
        setCurrentQuestion(interimTranscript);
      }
    };
    
    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      if (event.error === 'no-speech') {
        // Silently ignore no-speech errors
        return;
      }
      setError(`Speech recognition error: ${event.error}`);
    };
    
    recognition.onend = () => {
      if (isListening && sessionActive) {
        // Restart if still listening
        recognition.start();
      }
    };
    
    recognitionRef.current = recognition;
  };

  const toggleListening = () => {
    if (!sessionActive) return;
    
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
    } else {
      recognitionRef.current?.start();
      setIsListening(true);
      setError(null);
    }
  };

  const generateAIAnswer = async (question) => {
    if (!sessionId) return;
    
    setIsGeneratingAnswer(true);
    try {
      const response = await api.post(
        `/api/live-interview/sessions/${sessionId}/generate-answer`,
        { question: question, session_id: sessionId }
      );
      
      setAiAnswer(response.data);
    } catch (error) {
      console.error('Error generating answer:', error);
      setError('Failed to generate AI answer');
    } finally {
      setIsGeneratingAnswer(false);
    }
  };

  const endSession = async () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsListening(false);
    
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }
    
    if (sessionId) {
      try {
        await api.put(`/api/live-interview/sessions/${sessionId}/status`, {
          status: 'completed'
        });
        
        // Navigate to session analysis
        navigate(`/live-interview/session/${sessionId}/analysis`);
      } catch (error) {
        console.error('Error ending session:', error);
      }
    }
    
    setSessionActive(false);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Pre-session setup UI
  if (!sessionActive) {
    return (
      <div className="min-h-screen bg-secondary-50 py-8 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="card">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
                <Sparkles className="text-white" size={24} />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-secondary-900">Live Interview Assistant</h1>
                <p className="text-secondary-600">Real-time AI answers during your interview</p>
              </div>
            </div>

            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-3">
                <AlertCircle className="text-red-500 flex-shrink-0 mt-0.5" size={20} />
                <div>
                  <p className="text-red-800 font-medium">Error</p>
                  <p className="text-red-600 text-sm">{error}</p>
                </div>
              </div>
            )}

            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Session Title *
                </label>
                <input
                  type="text"
                  data-testid="session-title-input"
                  value={sessionTitle}
                  onChange={(e) => setSessionTitle(e.target.value)}
                  placeholder="e.g., Software Engineer Interview at Google"
                  className="input-field"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Resume Source *
                </label>
                <div className="space-y-3">
                  <div className="flex items-center space-x-4">
                    <label className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="radio"
                        name="resumeSource"
                        value="profile"
                        checked={resumeSource === 'profile'}
                        onChange={(e) => {
                          setResumeSource(e.target.value);
                          setSelectedResume('');
                        }}
                        className="w-4 h-4 text-primary-600 focus:ring-primary-500"
                      />
                      <span className="text-sm text-secondary-700">Use Profile Resume (Default)</span>
                    </label>
                    <label className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="radio"
                        name="resumeSource"
                        value="generated"
                        checked={resumeSource === 'generated'}
                        onChange={(e) => setResumeSource(e.target.value)}
                        className="w-4 h-4 text-primary-600 focus:ring-primary-500"
                      />
                      <span className="text-sm text-secondary-700">Use Generated Resume</span>
                    </label>
                  </div>
                  
                  {resumeSource === 'generated' && (
                    <select
                      value={selectedResume}
                      data-testid="resume-select"
                      onChange={(e) => setSelectedResume(e.target.value)}
                      className="input-field"
                    >
                      <option value="">Select a resume...</option>
                      {Array.isArray(resumes) && resumes.map(resume => (
                        <option key={resume.id} value={resume.id}>
                          {resume.title || 'Untitled Resume'} 
                          {resume.job_title && ` - ${resume.job_title}`}
                        </option>
                      ))}
                    </select>
                  )}
                </div>
                <p className="mt-1 text-sm text-secondary-500">
                  {resumeSource === 'profile' 
                    ? 'AI will use your raw profile data for answers' 
                    : 'AI will use optimized content from your selected resume'}
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Job Description (Optional)
                </label>
                <select
                  value={selectedJob}
                  data-testid="job-select"
                  onChange={(e) => setSelectedJob(e.target.value)}
                  className="input-field"
                >
                  <option value="">Select a job...</option>
                  {Array.isArray(jobs) && jobs.map(job => (
                    <option key={job.id} value={job.id}>
                      {job.title} at {job.company}
                    </option>
                  ))}
                </select>
                <p className="mt-1 text-sm text-secondary-500">
                  AI will tailor answers to this specific role
                </p>
              </div>

              <div className="bg-secondary-50 rounded-lg p-4">
                <button
                  onClick={() => setShowSettings(!showSettings)}
                  className="flex items-center justify-between w-full text-left"
                >
                  <div className="flex items-center space-x-2">
                    <Settings size={20} className="text-secondary-600" />
                    <span className="font-medium text-secondary-900">Advanced Settings</span>
                  </div>
                  {showSettings ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                </button>

                {showSettings && (
                  <div className="mt-4 space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-secondary-700 mb-2">
                        AI Model
                      </label>
                      <select
                        value={modelPreference}
                        onChange={(e) => setModelPreference(e.target.value)}
                        className="input-field"
                      >
                        <option value="gpt-4">GPT-4 (Fastest, Most Accurate)</option>
                        <option value="claude-sonnet">Claude Sonnet (Alternative)</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-secondary-700 mb-2">
                        Language
                      </label>
                      <select
                        value={language}
                        onChange={(e) => setLanguage(e.target.value)}
                        className="input-field"
                      >
                        <option value="en-US">English (US)</option>
                        <option value="en-GB">English (UK)</option>
                        <option value="es-ES">Spanish</option>
                        <option value="fr-FR">French</option>
                        <option value="de-DE">German</option>
                        <option value="zh-CN">Chinese</option>
                        <option value="ja-JP">Japanese</option>
                      </select>
                    </div>
                  </div>
                )}
              </div>

              <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
                <h3 className="font-medium text-primary-900 mb-2">How it works:</h3>
                <ul className="space-y-2 text-sm text-primary-800">
                  <li className="flex items-start space-x-2">
                    <Check size={16} className="flex-shrink-0 mt-0.5" />
                    <span>Start your video call (Zoom, Meet, Teams, etc.)</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <Check size={16} className="flex-shrink-0 mt-0.5" />
                    <span>Click "Start Session" and enable microphone access</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <Check size={16} className="flex-shrink-0 mt-0.5" />
                    <span>Keep this tab open - AI will transcribe questions and provide answers</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <Check size={16} className="flex-shrink-0 mt-0.5" />
                    <span>Read AI suggestions naturally in your own words</span>
                  </li>
                </ul>
              </div>

              <button
                onClick={startSession}
                data-testid="start-session-button"
                disabled={!sessionTitle.trim()}
                className="btn-primary w-full py-3 text-lg"
              >
                <Play size={20} className="mr-2" />
                Start Live Session
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Active session UI
  return (
    <div className="min-h-screen bg-secondary-50">
      {/* Header */}
      <div className="bg-white border-b border-secondary-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className={`w-3 h-3 rounded-full ${isListening ? 'bg-green-500 animate-pulse' : 'bg-secondary-300'}`} />
              <div>
                <h2 className="font-semibold text-secondary-900">{sessionTitle}</h2>
                <div className="flex items-center space-x-4 text-sm text-secondary-600">
                  <span className="flex items-center space-x-1">
                    <Clock size={14} />
                    <span>{formatTime(sessionTime)}</span>
                  </span>
                  <span className="flex items-center space-x-1">
                    <MessageSquare size={14} />
                    <span>{transcript.length} questions</span>
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <button
                onClick={toggleListening}
                data-testid="toggle-listening-button"
                className={`btn-icon ${isListening ? 'bg-green-500 hover:bg-green-600' : 'bg-secondary-500 hover:bg-secondary-600'}`}
              >
                {isListening ? <Mic size={20} /> : <MicOff size={20} />}
              </button>

              <button
                onClick={endSession}
                data-testid="end-session-button"
                className="btn-danger"
              >
                <Square size={16} className="mr-2" />
                End Session
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Transcript Panel */}
          <div className="lg:col-span-2 space-y-6">
            {/* Current Question */}
            {currentQuestion && (
              <div className="card bg-gradient-to-br from-primary-50 to-white border-2 border-primary-200">
                <div className="flex items-start space-x-3">
                  <div className="w-10 h-10 bg-primary-500 rounded-lg flex items-center justify-center flex-shrink-0">
                    <MessageSquare className="text-white" size={20} />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-medium text-secondary-900 mb-2">Current Question:</h3>
                    <p className="text-lg text-secondary-800">{currentQuestion}</p>
                  </div>
                </div>
              </div>
            )}

            {/* AI Answer */}
            {aiAnswer && (
              <div className="card bg-gradient-to-br from-green-50 to-white border-2 border-green-200">
                <div className="flex items-start space-x-3">
                  <div className="w-10 h-10 bg-green-500 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Brain className="text-white" size={20} />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-medium text-secondary-900">AI Suggested Answer:</h3>
                      <span className="text-xs text-secondary-500 bg-secondary-100 px-2 py-1 rounded">
                        {aiAnswer.model === 'gpt-4' ? 'GPT-4' : 'Claude'}
                      </span>
                    </div>
                    <p className="text-secondary-800 leading-relaxed">{aiAnswer.answer}</p>
                    {aiAnswer.context_used && aiAnswer.context_used.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-green-200">
                        <p className="text-xs text-secondary-600">
                          Based on: {aiAnswer.context_used.join(', ')}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {isGeneratingAnswer && (
              <div className="card bg-secondary-50 border-2 border-dashed border-secondary-300">
                <div className="flex items-center justify-center space-x-3 py-4">
                  <Loader className="animate-spin text-primary-500" size={24} />
                  <span className="text-secondary-600">Generating AI answer...</span>
                </div>
              </div>
            )}

            {/* Transcript History */}
            <div className="card">
              <h3 className="font-semibold text-secondary-900 mb-4">Transcript</h3>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {transcript.length === 0 ? (
                  <p className="text-center text-secondary-500 py-8">
                    {isListening ? 'Listening for questions...' : 'Start listening to see transcript'}
                  </p>
                ) : (
                  transcript.map((entry, index) => (
                    <div key={index} className="bg-secondary-50 rounded-lg p-3">
                      <div className="flex items-start justify-between mb-1">
                        <span className="text-xs text-secondary-500">
                          {new Date(entry.timestamp).toLocaleTimeString()}
                        </span>
                        {entry.confidence && (
                          <span className="text-xs text-secondary-500">
                            {Math.round(entry.confidence * 100)}% confident
                          </span>
                        )}
                      </div>
                      <p className="text-secondary-800">{entry.text}</p>
                    </div>
                  ))
                )}
                <div ref={transcriptEndRef} />
              </div>
            </div>
          </div>

          {/* Context Panel */}
          <div className="space-y-6">
            <div className="card">
              <button
                onClick={() => setShowContext(!showContext)}
                className="flex items-center justify-between w-full text-left mb-4"
              >
                <h3 className="font-semibold text-secondary-900">Your Context</h3>
                {showContext ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
              </button>

              {showContext && profile && (
                <div className="space-y-4 text-sm">
                  {profile.professional_summary && (
                    <div>
                      <h4 className="font-medium text-secondary-700 mb-1">Summary</h4>
                      <p className="text-secondary-600 line-clamp-3">{profile.professional_summary}</p>
                    </div>
                  )}

                  {profile.experience && profile.experience.length > 0 && (
                    <div>
                      <h4 className="font-medium text-secondary-700 mb-2">Recent Experience</h4>
                      <div className="space-y-2">
                        {profile.experience.slice(0, 2).map((exp, idx) => (
                          <div key={idx} className="bg-secondary-50 rounded p-2">
                            <p className="font-medium text-secondary-800">{exp.title}</p>
                            <p className="text-xs text-secondary-600">{exp.company}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {profile.skills && profile.skills.length > 0 && (
                    <div>
                      <h4 className="font-medium text-secondary-700 mb-2">Top Skills</h4>
                      <div className="flex flex-wrap gap-2">
                        {profile.skills.slice(0, 8).map((skill, idx) => (
                          <span key={idx} className="badge-secondary text-xs">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            <div className="card bg-primary-50 border border-primary-200">
              <h3 className="font-semibold text-primary-900 mb-3">Tips</h3>
              <ul className="space-y-2 text-sm text-primary-800">
                <li className="flex items-start space-x-2">
                  <Check size={14} className="flex-shrink-0 mt-0.5" />
                  <span>Speak AI answers naturally</span>
                </li>
                <li className="flex items-start space-x-2">
                  <Check size={14} className="flex-shrink-0 mt-0.5" />
                  <span>Add your personal touch</span>
                </li>
                <li className="flex items-start space-x-2">
                  <Check size={14} className="flex-shrink-0 mt-0.5" />
                  <span>Use examples from context</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveInterview;
