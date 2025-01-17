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

interface SignInProps {
    setUser: (fn: User | null) => void
    user: User | null
}

function SignIn({ setUser, user }: SignInProps) {
    const [open, setOpen] = useState<boolean>(false)
    const [loginError, setLoginError] = useState<boolean>(false)

    const handleLogin = (): void => {
        setOpen(true)
    }

    const handleLogout = (): void => {
        setUser(null)
    }

    const handleClose = (): void => {
        setOpen(false)
    }

    const loginUser = (username: string, password: string): void => {
        const request = fetch("http://localhost:5555/login", {
            method: "POST",
            headers: {
                Password: password,
                Username: username,
            },
        })

        request
            .then((response) => {
                if (response.ok) {
                    return response.json()
                } else {
                    setLoginError(true)
                    setTimeout(() => {
                        setLoginError(false)
                    }, 5000)
                    throw new Error("Login failed" + response)
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
                {user == null ? (
                    <Button variant="contained" color="primary" onClick={handleLogin}>
                        Sign in
                    </Button>
                ) : (
                    <Button variant="contained" color="primary" onClick={handleLogout}>
                        Logout
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
                        loginUser(event.currentTarget.username.value, event.currentTarget.password.value)
                    },
                }}
            >
                {loginError && <Alert severity="warning">Login failed.</Alert>}
                <DialogTitle>Sign in</DialogTitle>
                <DialogContent>
                    <DialogContentText>Please enter your username and password.</DialogContentText>
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
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose}>Cancel</Button>
                    <Button type="submit">Submit</Button>
                </DialogActions>
            </Dialog>
        </Container>
    )
}

export default SignIn
