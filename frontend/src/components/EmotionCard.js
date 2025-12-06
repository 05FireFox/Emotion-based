import React from 'react'
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

function EmotionCard({ emotion }) {
	return (
		<Box sx={{ textAlign: 'center', mb: 3 }}>
			<Typography variant="overline" display="block" gutterBottom sx={{ opacity: 0.7, color: 'white' }}>
				DETECTED EMOTION
			</Typography>
			<Typography variant="h2" component="div" sx={{ 
                fontWeight: 'bold', 
                background: 'linear-gradient(45deg, #00bcd4, #ffffff)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                textTransform: 'uppercase'
            }}>
				{emotion || "..."}
			</Typography>
		</Box>
	);
}

export default EmotionCard;