'use client'
import React, { useState } from 'react';
import {
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  TextField,
  DialogActions,
} from '@mui/material';
import { useRouter } from 'next/navigation';
import { LOGIN_API, VERIFY_API } from '@/utils/apiConstants';
import HTTPService from '@/utils/fetch';

enum LoginStates {
  LOGIN,
  VERIFY_OTP
}

const httpService = new HTTPService()
const LoginPopup = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loginState, setLoginState] = useState(LoginStates.LOGIN)
  const [otp, setOTP] = useState('');
  const router = useRouter();

  const handleClose = () => {
    router.push('/')
  }

  const handleLogin = async () => {
    // Here you can add your login logic, such as calling an API to authenticate the user
    try {
      const loginResponse = await httpService.request(LOGIN_API, { method: 'POST', body: { email: username, password } })
      if (loginResponse?.code) console.log('error', loginResponse)
      setLoginState(LoginStates.VERIFY_OTP)
    }
    catch (e) {
      console.log('error in fetching ', e)
    }
  };

  const handleOTP = async () => {
    if (!otp) {
      return;
    };
  }

  return (
    <div>
      <Dialog open={true} onClose={() => { }}>
        {
          loginState === LoginStates.LOGIN ?
            <>
              <DialogTitle>Login</DialogTitle>
              <DialogContent>
                <TextField
                  autoFocus
                  margin="dense"
                  label="Email"
                  type="email"
                  fullWidth
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
                <TextField
                  margin="dense"
                  label="Password"
                  type="password"
                  fullWidth
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </DialogContent>
              <DialogActions>
                <Button onClick={handleClose}>Cancel</Button>
                <Button onClick={handleLogin} variant="contained" color="primary">Login</Button>
              </DialogActions>
            </>
            : ''
        }
        {
          loginState === LoginStates.VERIFY_OTP ?
            <>
              <DialogTitle>Verify OTP</DialogTitle>
              <DialogContent>
                <TextField
                  autoFocus
                  margin="dense"
                  label="OTP"
                  type="text"
                  fullWidth
                  value={otp}
                  onChange={(e) => setOTP(e.target.value)}
                />
              </DialogContent>
              <DialogActions>
                <Button onClick={handleOTP} variant="contained" color="primary">Submit OTP</Button>
              </DialogActions>
            </> : ''
        }
      </Dialog>
    </div>
  );
};

export default LoginPopup;

