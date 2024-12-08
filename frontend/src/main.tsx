import { StrictMode } from "react"
import { createRoot } from "react-dom/client"

import Menu from "./menu/Menu.tsx"
import React from "react"
import { Typography } from "@mui/material"
import { Home } from "./components/Home.tsx"

export interface User {
    name: string
}

function MainWrap() {
    const [user, setUser] = React.useState<User | null>(null)
    return (
        <>
            <Menu setUser={setUser} user={user}>
                {[
                    <Home key="Home" />,
                    <Typography key="TTS" sx={{ marginBottom: 2 }}>
                        Text to speech
                    </Typography>,
                ]}
            </Menu>
        </>
    )
}

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <MainWrap />
    </StrictMode>
)
