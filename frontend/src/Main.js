import React, { useRef, useState } from "react";
import axios from 'axios';
import { motion, AnimatePresence } from "framer-motion";

// Import Menu and Avatar components
import { Container, Grid, Box, Typography, Avatar, Menu, MenuItem, IconButton, Divider } from '@mui/material';
import LoadingButton from '@mui/lab/LoadingButton';
import MuiAlert from '@mui/material/Alert';
import Snackbar from '@mui/material/Snackbar';

import IdentifierInput from "./components/IdentifierInput";
import BeforeCapture from "./components/BeforeCapture";
import AfterCapture from "./components/AfterCapture";
import EmotionCard from "./components/EmotionCard";
import TableGames from './components/TableGames';

function Main({ currentUser, onLogout }) {
  const webcamRef = useRef(null);
  
  // ==========================================
  // Profile Menu State (For Top-Right Avatar)
  // ==========================================
  const [anchorEl, setAnchorEl] = useState(null);
  const openMenu = Boolean(anchorEl);
  const handleMenuClick = (event) => setAnchorEl(event.currentTarget);
  const handleMenuClose = () => setAnchorEl(null);

  const [isUser, setIsUser] = useState(true);
  
  // Set the input automatically to the user's ID passed from the login
  const [input, setInput] = useState(currentUser?.user_id || '');
  
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
    
    // ✅ CHANGED: Removed the proxy path and added the full Environment Variable URL
    const url = `${process.env.REACT_APP_FILTERING_API_URL}/recommend/${isUser ? "user" : "game"}/${input}`;

    axios.post(url, {
      image: photo
    })
    .then(response => {
      // 1. CHECK FOR BLURRY/UNDETECTED FACE FIRST
      if (response.data.emotion === 'undetected') {
        setSnackbar({ 
          message: 'Face is blurry or unstable. Please RETAKE the image!', 
          severity: 'error', 
          open: true 
        });
        setLoading(false);
        return; 
      }

      // 2. CONTINUE AS NORMAL IF FACE IS DETECTED
      if(response.data.games.length === 0){
        setSnackbar({ message: `The ${isUser ? "user" : "steam"} ID might not exist in database`, severity: 'warning' , open: true});
      }
      
      setTableData(response.data.games);
      setEmotion(response.data.emotion);
      setLoading(false);

      // 3. NEW FEATURE: LOG TO EXCEL/CSV HISTORY
      if (response.data.games && response.data.games.length > 0) {
        // ✅ CHANGED: Replaced localhost with the Environment Variable
        fetch(`${process.env.REACT_APP_FILTERING_API_URL}/save_history`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: input,
            emotion: response.data.emotion,
            games: response.data.games.map(g => g.title).join(" | ")
          })
        }).catch(err => console.log("History logging failed", err));
      }

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
    <div style={{ backgroundColor: '#F9F9F9', minHeight: '100vh', width: '100%' }}>
      <Container component="main" maxWidth="lg" sx={{ position: 'relative', zIndex: 1, minHeight: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'center', py: 4 }}>
        
        {/* ========================================== */}
        {/* TOP RIGHT PROFILE ICON & MENU              */}
        {/* ========================================== */}
        {currentUser && (
          <Box sx={{ position: 'absolute', top: 20, right: 20 }}>
            <IconButton onClick={handleMenuClick} sx={{ backgroundColor: 'rgba(0,123,255,0.1)', '&:hover': { backgroundColor: 'rgba(0,123,255,0.3)'} }}>
              <Avatar sx={{ bgcolor: '#007BFF', color: '#F9F9F9' }}>
                {/* Shows the first letter of their name */}
                {currentUser.name ? currentUser.name.charAt(0).toUpperCase() : 'U'}
              </Avatar>
            </IconButton>
            
            <Menu
              anchorEl={anchorEl}
              open={openMenu}
              onClose={handleMenuClose}
              PaperProps={{
                sx: {
                  bgcolor: '#FFFFFF',
                  color: '#2D2D2D',
                  border: '1px solid rgba(0,0,0,0.05)',
                  mt: 1.5,
                  minWidth: '220px',
                  borderRadius: '12px',
                  boxShadow: '0 8px 30px rgba(0,0,0,0.1)'
                }
              }}
              transformOrigin={{ horizontal: 'right', vertical: 'top' }}
              anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            >
              <Box sx={{ px: 2, py: 1.5 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 'bold', color: '#007BFF' }}>
                  {currentUser.name}
                </Typography>
                <Typography variant="body2" sx={{ color: 'rgba(45,45,45,0.7)' }}>
                  {currentUser.email}
                </Typography>
                <Typography variant="body2" sx={{ color: 'rgba(45,45,45,0.7)', mt: 0.5 }}>
                  ID: {currentUser.user_id}
                </Typography>
              </Box>
              <Divider sx={{ borderColor: 'rgba(0,0,0,0.1)' }} />
              <MenuItem onClick={onLogout} sx={{ color: '#ff5252', py: 1.5, '&:hover': { bgcolor: 'rgba(255,82,82,0.1)' } }}>
                <Typography fontWeight="bold">Logout</Typography>
              </MenuItem>
            </Menu>
          </Box>
        )}
        {/* ========================================== */}

        {/* Header */}
        <Box sx={{ mb: 4, textAlign: 'center' }}>
          <Typography variant="h3" component="h1" sx={{ fontWeight: 800, letterSpacing: '-0.05em', color: '#2D2D2D' }}>
            EMOTION <span style={{ color: '#007BFF' }}>SENSE</span>
          </Typography>
          <Typography variant="subtitle1" sx={{ color: '#2D2D2D', letterSpacing: '0.1em' }}>
            GAME RECOMMENDER
          </Typography>
        </Box>

        <Grid container spacing={4} alignItems="flex-start">
          
          {/* LEFT PANEL */}
          <Grid item xs={12} md={6}>
            <motion.div variants={containerVariants} initial="hidden" animate="visible">
              <Box sx={{ p: 4, bgcolor: '#FFFFFF', borderRadius: '16px', boxShadow: '0 8px 30px rgba(0,0,0,0.05)', border: '1px solid rgba(0,0,0,0.05)' }}>
                <IdentifierInput identifierInputProps={identifierInputProps} />
                
                <Box sx={{ mt: 3, mb: 3, borderRadius: '12px', overflow: 'hidden', border: '1px solid rgba(0,0,0,0.05)' }}>
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
                    backgroundColor: '#007BFF',
                    color: '#F9F9F9',
                    boxShadow: 'none',
                    '&:hover': { backgroundColor: '#0056b3', boxShadow: 'none' },
                    '&:disabled': { backgroundColor: 'rgba(249,249,249,0.1)', color: 'rgba(249,249,249,0.3)' }
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
                  <Box sx={{ p: 4, minHeight: '400px', bgcolor: '#FFFFFF', borderRadius: '16px', boxShadow: '0 8px 30px rgba(0,0,0,0.05)', border: '1px solid rgba(0,0,0,0.05)' }}>
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
                    border: '1px solid rgba(0,0,0,0.05)', 
                    borderRadius: '16px',
                    backgroundColor: '#FFFFFF',
                    boxShadow: '0 8px 30px rgba(0,0,0,0.05)'
                  }}>
                    <Typography variant="body1" sx={{ color: 'rgba(45,45,45,0.5)' }}>
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
