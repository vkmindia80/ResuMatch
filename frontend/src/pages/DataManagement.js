import React, { useState } from 'react';
import { adminAPI } from '../services/api';
import { Database, Trash2, CheckCircle, XCircle, AlertTriangle, RefreshCw } from 'lucide-react';

const DataManagement = () => {
  const [generatingData, setGeneratingData] = useState(false);
  const [clearingData, setClearingData] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const [generationResult, setGenerationResult] = useState(null);
  const [clearResult, setClearResult] = useState(null);
  const [targetEmail, setTargetEmail] = useState('demo@resumatch.com');
  const [showClearConfirm, setShowClearConfirm] = useState(false);

  const generateSampleData = async () => {
    setGeneratingData(true);
    setMessage('');
    setGenerationResult(null);
    
    try {
      const response = await adminAPI.generateSampleData({
        target_user_email: targetEmail
      });
      
      if (response.data.success) {
        setGenerationResult(response.data.created);
        setMessage(`Successfully generated ${response.data.total_items} items for ${response.data.user_email}`);
        setMessageType('success');
      }
    } catch (error) {
      setMessage('Error generating sample data: ' + (error.response?.data?.detail || error.message));
      setMessageType('error');
    } finally {
      setGeneratingData(false);
    }
  };

  const clearSampleData = async () => {
    setClearingData(true);
    setMessage('');
    setClearResult(null);
    
    try {
      const response = await adminAPI.clearSampleData({
        target_user_email: targetEmail
      });
      
      if (response.data.success) {
        setClearResult(response.data.deleted);
        setMessage(`Successfully cleared ${response.data.total_items} items for ${response.data.user_email}`);
        setMessageType('success');
        setGenerationResult(null);
      }
    } catch (error) {
      setMessage('Error clearing sample data: ' + (error.response?.data?.detail || error.message));
      setMessageType('error');
    } finally {
      setClearingData(false);
      setShowClearConfirm(false);
    }
  };

  const handleClearClick = () => {
    setShowClearConfirm(true);
  };

  const handleCancelClear = () => {
    setShowClearConfirm(false);
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-secondary-900 flex items-center space-x-2">
          <Database size={32} className="text-primary-600" />
          <span>Data Management</span>
        </h1>
        <p className="text-secondary-600 mt-1">Generate or clear sample data for testing and demonstration</p>
      </div>

      {/* Message */}
      {message && (
        <div className={`mb-6 p-4 rounded-lg flex items-center space-x-3 ${
          messageType === 'success' 
            ? 'bg-green-50 border border-green-200' 
            : 'bg-red-50 border border-red-200'
        }`}>
          {messageType === 'success' ? (
            <CheckCircle className="text-green-600 flex-shrink-0" size={24} />
          ) : (
            <XCircle className="text-red-600 flex-shrink-0" size={24} />
          )}
          <span className={messageType === 'success' ? 'text-green-700' : 'text-red-700'}>
            {message}
          </span>
        </div>
      )}

      {/* Target User Email */}
      <div className="card mb-6">
        <h2 className="text-xl font-semibold text-secondary-900 mb-4">Target User</h2>
        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-2">
            User Email
          </label>
          <input
            type="email"
            value={targetEmail}
            onChange={(e) => setTargetEmail(e.target.value)}
            className="input-field max-w-md"
            placeholder="user@example.com"
          />
          <p className="text-xs text-secondary-500 mt-2">
            Enter the email of the user account where data should be generated or cleared.
            Default: demo@resumatch.com
          </p>
        </div>
      </div>

      {/* Generate Sample Data */}
      <div className="card mb-6">
        <div className="flex items-start space-x-4">
          <div className="flex-shrink-0">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <Database className="text-green-600" size={24} />
            </div>
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-semibold text-secondary-900 mb-2">Generate Sample Data</h2>
            <p className="text-sm text-secondary-600 mb-4">
              Populate the selected user account with comprehensive sample data including:
            </p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4 text-sm text-secondary-700">
              <div className="flex items-center space-x-2">
                <CheckCircle size={16} className="text-green-600" />
                <span>Profile Data</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle size={16} className="text-green-600" />
                <span>Job Descriptions</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle size={16} className="text-green-600" />
                <span>Resumes</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle size={16} className="text-green-600" />
                <span>Cover Letters</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle size={16} className="text-green-600" />
                <span>Interview Prep</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle size={16} className="text-green-600" />
                <span>Practice Sessions</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle size={16} className="text-green-600" />
                <span>Live Sessions</span>
              </div>
            </div>

            {generationResult && (
              <div className="mb-4 bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-3">
                  <CheckCircle size={20} className="text-green-600" />
                  <span className="font-semibold text-green-900">Generated Items:</span>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm text-green-900">
                  <div>✓ Profiles: {generationResult.profiles}</div>
                  <div>✓ Jobs: {generationResult.job_descriptions}</div>
                  <div>✓ Resumes: {generationResult.resumes}</div>
                  <div>✓ Questions: {generationResult.interview_questions}</div>
                  <div>✓ Cover Letters: {generationResult.cover_letters}</div>
                  <div>✓ Practice: {generationResult.practice_sessions}</div>
                  <div className="col-span-2">✓ Live Sessions: {generationResult.live_interview_sessions}</div>
                </div>
              </div>
            )}

            <button
              onClick={generateSampleData}
              disabled={generatingData || !targetEmail}
              className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {generatingData ? (
                <>
                  <RefreshCw size={18} className="animate-spin" />
                  <span>Generating Sample Data...</span>
                </>
              ) : (
                <>
                  <Database size={18} />
                  <span>Generate Sample Data</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Clear Sample Data */}
      <div className="card border-2 border-red-100">
        <div className="flex items-start space-x-4">
          <div className="flex-shrink-0">
            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
              <Trash2 className="text-red-600" size={24} />
            </div>
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-semibold text-secondary-900 mb-2">Clear Sample Data</h2>
            <p className="text-sm text-secondary-600 mb-4">
              Remove all data for the selected user including profiles, jobs, resumes, cover letters, interview prep, and sessions.
            </p>

            <div className="mb-4 bg-yellow-50 border border-yellow-200 rounded-lg p-3 flex items-start space-x-2">
              <AlertTriangle className="text-yellow-600 flex-shrink-0 mt-0.5" size={18} />
              <p className="text-sm text-yellow-800">
                <strong>Warning:</strong> This action is permanent and cannot be undone. All data for the user will be deleted.
              </p>
            </div>

            {clearResult && (
              <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-3">
                  <CheckCircle size={20} className="text-red-600" />
                  <span className="font-semibold text-red-900">Deleted Items:</span>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm text-red-900">
                  <div>✓ Profiles: {clearResult.profiles}</div>
                  <div>✓ Jobs: {clearResult.job_descriptions}</div>
                  <div>✓ Resumes: {clearResult.resumes}</div>
                  <div>✓ Questions: {clearResult.interview_questions}</div>
                  <div>✓ Cover Letters: {clearResult.cover_letters}</div>
                  <div>✓ Practice: {clearResult.practice_sessions}</div>
                  <div>✓ Live Sessions: {clearResult.live_interview_sessions}</div>
                  <div>✓ Transcripts: {clearResult.interview_transcripts}</div>
                </div>
              </div>
            )}

            {!showClearConfirm ? (
              <button
                onClick={handleClearClick}
                disabled={clearingData || !targetEmail}
                className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Trash2 size={18} />
                <span>Clear All Data</span>
              </button>
            ) : (
              <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4">
                <p className="text-sm font-semibold text-red-900 mb-3">
                  Are you absolutely sure? This will permanently delete all data for {targetEmail}.
                </p>
                <div className="flex items-center space-x-3">
                  <button
                    onClick={clearSampleData}
                    disabled={clearingData}
                    className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {clearingData ? (
                      <>
                        <RefreshCw size={18} className="animate-spin" />
                        <span>Clearing Data...</span>
                      </>
                    ) : (
                      <>
                        <Trash2 size={18} />
                        <span>Yes, Clear All Data</span>
                      </>
                    )}
                  </button>
                  <button
                    onClick={handleCancelClear}
                    disabled={clearingData}
                    className="bg-secondary-200 hover:bg-secondary-300 text-secondary-900 font-medium py-2 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Information */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <Database className="text-blue-600 flex-shrink-0 mt-0.5" size={20} />
          <div className="text-sm text-blue-800">
            <p className="font-medium mb-1">About Data Management</p>
            <ul className="list-disc list-inside space-y-1">
              <li>Sample data is useful for testing and demonstrations</li>
              <li>Generated data includes realistic profiles across multiple industries</li>
              <li>You can generate data multiple times (existing data won't be duplicated)</li>
              <li>Clearing data is permanent and cannot be undone</li>
              <li>Use the demo account (demo@resumatch.com) for testing</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DataManagement;
