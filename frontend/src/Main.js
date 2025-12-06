import React, { useRef, useState } from "react";
import axios from 'axios';
import { motion, AnimatePresence } from "framer-motion";

import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';
import LoadingButton from '@mui/lab/LoadingButton';
import MuiAlert from '@mui/material/Alert';
import Snackbar from '@mui/material/Snackbar';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

import IdentifierInput from "./components/IdentifierInput";
import BeforeCapture from "./components/BeforeCapture";
import AfterCapture from "./components/AfterCapture";
import EmotionCard from "./components/EmotionCard";
import TableGames from './components/TableGames';
// Removed Background3D to use the new "dashboard-container" CSS style

function Main() {
  const webcamRef = useRef(null);
  const [isUser, setIsUser] = useState(true);
  const [input, setInput] = useState('');
  const [photo, setPhoto] = useState(null);
  const [emotion, setEmotion] = useState('');
  const [tableData, setTableData] = useState([]);
  const [empty, setEmpty] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  const [snackbar, setSnackbar] = useState({ message: '', severity: 'info', open: false});

  const identifierInputProps = { isUser, input, photo, error, loading, setIsUser, setEmpty, setInput, setEmotion, setTableData, setError };
  const beforeCaptureProps = { input, webcamRef, setPhoto, setEmpty };
  const afterCaptureProps = { photo, loading, setPhoto, setEmpty, setEmotion, setTableData };

  const handleCloseSnackbar = (event, reason) => {
    if (reason === 'clickaway') return;
    setSnackbar({ ...snackbar, open: false });
  };
  
  const get_recommendations = () => {
    setLoading(true);
    
    // USING PROXY PATH to avoid CORS
    const url = `/recommend/${isUser ? "user" : "game"}/${input}`;

    axios.post(url, {
      image: photo
    })
    .then(response => {
      if(response.data.games.length === 0){
        setSnackbar({ message: `The ${isUser ? "user" : "steam"} ID might not exist in database`, severity: 'warning' , open: true});
      }
      setTableData(response.data.games);
      setEmotion(response.data.emotion);
      setLoading(false);
    })
    .catch(error => {
      setSnackbar({ message: 'Error! Check backend connection.', severity: 'error' , open: true });
      console.error(error);
      setLoading(false);
    });
  };
  
  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } }
  };

  return (
    <div className="dashboard-container">
      <Container component="main" maxWidth="lg" sx={{ position: 'relative', zIndex: 1, minHeight: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'center', py: 4 }}>
        
        {/* Header */}
        <Box sx={{ mb: 4, textAlign: 'center' }}>
          <Typography variant="h3" component="h1" sx={{ fontWeight: 800, letterSpacing: '-0.05em', color: 'white', textShadow: '0 4px 20px rgba(0,0,0,0.5)' }}>
            EMOTION <span style={{ color: '#00bcd4' }}>SENSE</span>
          </Typography>
          <Typography variant="subtitle1" sx={{ color: 'rgba(255,255,255,0.7)', letterSpacing: '0.1em' }}>
            GAME RECOMMENDER
          </Typography>
        </Box>

        <Grid container spacing={4} alignItems="flex-start">
          
          {/* LEFT PANEL */}
          <Grid item xs={12} md={6}>
            <motion.div variants={containerVariants} initial="hidden" animate="visible">
              <Box className="glass-panel" sx={{ p: 4 }}>
                <IdentifierInput identifierInputProps={identifierInputProps} />
                
                <Box sx={{ mt: 3, mb: 3, borderRadius: '12px', overflow: 'hidden', border: '1px solid rgba(255,255,255,0.1)' }}>
                  { photo === null ? (
                    <BeforeCapture beforeCaptureProps={beforeCaptureProps}/>
                  ) : (
                    <AfterCapture afterCaptureProps={afterCaptureProps}/>
                  )}
                </Box>

                <LoadingButton
                  fullWidth
                  loading={loading}
                  variant="contained"
                  size="large"
                  onClick={get_recommendations}
                  disabled={empty}
                  sx={{
                    borderRadius: '8px',
                    fontWeight: 'bold',
                    textTransform: 'none',
                    backgroundColor: '#00bcd4',
                    color: 'white',
                    '&:hover': { backgroundColor: '#00acc1' },
                    '&:disabled': { backgroundColor: 'rgba(255,255,255,0.1)', color: 'rgba(255,255,255,0.3)' }
                  }}
                >
                  {loading ? 'Analyzing...' : 'Get Recommendations'}
                </LoadingButton>
              </Box>
            </motion.div>
          </Grid>

          {/* RIGHT PANEL */}
          <Grid item xs={12} md={6}>
            <AnimatePresence mode="wait">
              {emotion ? (
                <motion.div 
                  key="results"
                  initial={{ opacity: 0, x: 20 }} 
                  animate={{ opacity: 1, x: 0 }} 
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.5 }}
                >
                  <Box className="glass-panel" sx={{ p: 4, minHeight: '400px' }}>
                    <EmotionCard emotion={emotion} />
                    <TableGames tableData={tableData} />
                  </Box>
                </motion.div>
              ) : (
                <motion.div 
                  key="placeholder"
                  initial={{ opacity: 0 }} 
                  animate={{ opacity: 0.5 }} 
                  transition={{ delay: 0.5 }}
                >
                  <Box sx={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center', 
                    height: '100%', 
                    minHeight: '400px', 
                    border: '2px dashed rgba(255,255,255,0.1)', 
                    borderRadius: '16px',
                    backgroundColor: 'rgba(0,0,0,0.2)'
                  }}>
                    <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                      Capture photo to see results
                    </Typography>
                  </Box>
                </motion.div>
              )}
            </AnimatePresence>
          </Grid>

        </Grid>

        <Snackbar open={snackbar.open} autoHideDuration={5000} onClose={handleCloseSnackbar} anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}>
          <MuiAlert onClose={handleCloseSnackbar} severity={snackbar.severity} variant="filled" sx={{ width: '100%' }}>
            {snackbar.message}
          </MuiAlert>
        </Snackbar>
      </Container>
    </div>
  );
}

export default Main;