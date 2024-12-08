import { Box } from "@mui/material"
import * as React from "react"
import bg from "../assets/Menu_background.webp"

export function Home() {
    return (
        <Box
            sx={{
                background: `url(${bg})`,
                height: "100vh",
                backgroundSize: "cover",
            }}
        >
            <h1>Home</h1>
            <p>Welcome to the home page.</p>
        </Box>
    )
}
