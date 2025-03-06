import { StrictMode, useEffect } from "react"
import { createRoot } from "react-dom/client"
import { CssBaseline } from "@mui/material"
import Menu from "./menu/menu_base.tsx"
import React from "react"
import { Typography } from "@mui/material"
import { Home } from "./components/component_home.tsx"
import Translate from "./components/translate.tsx"
import { BrowserRouter as Router, useNavigate } from "react-router-dom"
import { Library } from "./pages/library.tsx"
import FileUploadPage from "./pages/uploade_page.tsx"
import { loadBooks } from "./components/load_books.ts"
import { ThemeProvider, createTheme } from "@mui/material/styles"
import { PaletteMode } from "@mui/material"

export interface User {
    Username: string
}

export interface Book {
    _id: string
    count: number
}

const getDesignTokens = (mode: PaletteMode) => ({
    palette: {
        mode,
        primary: {
            // Aged leather brown for primary actions
            main: mode === "light" ? "#8B4513" : "#D2B48C",
        },
        secondary: {
            // Faded gold accent
            main: mode === "light" ? "#CD853F" : "#DAA520",
        },
        background: {
            // Parchment in light mode, aged leather in dark mode
            default: mode === "light" ? "#F5F1E4" : "#2A1A0A",
            paper: mode === "light" ? "#FFFAEB" : "#3C2A1A",
        },
        text: {
            // Faded ink in light mode, aged paper in dark mode
            primary: mode === "light" ? "#3E2723" : "#E0D2BC",
            secondary: mode === "light" ? "#5D4037" : "#D7C7AE",
        },
        divider: mode === "light" ? "#C8B28E" : "#5E4A36",
    },
    typography: {
        fontFamily: '"Libre Baskerville", "Garamond", "Georgia", serif',
        button: {
            textTransform: "none",
        },
        h1: {
            fontWeight: 500,
            letterSpacing: "0.02em",
        },
        h2: {
            fontWeight: 500,
            letterSpacing: "0.02em",
        },
        body1: {
            lineHeight: 1.6,
        },
    },
    components: {
        MuiPaper: {
            styleOverrides: {
                root: {
                    // Subtle texture for paper components
                    backgroundImage:
                        mode === "light"
                            ? "linear-gradient(rgba(245, 241, 228, 0.05) 2px, transparent 2px), linear-gradient(90deg, rgba(245, 241, 228, 0.05) 2px, transparent 2px)"
                            : "none",
                    backgroundSize: "50px 50px",
                },
            },
        },
        MuiAppBar: {
            styleOverrides: {
                root: {
                    background:
                        mode === "light"
                            ? "linear-gradient(45deg, #8B4513 30%, #A0522D 90%)"
                            : "linear-gradient(45deg, #2A1A0A 30%, #3C2A1A 90%)",
                    boxShadow:
                        mode === "light" ? "0 3px 5px 2px rgba(139, 69, 19, .3)" : "0 3px 5px 2px rgba(20, 10, 0, .5)",
                },
            },
        },
        MuiButton: {
            styleOverrides: {
                root: {
                    borderRadius: 4,
                },
                contained: {
                    boxShadow: mode === "light" ? "0 2px 4px rgba(139, 69, 19, 0.25)" : "0 2px 4px rgba(0, 0, 0, 0.35)",
                },
            },
        },
        MuiListItemButton: {
            styleOverrides: {
                root: {
                    borderRadius: 8,
                    "&.Mui-selected": {
                        backgroundColor: mode === "light" ? "rgba(139, 69, 19, 0.15)" : "rgba(218, 165, 32, 0.2)",
                        color: mode === "light" ? "#8B4513" : "#DAA520",
                    },
                    "&:hover": {
                        backgroundColor: mode === "light" ? "rgba(139, 69, 19, 0.08)" : "rgba(218, 165, 32, 0.08)",
                    },
                },
            },
        },
        MuiDrawer: {
            styleOverrides: {
                paper: {
                    borderRight:
                        mode === "light" ? "1px solid rgba(200, 178, 142, 0.2)" : "1px solid rgba(62, 43, 30, 0.2)",
                },
            },
        },
        MuiDivider: {
            styleOverrides: {
                root: {
                    borderColor: mode === "light" ? "#C8B28E" : "#5E4A36",
                },
            },
        },
    },
})

// ColorMode context to manage theme state globally
export const ColorModeContext = React.createContext({
    toggleColorMode: () => {
        if (localStorage.getItem("colorMode") === "light") {
            localStorage.setItem("colorMode", "dark")
        } else {
            localStorage.setItem("colorMode", "light")
        }
    },
})

function MainWrap() {
    const [user, setUser] = React.useState<User | null>(null)
    const [books, setBooks] = React.useState<Book[]>([])

    // Get the user's preferred mode from localStorage or default to 'light'
    const storedMode = (localStorage.getItem("colorMode") as PaletteMode) || "light"
    const [mode, setMode] = React.useState<PaletteMode>(storedMode)

    // Color mode context value
    const colorMode = React.useMemo(
        () => ({
            toggleColorMode: () => {
                setMode((prevMode) => {
                    const newMode = prevMode === "light" ? "dark" : "light"
                    localStorage.setItem("colorMode", newMode)
                    console.log("Theme changed to:", newMode) // Debug log
                    return newMode
                })
            },
        }),
        []
    )

    // Generate theme based on current mode
    const theme = React.useMemo(() => createTheme(getDesignTokens(mode)), [mode])

    useEffect(() => {
        if (user != null) {
            loadBooks(user, setBooks)
        }
    }, [user])

    return (
        <ColorModeContext.Provider value={colorMode}>
            <ThemeProvider theme={theme}>
                <CssBaseline /> {/* Add CssBaseline for proper theme background */}
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
            </ThemeProvider>
        </ColorModeContext.Provider>
    )
}

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <MainWrap />
    </StrictMode>
)
