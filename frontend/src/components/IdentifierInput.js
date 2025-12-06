import React from 'react'

import Grid from '@mui/material/Grid';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import TextField from '@mui/material/TextField';

function IdentifierInput(props) {
	const { identifierInputProps } = props
	const { isUser, input, photo, error, loading, setIsUser, setEmpty, setInput, setEmotion, setTableData, setError } = identifierInputProps

	const handleSelectChange = (event) => {
		setIsUser(event.target.value);
		setEmpty(true)
		setInput('')
		setEmotion('')
		setTableData([])
	  }

	const handleInputChange = (event) => {
    if(event.target.value.length !== 0 && photo !== null){
      if(parseInt(event.target.value)){
        setEmpty(false)
        setError(false)
      } else {
        setError(true)
      }
    } else {
      setEmpty(true)
      setInput('')
      setEmotion('')
      setTableData([])
      if(parseInt(event.target.value)){
        setError(false)
      } else if(event.target.value.length === 0) {
        setError(false)
      } else {
        setError(true)
      }
    }
	setInput(event.target.value)
	}

	return (
		<Grid container>
              <Grid item xs={4} sx={{display: 'flex', flexDirection: 'column',}}>
              <FormControl fullWidth>
                <InputLabel id="select-id-type" disabled={loading} sx={{marginTop: 2}}>ID type</InputLabel>
                <Select
                  labelId="select-id-type"
                  value={isUser}
                  disabled={loading}
                  label="ID type"
                  onChange={handleSelectChange}
                  sx={{marginTop: 2}}
                >
                  <MenuItem value={true}>User</MenuItem>
                  <MenuItem value={false}>Steam</MenuItem>
                </Select>
              </FormControl>
              </Grid>
              <Grid item xs={8} sx={{display: 'flex', flexDirection: 'column',}}>
                <TextField
                  required fullWidth multiline autoFocus margin="normal" id="outlined-multiline-flexible" 
                  type="number"
                  error={error}
                  label={isUser ? "user id" : "steam id"}
                  disabled={loading}
                  value={input}
                  onChange={handleInputChange}
                />
              </Grid>
            </Grid>

	);
}

export default IdentifierInput;