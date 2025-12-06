import React, { useCallback } from 'react'

import Webcam from "react-webcam";

import Container from '@mui/material/Container';
import Button from '@mui/material/Button';

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
		console.log('inside capture')
		if (input !== null && input!=='') {
			setEmpty(false)
		}
	}, [webcamRef, input, setEmpty, setPhoto]);

	return (
		<Container maxWidth="xs" sx={{alignItems: 'center'}}>
			<Webcam
				audio={false}
				mirrored={true}
				height={400}
				width={400}
				ref={webcamRef}
				screenshotFormat="image/jpeg"
				videoConstraints={videoConstraints}
			/>
			<Button
				fullWidth
				variant="outlined"
				sx={{ marginTop: 0.5, marginBottom: 1 }}
				onClick={capture}
			>
				Capture photo
			</Button>
		</Container>
	);
}

export default BeforeCapture;