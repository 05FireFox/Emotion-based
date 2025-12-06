import React, { useState } from 'react';
import Main from './Main.js';
import LandingPage from './LandingPage';
import './App.css'; 

import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { AnimatePresence, motion } from 'framer-motion';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00bcd4',
    },
    background: {
      default: 'transparent',
      paper: 'transparent',
    },
    text: {
      primary: '#ffffff',
      secondary: 'rgba(255, 255, 255, 0.7)',
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
            borderColor: 'rgba(255, 255, 255, 0.3)',
          },
          '&:hover .MuiOutlinedInput-notchedOutline': {
            borderColor: '#00bcd4',
          },
          '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
            borderColor: '#00bcd4',
          },
          color: 'white',
        },
      },
    },
    MuiInputLabel: {
      styleOverrides: {
        root: {
          color: 'rgba(255, 255, 255, 0.7)',
          '&.Mui-focused': {
            color: '#00bcd4',
          },
        },
      },
    },
    MuiSelect: {
      styleOverrides: {
        icon: { color: 'white' },
      }
    },
    MuiTableCell: {
      styleOverrides: {
          root: {
              borderBottom: '1px solid rgba(255,255,255,0.1)'
          },
          head: {
              backgroundColor: 'rgba(0,0,0,0.4) !important',
              color: '#00bcd4'
          }
      }
    }
  },
});

function App() {
  const [hasStarted, setHasStarted] = useState(false);

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <AnimatePresence mode="wait">
        {!hasStarted ? (
          <LandingPage key="landing" onEnter={() => setHasStarted(true)} />
        ) : (
          <motion.div
            key="main"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1 }}
          >
            <Main />
          </motion.div>
        )}
      </AnimatePresence>
    </ThemeProvider>
  );
}

export default App;