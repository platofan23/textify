import { Button, Container, Box } from "@mui/material"
import { User } from "../main"

function SignIn({ setUser, user }: { setUser: (fn: User | null) => void; user: User | null }) {
    const handleLogin = () => {
        setUser({ name: "John Doe" })
    }
    const handleLogout = () => {
        setUser(null)
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
        </Container>
    )
}

export default SignIn
