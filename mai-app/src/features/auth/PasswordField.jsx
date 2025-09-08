import React, { useState } from 'react';
import { Button, InputAdornment, TextField } from '@mui/material';

export default function PasswordField({ label = 'Password', value, onChange, required, fullWidth = true, ...rest }) {
  const [show, setShow] = useState(false);
  return (
    <TextField
      label={label}
      type={show ? 'text' : 'password'}
      value={value}
      onChange={onChange}
      required={required}
      fullWidth={fullWidth}
      InputProps={{
        endAdornment: (
          <InputAdornment position="end">
            <Button onClick={() => setShow(s => !s)} size="small" tabIndex={-1} aria-label="toggle password">
              {show ? 'Hide' : 'Show'}
            </Button>
          </InputAdornment>
        )
      }}
      {...rest}
    />
  );
}
