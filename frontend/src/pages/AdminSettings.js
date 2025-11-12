import React, { useState, useEffect } from 'react';
import { adminAPI } from '../services/api';
import { Settings, Save, Database, HardDrive, Cloud, CheckCircle, XCircle, Bot } from 'lucide-react';
import AISettings from './AISettings';
import DataManagement from './DataManagement';

const AdminSettings = () => {
  const [activeTab, setActiveTab] = useState('storage');
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');

  useEffect(() => {
    if (activeTab === 'storage') {
      fetchSettings();
    }
  }, [activeTab]);

  const fetchSettings = async () => {
    try {
      const response = await adminAPI.getStorageSettings();
      setSettings(response.data);
    } catch (error) {
      console.error('Error fetching settings:', error);
      setMessage('Error loading settings');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage('');
    
    try {
      const updateData = {
        storage_type: settings.storage_type,
        local_storage_path: settings.local_storage_path,
        s3_bucket_name: settings.s3_bucket_name,
        s3_region: settings.s3_region,
        aws_access_key_id: settings.aws_access_key_id,
        aws_secret_access_key: settings.aws_secret_access_key,
        max_file_size_mb: settings.max_file_size_mb
      };

      await adminAPI.updateStorageSettings(updateData);
      setMessage('Settings updated successfully! Changes will take effect immediately.');
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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="inline-block w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="mt-4 text-secondary-600">Loading settings...</p>
        </div>
      </div>
    );
  }

  // If AI tab is active, render AISettings component
  if (activeTab === 'ai') {
    return <AISettings />;
  }

  // If Data Management tab is active, render DataManagement component
  if (activeTab === 'data') {
    return <DataManagement />;
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-secondary-900 flex items-center space-x-2">
            <Settings size={32} />
            <span>Admin Settings</span>
          </h1>
          <p className="text-secondary-600 mt-1">Configure application settings and integrations</p>
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

      {/* Tabs */}
      <div className="mb-6 border-b border-secondary-200">
        <div className="flex space-x-8 overflow-x-auto">
          <button
            onClick={() => setActiveTab('storage')}
            className={`pb-4 px-1 border-b-2 font-medium text-sm transition-colors whitespace-nowrap ${
              activeTab === 'storage'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-secondary-600 hover:text-secondary-900 hover:border-secondary-300'
            }`}
          >
            <div className="flex items-center space-x-2">
              <HardDrive size={18} />
              <span>Storage</span>
            </div>
          </button>
          <button
            onClick={() => setActiveTab('ai')}
            className={`pb-4 px-1 border-b-2 font-medium text-sm transition-colors whitespace-nowrap ${
              activeTab === 'ai'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-secondary-600 hover:text-secondary-900 hover:border-secondary-300'
            }`}
          >
            <div className="flex items-center space-x-2">
              <Bot size={18} />
              <span>AI Integrations</span>
            </div>
          </button>
          <button
            onClick={() => setActiveTab('data')}
            className={`pb-4 px-1 border-b-2 font-medium text-sm transition-colors whitespace-nowrap ${
              activeTab === 'data'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-secondary-600 hover:text-secondary-900 hover:border-secondary-300'
            }`}
          >
            <div className="flex items-center space-x-2">
              <Database size={18} />
              <span>Data Management</span>
            </div>
          </button>
        </div>
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

      {/* Storage Configuration */}
      <div className="card space-y-6">
        <div>
          <h2 className="text-xl font-semibold text-secondary-900 mb-2">Storage Configuration</h2>
          <p className="text-sm text-secondary-600">
            Configure where uploaded files (certificates, resumes) are stored
          </p>
        </div>

        {/* Storage Type Selection */}
        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-3">
            Storage Type *
          </label>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Local Storage */}
            <div
              onClick={() => setSettings({ ...settings, storage_type: 'local' })}
              className={`cursor-pointer border-2 rounded-lg p-4 transition-all ${
                settings.storage_type === 'local'
                  ? 'border-primary-600 bg-primary-50'
                  : 'border-secondary-200 hover:border-primary-300'
              }`}
            >
              <div className="flex items-center space-x-3 mb-2">
                <HardDrive 
                  size={24} 
                  className={settings.storage_type === 'local' ? 'text-primary-600' : 'text-secondary-600'} 
                />
                <h3 className="font-semibold text-secondary-900">Local Storage</h3>
              </div>
              <p className="text-sm text-secondary-600">Store files on server disk</p>
            </div>

            {/* S3 Storage */}
            <div
              onClick={() => setSettings({ ...settings, storage_type: 's3' })}
              className={`cursor-pointer border-2 rounded-lg p-4 transition-all ${
                settings.storage_type === 's3'
                  ? 'border-primary-600 bg-primary-50'
                  : 'border-secondary-200 hover:border-primary-300'
              }`}
            >
              <div className="flex items-center space-x-3 mb-2">
                <Cloud 
                  size={24} 
                  className={settings.storage_type === 's3' ? 'text-primary-600' : 'text-secondary-600'} 
                />
                <h3 className="font-semibold text-secondary-900">AWS S3</h3>
              </div>
              <p className="text-sm text-secondary-600">Store files in S3 bucket</p>
            </div>

            {/* Database Storage */}
            <div
              onClick={() => setSettings({ ...settings, storage_type: 'database' })}
              className={`cursor-pointer border-2 rounded-lg p-4 transition-all ${
                settings.storage_type === 'database'
                  ? 'border-primary-600 bg-primary-50'
                  : 'border-secondary-200 hover:border-primary-300'
              }`}
            >
              <div className="flex items-center space-x-3 mb-2">
                <Database 
                  size={24} 
                  className={settings.storage_type === 'database' ? 'text-primary-600' : 'text-secondary-600'} 
                />
                <h3 className="font-semibold text-secondary-900">Database</h3>
              </div>
              <p className="text-sm text-secondary-600">Store as base64 in DB</p>
            </div>
          </div>
        </div>

        {/* Local Storage Settings */}
        {settings.storage_type === 'local' && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-4">
            <h3 className="font-semibold text-blue-900 flex items-center space-x-2">
              <HardDrive size={18} />
              <span>Local Storage Configuration</span>
            </h3>
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">
                Storage Path *
              </label>
              <input
                type="text"
                value={settings.local_storage_path || ''}
                onChange={(e) => setSettings({ ...settings, local_storage_path: e.target.value })}
                className="input-field"
                placeholder="/app/uploads"
              />
              <p className="text-xs text-secondary-500 mt-1">
                Absolute path where files will be stored on the server
              </p>
            </div>
          </div>
        )}

        {/* S3 Storage Settings */}
        {settings.storage_type === 's3' && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-4">
            <h3 className="font-semibold text-blue-900 flex items-center space-x-2">
              <Cloud size={18} />
              <span>AWS S3 Configuration</span>
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  S3 Bucket Name *
                </label>
                <input
                  type="text"
                  value={settings.s3_bucket_name || ''}
                  onChange={(e) => setSettings({ ...settings, s3_bucket_name: e.target.value })}
                  className="input-field"
                  placeholder="my-bucket-name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  AWS Region *
                </label>
                <select
                  value={settings.s3_region || 'us-east-1'}
                  onChange={(e) => setSettings({ ...settings, s3_region: e.target.value })}
                  className="input-field"
                >
                  <option value="us-east-1">US East (N. Virginia)</option>
                  <option value="us-east-2">US East (Ohio)</option>
                  <option value="us-west-1">US West (N. California)</option>
                  <option value="us-west-2">US West (Oregon)</option>
                  <option value="eu-west-1">EU (Ireland)</option>
                  <option value="eu-central-1">EU (Frankfurt)</option>
                  <option value="ap-south-1">Asia Pacific (Mumbai)</option>
                  <option value="ap-southeast-1">Asia Pacific (Singapore)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  AWS Access Key ID *
                </label>
                <input
                  type="text"
                  value={settings.aws_access_key_id || ''}
                  onChange={(e) => setSettings({ ...settings, aws_access_key_id: e.target.value })}
                  className="input-field"
                  placeholder="AKIAIOSFODNN7EXAMPLE"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  AWS Secret Access Key *
                </label>
                <input
                  type="password"
                  value={settings.aws_secret_access_key || ''}
                  onChange={(e) => setSettings({ ...settings, aws_secret_access_key: e.target.value })}
                  className="input-field"
                  placeholder="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
                />
              </div>
            </div>
            <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
              <p className="text-sm text-yellow-800">
                <strong>Note:</strong> Ensure your S3 bucket has proper permissions and CORS configuration for file uploads.
              </p>
            </div>
          </div>
        )}

        {/* Database Storage Settings */}
        {settings.storage_type === 'database' && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-4">
            <h3 className="font-semibold text-blue-900 flex items-center space-x-2">
              <Database size={18} />
              <span>Database Storage Configuration</span>
            </h3>
            <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
              <p className="text-sm text-yellow-800">
                <strong>Note:</strong> Files will be stored as base64-encoded strings in MongoDB. 
                This is suitable for small files but may impact database performance with large files.
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">
                Max File Size (MB)
              </label>
              <input
                type="number"
                value={settings.max_file_size_mb || 10}
                onChange={(e) => setSettings({ ...settings, max_file_size_mb: parseInt(e.target.value) })}
                className="input-field"
                min="1"
                max="50"
              />
              <p className="text-xs text-secondary-500 mt-1">
                Maximum file size for database storage (recommended: 10MB or less)
              </p>
            </div>
          </div>
        )}

        {/* General Settings */}
        <div className="border-t pt-6">
          <h3 className="font-semibold text-secondary-900 mb-4">General Settings</h3>
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              Maximum File Size (MB)
            </label>
            <input
              type="number"
              value={settings.max_file_size_mb || 10}
              onChange={(e) => setSettings({ ...settings, max_file_size_mb: parseInt(e.target.value) })}
              className="input-field max-w-xs"
              min="1"
              max="100"
            />
            <p className="text-xs text-secondary-500 mt-1">
              Maximum size for uploaded files (certificates, resumes)
            </p>
          </div>
        </div>
      </div>

      {/* Current Configuration Status */}
      <div className="card mt-6">
        <h3 className="font-semibold text-secondary-900 mb-4">Current Configuration</h3>
        <div className="bg-secondary-50 rounded-lg p-4 space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-secondary-600">Storage Type:</span>
            <span className="font-medium text-secondary-900 capitalize">{settings.storage_type}</span>
          </div>
          {settings.storage_type === 'local' && (
            <div className="flex justify-between">
              <span className="text-secondary-600">Storage Path:</span>
              <span className="font-medium text-secondary-900">{settings.local_storage_path}</span>
            </div>
          )}
          {settings.storage_type === 's3' && (
            <>
              <div className="flex justify-between">
                <span className="text-secondary-600">S3 Bucket:</span>
                <span className="font-medium text-secondary-900">{settings.s3_bucket_name || 'Not configured'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-secondary-600">Region:</span>
                <span className="font-medium text-secondary-900">{settings.s3_region}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-secondary-600">S3 Configured:</span>
                <span className={`font-medium ${settings.s3_configured ? 'text-green-600' : 'text-red-600'}`}>
                  {settings.s3_configured ? 'Yes' : 'No'}
                </span>
              </div>
            </>
          )}
          <div className="flex justify-between">
            <span className="text-secondary-600">Max File Size:</span>
            <span className="font-medium text-secondary-900">{settings.max_file_size_mb} MB</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminSettings;
