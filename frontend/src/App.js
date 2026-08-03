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
    primary: {
      main: '#2D2D2D',
    },
    secondary: {
      main: '#007BFF',
    },
    background: {
      default: '#F9F9F9',
      paper: '#ffffff',
    },
    text: {
      primary: '#2D2D2D',
      secondary: 'rgba(45, 45, 45, 0.7)',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  },
  components: {
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-notchedOutline': {
            borderColor: 'rgba(45, 45, 45, 0.3)',
          },
          '&:hover .MuiOutlinedInput-notchedOutline': {
            borderColor: '#2D2D2D',
          },
          '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
            borderColor: '#2D2D2D',
          },
          color: '#2D2D2D',
        },
      },
    },
    MuiInputLabel: {
      styleOverrides: {
        root: {
          color: 'rgba(45, 45, 45, 0.7)',
          '&.Mui-focused': {
            color: '#2D2D2D',
          },
        },
      },
    },
    MuiSelect: {
      styleOverrides: {
        icon: { color: '#2D2D2D' },
      }
    },
  },
});

function App() {
  // Directly set the starting view to 'main' instead of 'landing'
  const [currentView, setCurrentView] = useState('main'); 
  
  // Provide a default guest profile so Main.js loads without crashing
  const [currentUser, setCurrentUser] = useState({
    user_id: "guest_user_123",
    name: "Guest",
    email: "guest@emotionsense.com",
    phone: "0000000000"
  });

  const handleAuthSuccess = (userData) => {
    setCurrentUser(userData);
    setCurrentView('main');
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setCurrentView('login'); // Takes them back to login screen if they click logout
  };

  return (
    <ThemeProvider theme={lightTheme}>
      <CssBaseline />
      <AnimatePresence mode="wait">
        
        {/* 1. Landing Page */}
        {currentView === 'landing' && (
          <LandingPage key="landing" onEnter={() => setCurrentView('login')} />
        )}

        {/* 2. Login Page */}
        {currentView === 'login' && (
          <Login 
            key="login" 
            onLoginSuccess={handleAuthSuccess} 
            switchToRegister={() => setCurrentView('register')} 
          />
        )}

        {/* 3. Register Page */}
        {currentView === 'register' && (
          <Register 
            key="register" 
            onRegisterSuccess={handleAuthSuccess} 
            switchToLogin={() => setCurrentView('login')} 
          />
        )}

        {/* 4. Main App (Camera & Recommendations) */}
        {currentView === 'main' && (
          <motion.div
            key="main"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1 }}
          >
            {/* Pass the guest/current user object and logout function to Main */}
            <Main currentUser={currentUser} onLogout={handleLogout} />
          </motion.div>
        )}

      </AnimatePresence>
    </ThemeProvider>
  );
}

export default App;
