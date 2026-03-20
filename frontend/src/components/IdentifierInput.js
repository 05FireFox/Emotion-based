import React, { useEffect } from 'react'
import Grid from '@mui/material/Grid';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import TextField from '@mui/material/TextField';

function IdentifierInput(props) {
  const { identifierInputProps } = props;
  
  // We don't need handleInputChange anymore because the input is locked!
  const { isUser, input, photo, setEmpty, setError } = identifierInputProps;

  // Automatically unlock the "Get Recommendations" button once a photo is taken
  // because the ID is already filled out and validated for them by the login screen.
  useEffect(() => {
    if (input && photo !== null) {
      setEmpty(false);
      setError(false);
    } else {
      setEmpty(true);
    }
  }, [input, photo, setEmpty, setError]);

  return (
    <Grid container spacing={2}>
      
      {/* 1. ID TYPE DROPDOWN (Locked to 'User') */}
      <Grid item xs={4} sx={{ display: 'flex', flexDirection: 'column' }}>
        <FormControl fullWidth>
          <InputLabel id="select-id-type" disabled={true} sx={{ marginTop: 2 }}>ID type</InputLabel>
          <Select
            labelId="select-id-type"
            value={isUser}
            disabled={true} // Locked!
            label="ID type"
            sx={{ marginTop: 2, bgcolor: '#F9F9F9', borderRadius: 1, '& .MuiSelect-select.Mui-disabled': { WebkitTextFillColor: '#2D2D2D' } }}
          >
            <MenuItem value={true}>User</MenuItem>
            <MenuItem value={false}>Steam</MenuItem>
          </Select>
        </FormControl>
      </Grid>

      {/* 2. TEXT FIELD (Locked to show their generated ID) */}
      <Grid item xs={8} sx={{ display: 'flex', flexDirection: 'column' }}>
        <TextField
          required 
          fullWidth 
          margin="normal" 
          type="text"
          label="Your Generated ID"
          disabled={true} // Locked! They cannot edit this.
          value={input || "Loading..."} // Displays the ID passed down from Login
          sx={{ bgcolor: '#F9F9F9', borderRadius: 1, '& .MuiInputBase-input.Mui-disabled': { WebkitTextFillColor: '#2D2D2D' } }}
        />
      </Grid>

    </Grid>
  );
}

export default IdentifierInput;