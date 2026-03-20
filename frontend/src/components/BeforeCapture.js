import React, { useCallback } from 'react'
import Webcam from "react-webcam";
import Container from '@mui/material/Container';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box'; // Imported Box for layout

function BeforeCapture(props) {
	const { beforeCaptureProps } = props
	const { input, webcamRef, setPhoto, setEmpty } = beforeCaptureProps

	const videoConstraints = {
		width: 400,
		height: 400,
		facingMode: "user",
	};

	const capture = useCallback(() => {
		const imageSrc = webcamRef.current.getScreenshot();
		setPhoto(imageSrc);
		if (input !== null && input !== '') {
			setEmpty(false)
		}
	}, [webcamRef, input, setEmpty, setPhoto]);

	return (
		<Container maxWidth="xs" sx={{ alignItems: 'center', display: 'flex', flexDirection: 'column' }}>
			
			{/* 1. WRAPPER: Position relative allows us to place the box 'over' the video */}
			<Box sx={{ position: 'relative', width: 400, height: 400, overflow: 'hidden', borderRadius: '12px' }}>
				
				<Webcam
					audio={false}
					mirrored={true}
					height={400}
					width={400}
					ref={webcamRef}
					screenshotFormat="image/jpeg"
					videoConstraints={videoConstraints}
					style={{ objectFit: 'cover' }} 
				/>

				{/* 2. THE FACE GUIDE SQUARE */}
				<div style={{
					position: 'absolute',
					top: '50%',
					left: '50%',
					transform: 'translate(-50%, -50%)',
					width: '200px',        // Width of the square
					height: '250px',       // Height (slightly oval/rectangular for faces)
					border: '2px dashed rgba(0, 188, 212, 0.7)', // Cyan color matching your theme
					borderRadius: '30%',   // Rounded corners to look like a face shape
					boxShadow: '0 0 0 9999px rgba(0, 0, 0, 0.5)', // Darkens the area OUTSIDE the box
					zIndex: 10,
					pointerEvents: 'none'  // Clicks pass through to the video/button
				}}>
				</div>
                
                {/* Optional: "Scan" Line Animation (Purely visual cool factor) */}
                <div style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    width: '200px',
                    height: '2px',
                    backgroundColor: 'rgba(0, 188, 212, 0.5)',
                    boxShadow: '0 0 10px #00bcd4',
                    animation: 'scan 2s infinite ease-in-out',
                    zIndex: 11
                }} />

			</Box>

			<Button
				fullWidth
				variant="outlined"
				sx={{ marginTop: 2, marginBottom: 1 }}
				onClick={capture}
			>
				Capture photo
			</Button>

            {/* Inline keyframes for the scan animation */}
            <style>
                {`
                    @keyframes scan {
                        0% { transform: translate(-50%, -125px); opacity: 0; }
                        50% { opacity: 1; }
                        100% { transform: translate(-50%, 125px); opacity: 0; }
                    }
                `}
            </style>
		</Container>
	);
}

export default BeforeCapture;