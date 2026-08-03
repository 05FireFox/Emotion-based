import React, { useState } from 'react';
import { Box, Typography, TextField, Container, Button } from '@mui/material';
import { motion } from 'framer-motion';

function Login({ onLoginSuccess, switchToRegister }) {
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    
    // Quick validation
    if (!identifier || !password) {
        return setError("Please enter your login details.");
    }

    setLoading(true);
    setError('');

    try {
      // ✅ CHANGED: Now uses the environment variable
      const response = await fetch(`${process.env.REACT_APP_FILTERING_API_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identifier, password })
      });
      
      const data = await response.json();
      if (response.ok) {
        onLoginSuccess(data.user); 
      } else {
        setError(data.error);
        setLoading(false);
      }
    } catch (err) {
      setError("Server connection failed.");
      setLoading(false);
    }
  };

  return (
    <div style={{ backgroundColor: '#F9F9F9', minHeight: '100vh', width: '100%' }}>
      <Container maxWidth="sm" sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', minHeight: '100vh' }}>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <Box sx={{ p: 5, textAlign: 'center', borderRadius: '16px', bgcolor: '#FFFFFF', boxShadow: '0 8px 30px rgba(0,0,0,0.05)', border: '1px solid rgba(0,0,0,0.05)' }}>
            <Typography variant="h4" sx={{ mb: 1, fontWeight: 'bold', color: '#2D2D2D' }}>Welcome Back</Typography>
            <Typography variant="subtitle1" sx={{ mb: 4, color: 'rgba(45,45,45,0.7)' }}>Login to Emotion Sense</Typography>
            
            {error && <Typography color="error" sx={{ mb: 2, fontWeight: 'bold' }}>{error}</Typography>}
            
            <form onSubmit={handleLogin}>
              <TextField fullWidth required label="Email OR User ID" value={identifier} onChange={(e) => setIdentifier(e.target.value)} sx={{ mb: 3, bgcolor: '#F9F9F9', borderRadius: 1 }} />
              <TextField fullWidth required label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} sx={{ mb: 3, bgcolor: '#F9F9F9', borderRadius: 1 }} />
              <Button fullWidth type="submit" variant="contained" size="large" disabled={loading} sx={{ backgroundColor: '#007BFF', color: '#F9F9F9', py: 1.5, boxShadow: 'none', '&:hover': { backgroundColor: '#0056b3', boxShadow: 'none' } }}>
                {loading ? 'Logging in...' : 'Login'}
              </Button>
            </form>
            
            <Button onClick={switchToRegister} sx={{ mt: 3, color: 'rgba(45,45,45,0.7)' }}>Need an account? Register here.</Button>
          </Box>
        </motion.div>
      </Container>
    </div>
  );
}

export default Login;
