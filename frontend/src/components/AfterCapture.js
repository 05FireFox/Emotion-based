import React from 'react'

import Container from '@mui/material/Container';
import Button from '@mui/material/Button';

function AfterCapture(props) {
	const { afterCaptureProps } = props
	const { photo, loading, setPhoto, setEmpty, setEmotion, setTableData } = afterCaptureProps

	const retakePhoto = () => {
		setPhoto(null);
		setEmpty(true)
		setEmotion('')
		setTableData([])
	}

	return (
		<Container maxWidth="xs" sx={{alignItems: 'center'}}>
          <img src={photo} alt="screenshot" />
          <Button
                fullWidth
                variant="outlined"
                sx={{ marginTop: 0.5, marginBottom: 1 }}
                onClick={retakePhoto}
				disabled={loading}
              >
                Retake
              </Button>
        </Container>
	);
}

export default AfterCapture;