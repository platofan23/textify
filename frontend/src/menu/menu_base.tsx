import * as React from "react"
import HomeIcon from "@mui/icons-material/Home"
import LibraryBooksIcon from "@mui/icons-material/LibraryBooks"
import CloudUploadIcon from "@mui/icons-material/CloudUpload"
import TranslateIcon from "@mui/icons-material/Translate"
import LoginIcon from "@mui/icons-material/Login"
import Box from "@mui/material/Box"
import Drawer from "@mui/material/Drawer"
import AppBar from "@mui/material/AppBar"
import CssBaseline from "@mui/material/CssBaseline"
import Toolbar from "@mui/material/Toolbar"
import List from "@mui/material/List"
import Typography from "@mui/material/Typography"
import Divider from "@mui/material/Divider"
import ListItem from "@mui/material/ListItem"
import ListItemButton from "@mui/material/ListItemButton"
import SignIn from "./menu_sign_In"
import SignUp from "./menu_sign_up"
import { User } from "../main"
import IconButton from "@mui/material/IconButton"
import Brightness4Icon from "@mui/icons-material/Brightness4" // For dark mode
import Brightness7Icon from "@mui/icons-material/Brightness7" // For light mode
import { useTheme } from "@mui/material/styles"
import { ColorModeContext } from "../main"
import { useNavigate, useLocation } from "react-router-dom"
import { Accordion, AccordionSummary } from "@mui/material"
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown"
import { useEditor } from "@craftjs/core"

const drawerWidth = 240

export default function Menu({
    setUser,
    user,
    children,
}: {
    setUser: (fn: User | null) => void
    user: User | null
    children: React.ReactNode[]
}) {
    const navigate = useNavigate()
    const location = useLocation()
    const path = location.pathname.slice(1)
    const NEED_LOGIN = ["Library"]
    // Remove the show = "none" line that was hiding the library menu
    // let show = "none"

    // Add theme context
    const theme = useTheme()
    const colorMode = React.useContext(ColorModeContext)

    React.useEffect(() => {
        if (NEED_LOGIN.includes(path) && user == null) {
            navigate("Home")
        }
    }, [user])

    React.useEffect(() => {
        navigate("Home")
    }, [])

    return (
        <Box sx={{ display: "flex" }}>
            <CssBaseline />
            <AppBar
                position="fixed"
                sx={{
                    zIndex: (theme) => theme.zIndex.drawer + 1,
                    background:
                        theme.palette.mode === "light"
                            ? "linear-gradient(45deg, #8B4513 30%, #A0522D 90%)"
                            : "linear-gradient(45deg, #2A1A0A 30%, #3C2A1A 90%)",
                    boxShadow:
                        theme.palette.mode === "light"
                            ? "0 3px 5px 2px rgba(139, 69, 19, .3)"
                            : "0 3px 5px 2px rgba(20, 10, 0, .5)",
                }}
            >
                <Toolbar sx={{ display: "flex", justifyContent: "space-between" }} component="div">
                    <Typography
                        variant="h6"
                        noWrap
                        component="div"
                        sx={{
                            fontWeight: "bold",
                            letterSpacing: "1px",
                        }}
                    >
                        Textify
                    </Typography>
                    <Box
                        sx={{
                            display: "flex",
                            alignItems: "center",
                            gap: 2, // Adds spacing between the buttons
                        }}
                        component="div"
                    >
                        {/* Add the dark mode toggle button */}
                        <IconButton
                            onClick={() => {
                                console.log("Toggle button clicked") // Debug log
                                colorMode.toggleColorMode()
                            }}
                            color="inherit"
                            sx={{
                                borderRadius: "50%",
                                bgcolor: "rgba(255, 255, 255, 0.1)",
                                "&:hover": {
                                    bgcolor: "rgba(255, 255, 255, 0.2)",
                                },
                                p: 1, // Add some padding to make the button more clickable
                            }}
                            aria-label="toggle dark mode"
                        >
                            {theme.palette.mode === "dark" ? <Brightness7Icon /> : <Brightness4Icon />}
                        </IconButton>
                        <SignIn setUser={setUser} user={user} />
                        <SignUp
                            setUser={setUser}
                            user={user}
                            sx={{
                                whiteSpace: "nowrap", // This ensures the text won't break into multiple lines
                            }}
                        />
                    </Box>
                </Toolbar>
            </AppBar>
            <Drawer
                variant="permanent"
                sx={{
                    width: drawerWidth,
                    flexShrink: 0,
                    [`& .MuiDrawer-paper`]: {
                        width: drawerWidth,
                        boxSizing: "border-box",
                        borderRight:
                            theme.palette.mode === "light"
                                ? "1px solid rgba(200, 178, 142, 0.2)"
                                : "1px solid rgba(62, 43, 30, 0.2)",
                        boxShadow: "0 0 10px rgba(0, 0, 0, 0.05)",
                    },
                }}
            >
                <Toolbar />
                <Box sx={{ overflow: "auto" }}>
                    <List>
                        <ListItem sx={{ padding: "4px 8px" }}>
                            <ListItemButton
                                selected={path === "Home"}
                                onClick={() => {
                                    navigate("Home")
                                }}
                                sx={{
                                    borderRadius: "8px",
                                    "&.Mui-selected": {
                                        backgroundColor:
                                            theme.palette.mode === "light"
                                                ? "rgba(139, 69, 19, 0.15)"
                                                : "rgba(218, 165, 32, 0.2)",
                                        color: theme.palette.mode === "light" ? "#8B4513" : "#DAA520",
                                        fontWeight: "bold",
                                    },
                                    "&:hover": {
                                        backgroundColor:
                                            theme.palette.mode === "light"
                                                ? "rgba(139, 69, 19, 0.08)"
                                                : "rgba(218, 165, 32, 0.08)",
                                    },
                                    display: "flex",
                                    alignItems: "center",
                                }}
                            >
                                <HomeIcon sx={{ mr: 1.5, fontSize: "20px" }} />
                                Home
                            </ListItemButton>
                        </ListItem>
                        <Divider sx={{ my: 1 }} />
                        {user == null ? (
                            // Show this when not logged in
                            <>
                                <ListItem sx={{ padding: "4px 8px" }}>
                                    <ListItemButton
                                        sx={{
                                            borderRadius: "8px",
                                            backgroundColor: theme.palette.mode === "light" ? "#CD853F" : "#DAA520",
                                            color: theme.palette.mode === "light" ? "#FFFFFF" : "#2A1A0A",
                                            transition: "all 0.3s ease",
                                            display: "flex",
                                            alignItems: "center",
                                            ":hover": {
                                                backgroundColor: theme.palette.mode === "light" ? "#B87333" : "#B8860B",
                                                transform: "translateY(-1px)",
                                            },
                                        }}
                                    >
                                        <LoginIcon sx={{ mr: 1.5, fontSize: "20px" }} />
                                        Login for more
                                    </ListItemButton>
                                </ListItem>
                                <Divider sx={{ my: 1 }} />
                            </>
                        ) : (
                            // Show this when logged in
                            <ListItem sx={{ padding: "4px 8px" }}>
                                <Accordion
                                    sx={{
                                        width: "100%",
                                        boxShadow: "none",
                                        "&:before": { display: "none" },
                                        backgroundColor: "transparent",
                                    }}
                                    defaultExpanded
                                >
                                    <AccordionSummary
                                        expandIcon={<ArrowDropDownIcon />}
                                        aria-controls="panel1-content"
                                        id="panel1-header"
                                        sx={{
                                            minHeight: "48px",
                                            borderRadius: "8px",
                                            "&:hover": {
                                                backgroundColor:
                                                    theme.palette.mode === "light"
                                                        ? "rgba(139, 69, 19, 0.08)"
                                                        : "rgba(218, 165, 32, 0.08)",
                                            },
                                        }}
                                    >
                                        <Box sx={{ display: "flex", alignItems: "center" }}>
                                            <LibraryBooksIcon sx={{ mr: 1.5, fontSize: "20px" }} />
                                            <Typography component="span">Book Library</Typography>
                                        </Box>
                                    </AccordionSummary>
                                    <ListItemButton
                                        selected={path === "Library"}
                                        onClick={() => {
                                            navigate("Library")
                                        }}
                                        sx={{
                                            pl: 4,
                                            borderRadius: "8px",
                                            my: 0.5,
                                            "&.Mui-selected": {
                                                backgroundColor:
                                                    theme.palette.mode === "light"
                                                        ? "rgba(139, 69, 19, 0.15)"
                                                        : "rgba(218, 165, 32, 0.2)",
                                                color: theme.palette.mode === "light" ? "#8B4513" : "#DAA520",
                                            },
                                        }}
                                    >
                                        Library
                                    </ListItemButton>
                                    <ListItemButton
                                        selected={path === "Upload"}
                                        onClick={() => {
                                            navigate("Upload")
                                        }}
                                        sx={{
                                            pl: 4,
                                            borderRadius: "8px",
                                            my: 0.5,
                                            "&.Mui-selected": {
                                                backgroundColor:
                                                    theme.palette.mode === "light"
                                                        ? "rgba(139, 69, 19, 0.15)"
                                                        : "rgba(218, 165, 32, 0.2)",
                                                color: theme.palette.mode === "light" ? "#8B4513" : "#DAA520",
                                            },
                                            display: "flex",
                                            alignItems: "center",
                                        }}
                                    >
                                        <CloudUploadIcon sx={{ mr: 1.5, fontSize: "20px" }} />
                                        Upload
                                    </ListItemButton>
                                </Accordion>
                            </ListItem>
                        )}

                        <ListItem sx={{ padding: "4px 8px" }}>
                            <Accordion
                                sx={{
                                    width: "100%",
                                    boxShadow: "none",
                                    "&:before": { display: "none" },
                                    backgroundColor: "transparent",
                                }}
                            >
                                <AccordionSummary
                                    expandIcon={<ArrowDropDownIcon />}
                                    aria-controls="panel2-content"
                                    id="panel2-header"
                                    sx={{
                                        minHeight: "48px",
                                        borderRadius: "8px",
                                        "&:hover": {
                                            backgroundColor:
                                                theme.palette.mode === "light"
                                                    ? "rgba(139, 69, 19, 0.08)"
                                                    : "rgba(218, 165, 32, 0.08)",
                                        },
                                    }}
                                >
                                    <Box sx={{ display: "flex", alignItems: "center" }}>
                                        <TranslateIcon sx={{ mr: 1.5, fontSize: "20px" }} />
                                        <Typography component="span">Translate</Typography>
                                    </Box>
                                </AccordionSummary>
                                <ListItemButton
                                    selected={path === "Translate"}
                                    onClick={() => {
                                        navigate("Translate")
                                    }}
                                    sx={{
                                        pl: 4,
                                        borderRadius: "8px",
                                        my: 0.5,
                                        "&.Mui-selected": {
                                            backgroundColor:
                                                theme.palette.mode === "light"
                                                    ? "rgba(139, 69, 19, 0.15)"
                                                    : "rgba(218, 165, 32, 0.2)",
                                            color: theme.palette.mode === "light" ? "#8B4513" : "#DAA520",
                                        },
                                    }}
                                >
                                    Translate
                                </ListItemButton>
                            </Accordion>
                        </ListItem>
                    </List>

                    <Divider sx={{ my: 1 }} />
                    <List></List>
                </Box>
            </Drawer>
            <Box
                component="main"
                sx={{
                    display: "flex",
                    flexDirection: "column",
                    height: "100vh",
                    width: "100%",
                }}
            >
                <Toolbar />
                {children.map((child) => {
                    if (React.isValidElement(child) && child.key === path) {
                        return child
                    }
                })}
            </Box>
        </Box>
    )
}
