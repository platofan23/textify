import "./components/polyfills.ts"
import { StrictMode, useEffect } from "react"
import { createRoot } from "react-dom/client"
import Menu from "./menu/menu_base.tsx"
import React from "react"
import { Typography } from "@mui/material"
import { Home } from "./components/component_home.tsx"
import Translate from "./components/translate.tsx"
import { BrowserRouter as Router, useNavigate } from "react-router-dom"
import { Library } from "./pages/library.tsx"
import FileUploadPage from "./pages/uploade_page.tsx"
import { loadBooks } from "./components/load_books.ts"

export interface User {
    Username: string
}

export interface Book {
    _id: string
    count: number
}

function MainWrap() {
    const [user, setUser] = React.useState<User | null>(null)

    const [books, setBooks] = React.useState<Book[]>([])

    useEffect(() => {
        if (user != null) {
            loadBooks(user, setBooks)
        }
        console.log("Books loaded" + user?.Username)
    }, [user])

    return (
        <>
            <Router>
                <Menu setUser={setUser} user={user}>
                    {[
                        <Home key="Home" />,
                        <Library books={books} setBooks={setBooks} user={user} key="Library" />,
                        <FileUploadPage key="Upload" user={user} />,
                        <Translate key="Translate" />,
                    ]}
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
