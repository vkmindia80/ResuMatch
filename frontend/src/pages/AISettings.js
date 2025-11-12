import React, { useState, useEffect } from 'react';
import { adminAPI } from '../services/api';
import { 
  Save, Bot, CheckCircle, XCircle, 
  AlertCircle, Zap, Eye, EyeOff, ToggleLeft, ToggleRight 
} from 'lucide-react';

const AISettings = () => {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const [showKeys, setShowKeys] = useState({});

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await adminAPI.getAISettings();
      setSettings(response.data);
    } catch (error) {
      console.error('Error fetching AI settings:', error);
      setMessage('Error loading AI settings');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage('');
    
    try {
      await adminAPI.updateAISettings(settings);
      setMessage('AI settings updated successfully! Changes will be applied immediately.');
      setMessageType('success');
      
      setTimeout(() => {
        setMessage('');
        setMessageType('');
      }, 5000);
    } catch (error) {
      setMessage('Error saving settings: ' + (error.response?.data?.detail || error.message));
      setMessageType('error');
    } finally {
      setSaving(false);
    }
  };

  const toggleProvider = (provider) => {
    setSettings({
      ...settings,
      [provider]: {
        ...settings[provider],
        enabled: !settings[provider]?.enabled
      }
    });
  };

  const updateProviderKey = (provider, key) => {
    setSettings({
      ...settings,
      [provider]: {
        ...settings[provider],
        api_key: key
      }
    });
  };

  const updateFeatureConfig = (feature, field, value) => {
    setSettings({
      ...settings,
      [feature]: {
        ...settings[feature],
        [field]: value
      }
    });
  };

  const toggleShowKey = (provider) => {
    setShowKeys({
      ...showKeys,
      [provider]: !showKeys[provider]
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="inline-block w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="mt-4 text-secondary-600">Loading AI settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-secondary-900 flex items-center space-x-2">
            <Bot size={32} className="text-primary-600" />
            <span>AI Integration Settings</span>
          </h1>
          <p className="text-secondary-600 mt-1">Configure AI providers and models for different features</p>
        </div>
        <button
          onClick={handleSave}
          disabled={saving}
          className="btn-primary flex items-center space-x-2"
        >
          <Save size={18} />
          <span>{saving ? 'Saving...' : 'Save Changes'}</span>
        </button>
      </div>

      {/* Message */}
      {message && (
        <div className={`mb-6 p-4 rounded-lg flex items-center space-x-3 ${
          messageType === 'success' 
            ? 'bg-green-50 border border-green-200' 
            : 'bg-red-50 border border-red-200'
        }`}>
          {messageType === 'success' ? (
            <CheckCircle className="text-green-600" size={24} />
          ) : (
            <XCircle className="text-red-600" size={24} />
          )}
          <span className={messageType === 'success' ? 'text-green-700' : 'text-red-700'}>
            {message}
          </span>
        </div>
      )}

      {/* Emergent LLM Key Info */}
      <div className="card mb-6 bg-gradient-to-r from-primary-50 to-blue-50 border-2 border-primary-200">
        <div className="flex items-start space-x-3">
          <Zap className="text-primary-600 flex-shrink-0 mt-1" size={24} />
          <div>
            <h3 className="font-semibold text-primary-900 mb-2">Emergent Universal LLM Key</h3>
            <p className="text-sm text-primary-800 mb-3">
              The Emergent LLM Key is a universal key that works across OpenAI, Anthropic, and Google AI providers. 
              It's enabled by default for all users.
            </p>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setSettings({ ...settings, use_emergent_key: !settings.use_emergent_key })}
                className="flex items-center space-x-2"
              >
                {settings?.use_emergent_key ? (
                  <ToggleRight className="text-green-600" size={32} />
                ) : (
                  <ToggleLeft className="text-secondary-400" size={32} />
                )}
                <span className="text-sm font-medium text-secondary-700">
                  {settings?.use_emergent_key ? 'Enabled' : 'Disabled'}
                </span>
              </button>
            </div>
            <p className="text-xs text-secondary-600 mt-2">
              When enabled, users can use Emergent LLM Key as default. They can still add their own keys as overrides.
            </p>
          </div>
        </div>
      </div>

      {/* AI Providers Configuration */}
      <div className="card mb-6">
        <h2 className="text-xl font-semibold text-secondary-900 mb-4">AI Provider Configuration</h2>
        <p className="text-sm text-secondary-600 mb-6">
          Configure API keys for different AI providers. Users can override these with their own keys.
        </p>

        <div className="space-y-6">
          {/* OpenAI */}
          <div className="border border-secondary-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                  <Bot size={20} className="text-green-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-secondary-900">OpenAI</h3>
                  <p className="text-xs text-secondary-600">GPT-4, GPT-4o, GPT-3.5 Turbo</p>
                </div>
              </div>
              <button
                onClick={() => toggleProvider('openai')}
                className="flex items-center space-x-2"
              >
                {settings?.openai?.enabled ? (
                  <ToggleRight className="text-green-600" size={32} />
                ) : (
                  <ToggleLeft className="text-secondary-400" size={32} />
                )}
              </button>
            </div>

            {settings?.openai?.enabled && (
              <div className="space-y-3 pl-13">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    API Key
                  </label>
                  <div className="relative">
                    <input
                      type={showKeys.openai ? 'text' : 'password'}
                      value={settings?.openai?.api_key || ''}
                      onChange={(e) => updateProviderKey('openai', e.target.value)}
                      className="input-field pr-10"
                      placeholder="sk-..."
                    />
                    <button
                      onClick={() => toggleShowKey('openai')}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-secondary-500 hover:text-secondary-700"
                    >
                      {showKeys.openai ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                  <p className="text-xs text-secondary-500 mt-1">
                    Admin default API key for OpenAI services
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Default Model
                  </label>
                  <select
                    value={settings?.openai?.default_model || 'gpt-4o'}
                    onChange={(e) => setSettings({
                      ...settings,
                      openai: { ...settings.openai, default_model: e.target.value }
                    })}
                    className="input-field"
                  >
                    <option value="gpt-4o">GPT-4o (Latest, Fastest)</option>
                    <option value="gpt-4">GPT-4 (Most Capable)</option>
                    <option value="gpt-4-turbo">GPT-4 Turbo</option>
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo (Budget)</option>
                  </select>
                </div>
              </div>
            )}
          </div>

          {/* Anthropic */}
          <div className="border border-secondary-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                  <Bot size={20} className="text-purple-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-secondary-900">Anthropic Claude</h3>
                  <p className="text-xs text-secondary-600">Claude Sonnet, Claude Opus</p>
                </div>
              </div>
              <button
                onClick={() => toggleProvider('anthropic')}
                className="flex items-center space-x-2"
              >
                {settings?.anthropic?.enabled ? (
                  <ToggleRight className="text-green-600" size={32} />
                ) : (
                  <ToggleLeft className="text-secondary-400" size={32} />
                )}
              </button>
            </div>

            {settings?.anthropic?.enabled && (
              <div className="space-y-3 pl-13">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    API Key
                  </label>
                  <div className="relative">
                    <input
                      type={showKeys.anthropic ? 'text' : 'password'}
                      value={settings?.anthropic?.api_key || ''}
                      onChange={(e) => updateProviderKey('anthropic', e.target.value)}
                      className="input-field pr-10"
                      placeholder="sk-ant-..."
                    />
                    <button
                      onClick={() => toggleShowKey('anthropic')}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-secondary-500 hover:text-secondary-700"
                    >
                      {showKeys.anthropic ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                  <p className="text-xs text-secondary-500 mt-1">
                    Admin default API key for Anthropic services
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Default Model
                  </label>
                  <select
                    value={settings?.anthropic?.default_model || 'claude-sonnet-4-20250514'}
                    onChange={(e) => setSettings({
                      ...settings,
                      anthropic: { ...settings.anthropic, default_model: e.target.value }
                    })}
                    className="input-field"
                  >
                    <option value="claude-4-sonnet-20250514">Claude 4 Sonnet (Balanced)</option>
                    <option value="claude-opus-4-20250514">Claude 4 Opus (Most Capable)</option>
                    <option value="claude-3.5-sonnet">Claude 3.5 Sonnet</option>
                  </select>
                </div>
              </div>
            )}
          </div>

          {/* Google */}
          <div className="border border-secondary-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Bot size={20} className="text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-secondary-900">Google AI</h3>
                  <p className="text-xs text-secondary-600">Gemini Pro, Gemini Flash</p>
                </div>
              </div>
              <button
                onClick={() => toggleProvider('google')}
                className="flex items-center space-x-2"
              >
                {settings?.google?.enabled ? (
                  <ToggleRight className="text-green-600" size={32} />
                ) : (
                  <ToggleLeft className="text-secondary-400" size={32} />
                )}
              </button>
            </div>

            {settings?.google?.enabled && (
              <div className="space-y-3 pl-13">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    API Key
                  </label>
                  <div className="relative">
                    <input
                      type={showKeys.google ? 'text' : 'password'}
                      value={settings?.google?.api_key || ''}
                      onChange={(e) => updateProviderKey('google', e.target.value)}
                      className="input-field pr-10"
                      placeholder="AIza..."
                    />
                    <button
                      onClick={() => toggleShowKey('google')}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-secondary-500 hover:text-secondary-700"
                    >
                      {showKeys.google ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                  <p className="text-xs text-secondary-500 mt-1">
                    Admin default API key for Google AI services
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Default Model
                  </label>
                  <select
                    value={settings?.google?.default_model || 'gemini-2.0-pro'}
                    onChange={(e) => setSettings({
                      ...settings,
                      google: { ...settings.google, default_model: e.target.value }
                    })}
                    className="input-field"
                  >
                    <option value="gemini-2.0-pro">Gemini 2.0 Pro (Latest)</option>
                    <option value="gemini-pro">Gemini Pro</option>
                    <option value="gemini-flash">Gemini Flash (Fast)</option>
                  </select>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Per-Feature Configuration */}
      <div className="card">
        <h2 className="text-xl font-semibold text-secondary-900 mb-4">Feature-Specific AI Configuration</h2>
        <p className="text-sm text-secondary-600 mb-6">
          Configure which AI provider and model to use for each feature
        </p>

        <div className="space-y-4">
          {[
            { key: 'resume_generation', label: 'Resume Generation', desc: 'AI-powered resume optimization and generation' },
            { key: 'interview_prep', label: 'Interview Preparation', desc: 'Interview question generation and answers' },
            { key: 'cover_letter', label: 'Cover Letters', desc: 'Personalized cover letter generation' },
            { key: 'live_interview', label: 'Live Interview Assistant', desc: 'Real-time interview answer generation' },
            { key: 'ats_optimization', label: 'ATS Optimization', desc: 'Resume ATS scoring and optimization' }
          ].map((feature) => (
            <div key={feature.key} className="border border-secondary-200 rounded-lg p-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="font-medium text-secondary-900">{feature.label}</h3>
                  <p className="text-xs text-secondary-600 mb-3">{feature.desc}</p>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-medium text-secondary-700 mb-1">
                        Provider
                      </label>
                      <select
                        value={settings?.[feature.key]?.provider || 'emergent'}
                        onChange={(e) => updateFeatureConfig(feature.key, 'provider', e.target.value)}
                        className="input-field text-sm"
                      >
                        <option value="emergent">Emergent LLM Key</option>
                        <option value="openai">OpenAI</option>
                        <option value="anthropic">Anthropic</option>
                        <option value="google">Google AI</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-secondary-700 mb-1">
                        Model
                      </label>
                      <input
                        type="text"
                        value={settings?.[feature.key]?.model || 'gpt-4o'}
                        onChange={(e) => updateFeatureConfig(feature.key, 'model', e.target.value)}
                        className="input-field text-sm"
                        placeholder="e.g., gpt-4o"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Info Box */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <AlertCircle className="text-blue-600 flex-shrink-0 mt-0.5" size={20} />
          <div className="text-sm text-blue-800">
            <p className="font-medium mb-1">Admin Settings vs User Settings</p>
            <ul className="list-disc list-inside space-y-1">
              <li>These are <strong>admin default settings</strong> that apply to all users</li>
              <li>Users can override these settings with their own API keys in their profile</li>
              <li>User settings always take priority over admin defaults</li>
              <li>If user has no custom settings, admin defaults are used</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AISettings;
