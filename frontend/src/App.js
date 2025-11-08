import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import JobDescriptions from './pages/JobDescriptions';
import Resumes from './pages/Resumes';
import InterviewPrep from './pages/InterviewPrep';
import CoverLetters from './pages/CoverLetters';
import PracticeSessions from './pages/PracticeSessions';
import ResumeIntelligence from './pages/ResumeIntelligence';
import AdminSettings from './pages/AdminSettings';
import Navbar from './components/Navbar';
import Loading from './components/Loading';
import './App.css';

function App() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <Loading />;
  }

  return (
    <Router>
      <div className="min-h-screen bg-secondary-50">
        {isAuthenticated && <Navbar />}
        <Routes>
          <Route path="/" element={isAuthenticated ? <Navigate to="/dashboard" /> : <Landing />} />
          <Route path="/login" element={isAuthenticated ? <Navigate to="/dashboard" /> : <Login />} />
          <Route path="/register" element={isAuthenticated ? <Navigate to="/dashboard" /> : <Register />} />
          
          <Route path="/dashboard" element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" />} />
          <Route path="/profile" element={isAuthenticated ? <Profile /> : <Navigate to="/login" />} />
          <Route path="/jobs" element={isAuthenticated ? <JobDescriptions /> : <Navigate to="/login" />} />
          <Route path="/resumes" element={isAuthenticated ? <Resumes /> : <Navigate to="/login" />} />
          <Route path="/resume-intelligence" element={isAuthenticated ? <ResumeIntelligence /> : <Navigate to="/login" />} />
          <Route path="/cover-letters" element={isAuthenticated ? <CoverLetters /> : <Navigate to="/login" />} />
          <Route path="/interview-prep" element={isAuthenticated ? <InterviewPrep /> : <Navigate to="/login" />} />
          <Route path="/practice-sessions" element={isAuthenticated ? <PracticeSessions /> : <Navigate to="/login" />} />
          <Route path="/admin/settings" element={isAuthenticated ? <AdminSettings /> : <Navigate to="/login" />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
