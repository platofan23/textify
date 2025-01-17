import { StrictMode } from "react"
import { createRoot } from "react-dom/client"

import Menu from "./menu/menu_base.tsx"
import React from "react"
import { Typography } from "@mui/material"
import { Home } from "./components/component_home.tsx"
import Translate from "./components/translate.tsx"
import { BrowserRouter as Router, useNavigate } from "react-router-dom"
import { Library } from "./pages/library.tsx"

export interface User {
    Username: string
}

function MainWrap() {
    const [user, setUser] = React.useState<User | null>(null)

    return (
        <>
            <Router>
                <Menu setUser={setUser} user={user}>
                    {[<Home key="Home" />, <Library key="Library" />, <Translate key="Translate" />]}
                </Menu>
            </Router>
        </>
    )
}

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <MainWrap />
    </StrictMode>
)
