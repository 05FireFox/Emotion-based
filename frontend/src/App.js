import React, { useState } from 'react';
import Main from './Main.js';
import LandingPage from './LandingPage';
import Login from './components/Login'; 
import Register from './components/Register'; 
import './App.css'; 

import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { AnimatePresence, motion } from 'framer-motion';

const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#2D2D2D' },
    secondary: { main: '#007BFF' },
    background: { default: '#F9F9F9', paper: '#ffffff' },
    text: { primary: '#2D2D2D', secondary: 'rgba(45, 45, 45, 0.7)' },
  },
  typography: { fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif' },
});

function App() {
  // Start directly on the 'main' view without asking for credentials
  const [currentView, setCurrentView] = useState('main'); 
  
  // Automatically provide a default user profile so no credentials are needed
  const [currentUser, setCurrentUser] = useState({
    user_id: "guest_user",
    name: "Guest User",
    email: "guest@emotionsense.com",
    phone: "0000000000"
  });

  // If someone clicks logout, this brings them back to a clean guest state instead of a login form
  const handleLogout = () => {
    setCurrentUser({
      user_id: "guest_user",
      name: "Guest User",
      email: "guest@emotionsense.com",
      phone: "0000000000"
    });
    setCurrentView('main');
  };

  return (
    <ThemeProvider theme={lightTheme}>
      <CssBaseline />
      <AnimatePresence mode="wait">
        
        {/* Main App (Camera & Recommendations) loads instantly */}
        {currentView === 'main' && (
          <motion.div
            key="main"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1 }}
          >
            <Main currentUser={currentUser} onLogout={handleLogout} />
          </motion.div>
        )}

      </AnimatePresence>
    </ThemeProvider>
  );
}

export default App;
