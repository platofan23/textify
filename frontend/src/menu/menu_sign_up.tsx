import React, { useState } from "react"
import {
    Container,
    Box,
    Button,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogContentText,
    TextField,
    DialogActions,
    Alert,
} from "@mui/material"

import { User } from "../main"

interface SignUpProps {
    setUser: (fn: User | null) => void
    user: User | null
}

function SignUp({ setUser, user }: SignUpProps) {
    const [open, setOpen] = useState<boolean>(false)
    const [signUpError, setSignUpError] = useState<boolean>(false)
    const [passwordMismatch, setPasswordMismatch] = useState<boolean>(false)
    const [PasswordToWeak, setPasswordToWeak] = useState<boolean>(false)

    const handleSignUp = (): void => {
        setOpen(true)
    }

    const handleClose = (): void => {
        setOpen(false)
        setPasswordMismatch(false)
    }

    const checkPasswordStrength = (password: string): boolean => {
        // Check if password is at least 8 characters long
        if (password.length < 8) {
            return false
        }
        if (password.match(/[a-z]/) == null) {
            return false
        }
        if (password.match(/[A-Z]/) == null) {
            return false
        }
        if (password.match(/[0-9]/) == null) {
            return false
        }
        return true
    }

    const registerUser = (username: string, password: string, confirmPassword: string): void => {
        // Check if passwords match
        if (password !== confirmPassword) {
            setPasswordMismatch(true)
            return
        }
        setPasswordMismatch(false)

        // Check if password is strong enough
        if (!checkPasswordStrength(password)) {
            setPasswordToWeak(true)
            return
        }
        setPasswordMismatch(false)

        const request = fetch("http://localhost:5558/register", {
            method: "POST",
            headers: {
                Password: password,
                Username: username,
                Register: "true", // Indicate this is a registration request
            },
        })

        request
            .then((response) => {
                if (response.ok) {
                    return response.json()
                } else {
                    setSignUpError(true)
                    setTimeout(() => {
                        setSignUpError(false)
                    }, 5000)
                    throw new Error("Registration failed: " + response)
                }
            })
            .then((data) => {
                setUser({ Username: data.Username })
                handleClose()
            })
            .catch((error) => {
                console.error(error)
            })
    }

    return (
        <Container>
            <Box textAlign="right">
                {user == null && (
                    <Button
                        variant="contained"
                        color="primary"
                        sx={{
                            whiteSpace: "nowrap",
                            minWidth: "fit-content", // Ensures button doesn't shrink below text width
                        }}
                        onClick={handleSignUp}
                    >
                        Sign up
                    </Button>
                )}
            </Box>
            <Dialog
                open={open}
                onClose={handleClose}
                PaperProps={{
                    component: "form",
                    onSubmit: (event: React.FormEvent<HTMLFormElement>): void => {
                        event.preventDefault()
                        registerUser(
                            event.currentTarget.username.value,
                            event.currentTarget.password.value,
                            event.currentTarget.confirmPassword.value
                        )
                    },
                }}
            >
                {signUpError && <Alert severity="warning">Registration failed.</Alert>}
                {passwordMismatch && <Alert severity="warning">Passwords do not match.</Alert>}
                {PasswordToWeak && <Alert severity="warning">Password is too weak.</Alert>}
                <DialogTitle>Create Account</DialogTitle>
                <DialogContent>
                    <DialogContentText>Enter your details to register.</DialogContentText>
                    <TextField
                        autoFocus
                        required
                        margin="dense"
                        id="username"
                        name="username"
                        label="Username"
                        type="text"
                        fullWidth
                        variant="standard"
                    />
                    <TextField
                        required
                        margin="dense"
                        id="password"
                        name="password"
                        label="Password"
                        type="password"
                        fullWidth
                        variant="standard"
                    />
                    <TextField
                        required
                        margin="dense"
                        id="confirmPassword"
                        name="confirmPassword"
                        label="Confirm Password"
                        type="password"
                        fullWidth
                        variant="standard"
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose} color="primary">
                        Cancel
                    </Button>
                    <Button type="submit" variant="contained" color="primary">
                        Register
                    </Button>
                </DialogActions>
            </Dialog>
        </Container>
    )
}

export default SignUp
