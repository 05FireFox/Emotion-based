import React, { useState } from 'react';
import { Box, Typography, TextField, Container, Button, Grid } from '@mui/material';
import { motion } from 'framer-motion';

function Register({ onRegisterSuccess, switchToLogin }) {
  const [formData, setFormData] = useState({ name: '', email: '', phone: '', password: '', confirm: '', otp: '' });
  const [otpSent, setOtpSent] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSendOTP = async () => {
    // 1. Basic Empty Check
    if (!formData.email || !formData.phone || !formData.name) {
        return setError("Please fill in your Name, Email, and Phone number.");
    }

    // 2. Email Validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
        return setError("Please enter a valid email address (e.g., user@mail.com).");
    }

    // 3. Phone Validation (Must be exactly 10 digits)
    const phoneRegex = /^\d{10}$/;
    if (!phoneRegex.test(formData.phone)) {
        return setError("Phone number must be exactly 10 digits.");
    }

    // 4. Password Match Check
    if (formData.password !== formData.confirm) {
        return setError("Passwords do not match!");
    }

    // 5. STRONG PASSWORD VALIDATION
    // Requires: Min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special character
    const strongPasswordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    if (!strongPasswordRegex.test(formData.password)) {
        return setError("Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a number, and a special character (e.g., !@#$%^&*).");
    }
    
    setError('');
    setLoading(true);
    
    try {
      await fetch('http://localhost:8082/send_otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: formData.email })
      });
      setOtpSent(true);
      setLoading(false);
      alert("OTP sent! Check your Python console terminal to see the code.");
    } catch (err) {
      setError("Failed to send OTP. Check server.");
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8082/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await response.json();
      
      if (response.ok) {
        alert(`Registration Success! Please remember your new User ID: ${data.user.user_id}`);
        onRegisterSuccess(data.user); 
      } else {
        setError(data.error);
        setLoading(false);
      }
    } catch (err) {
        setError("Registration failed. Check server.");
        setLoading(false);
    }
  };

  return (
    <div style={{ backgroundColor: '#F9F9F9', minHeight: '100vh', width: '100%' }}>
        <Container maxWidth="sm" sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', minHeight: '100vh', py: 5 }}>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <Box sx={{ p: 5, textAlign: 'center', borderRadius: '16px', bgcolor: '#FFFFFF', boxShadow: '0 8px 30px rgba(0,0,0,0.05)', border: '1px solid rgba(0,0,0,0.05)' }}>
            <Typography variant="h4" sx={{ mb: 3, fontWeight: 'bold', color: '#2D2D2D' }}>Create Account</Typography>
            
            {error && <Typography color="error" sx={{ mb: 2, fontWeight: 'bold' }}>{error}</Typography>}
            
            <form onSubmit={handleRegister}>
                <Grid container spacing={2}>
                <Grid item xs={12}><TextField fullWidth required label="Full Name" name="name" onChange={handleChange} sx={{ bgcolor: '#F9F9F9', borderRadius: 1 }} /></Grid>
                
                <Grid item xs={6}><TextField fullWidth required label="Email" name="email" type="email" onChange={handleChange} sx={{ bgcolor: '#F9F9F9', borderRadius: 1 }} /></Grid>
                <Grid item xs={6}><TextField fullWidth required label="Phone Number" name="phone" type="tel" onChange={handleChange} inputProps={{ maxLength: 10 }} sx={{ bgcolor: '#F9F9F9', borderRadius: 1 }} /></Grid>
                
                <Grid item xs={6}><TextField fullWidth required label="Password" name="password" type="password" onChange={handleChange} sx={{ bgcolor: '#F9F9F9', borderRadius: 1 }} /></Grid>
                <Grid item xs={6}><TextField fullWidth required label="Confirm Password" name="confirm" type="password" onChange={handleChange} sx={{ bgcolor: '#F9F9F9', borderRadius: 1 }} /></Grid>
                
                {!otpSent ? (
                    <Grid item xs={12}>
                    <Button fullWidth variant="contained" onClick={handleSendOTP} disabled={loading} sx={{ bgcolor: '#007BFF', color: '#F9F9F9', py: 1.5, mt: 2, boxShadow: 'none', '&:hover': { bgcolor: '#0056b3', boxShadow: 'none' } }}>
                        {loading ? 'Sending...' : 'Send OTP to Email & Phone'}
                    </Button>
                    </Grid>
                ) : (
                    <>
                    <Grid item xs={12}><TextField fullWidth required label="Enter 4-digit OTP" name="otp" onChange={handleChange} inputProps={{ maxLength: 4 }} sx={{ bgcolor: '#F9F9F9', borderRadius: 1 }} /></Grid>
                    <Grid item xs={12}>
                        <Button fullWidth type="submit" variant="contained" disabled={loading} sx={{ bgcolor: '#007BFF', color: '#F9F9F9', py: 1.5, mt: 1, boxShadow: 'none', '&:hover': { bgcolor: '#0056b3', boxShadow: 'none' } }}>
                        {loading ? 'Processing...' : 'Complete Registration'}
                        </Button>
                    </Grid>
                    </>
                )}
                </Grid>
            </form>
            <Button onClick={switchToLogin} sx={{ mt: 3, color: 'rgba(45,45,45,0.7)' }}>Already have an account? Login here.</Button>
            </Box>
        </motion.div>
        </Container>
    </div>
  );
}

export default Register;