import React from 'react'
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

function EmotionCard({ emotion }) {
	return (
		<Box sx={{ textAlign: 'center', mb: 3 }}>
			<Typography variant="overline" display="block" gutterBottom sx={{ opacity: 0.7, color: 'rgba(45,45,45,0.7)' }}>
				DETECTED EMOTION
			</Typography>
			<Typography variant="h2" component="div" sx={{ 
                fontWeight: 'bold', 
                color: '#007BFF',
                textTransform: 'uppercase'
            }}>
				{emotion || "..."}
			</Typography>
		</Box>
	);
}

export default EmotionCard;