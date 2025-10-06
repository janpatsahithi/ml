// src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext.jsx';
import { NeedsProvider } from './context/NeedsContext.jsx'; 
import ChatPopup from './components/Chatpopup.jsx';

// Pages and Components (using .jsx extensions)
import Navbar from './components/Navbar.jsx'; 
import Home from './pages/Home.jsx';
import About from './pages/About.jsx';
import Auth from './pages/Auth.jsx';
import DonorDashboard from './pages/DonorDashboard.jsx';
import NGODashboard from './pages/NGODashboard.jsx';
import NotFound from './pages/NotFound.jsx';

// --- Helper for Protected Routes ---
const ProtectedRoute = ({ children, allowedRoles }) => {
  const { isLoggedIn, user } = useAuth();

  if (!isLoggedIn) {
    return <Navigate to="/auth" replace />;
  }
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }
  return children;
};
// ------------------------------------

const AppContent = () => {
    // Note: Navbar is outside the container to span full width
  return (
    <>
      <Navbar />
      {/* CRITICAL FIX: Changed <main> to <div> but kept the class for content width/padding */}
      <div className="container"> 
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/auth" element={<Auth />} />

          {/* Protected Dashboard Routes */}
          <Route
            path="/donor-dashboard"
            element={
              <ProtectedRoute allowedRoles={['Donor']}>
                <DonorDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/ngo-dashboard"
            element={
              <ProtectedRoute allowedRoles={['NGO']}>
                <NGODashboard />
              </ProtectedRoute>
            }
          />

          <Route path="*" element={<NotFound />} />
        </Routes>
      </div> 
      {/* ChatPopup remains outside the main content wrapper */}
      <ChatPopup /> 
    </>
  );
};


const App = () => {
  return (
    <Router>
      <AuthProvider>
        <NeedsProvider> 
          <AppContent />
        </NeedsProvider>
      </AuthProvider>
    </Router>
  );
};

export default App;