import * as React from "react"
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
import { User } from "../main"
import { useNavigate, useLocation } from "react-router-dom"
import { Accordion, AccordionSummary } from "@mui/material"
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown"

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
    let show = "none"

    // Redirect to home page on first load
    React.useEffect(() => {
        if (path === "") navigate("Home")
    }, [])

    // Redirect to login page if user is not logged in
    React.useEffect(() => {
        if (NEED_LOGIN.includes(path) && user == null) {
            navigate("Home")
        }
    }, [user])

    if (user != null) {
        show = "1"
    }

    return (
        <Box sx={{ display: "flex" }}>
            <CssBaseline />
            <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
                <Toolbar>
                    <Typography variant="h6" noWrap component="div">
                        Textify
                    </Typography>
                    <SignIn setUser={setUser} user={user} />
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
                    },
                }}
            >
                <Toolbar />
                <Box sx={{ overflow: "auto" }}>
                    <List>
                        <ListItem>
                            <ListItemButton
                                selected={path === "Home"}
                                onClick={() => {
                                    navigate("Home")
                                }}
                            >
                                Home
                            </ListItemButton>
                        </ListItem>
                        <Divider />
                        {user == null && (
                            <>
                                <ListItem>
                                    <ListItemButton
                                        sx={{
                                            backgroundColor: "orange",
                                            color: "white",

                                            ":hover": {
                                                backgroundColor: "orange",
                                            },
                                        }}
                                    >
                                        Login for more
                                    </ListItemButton>
                                </ListItem>
                                <Divider />
                            </>
                        )}

                        <ListItem>
                            <Accordion sx={{ width: "100%", display: show }}>
                                <AccordionSummary
                                    expandIcon={<ArrowDropDownIcon />}
                                    aria-controls="panel1-content"
                                    id="panel1-header"
                                >
                                    <Typography component="span">Book Library</Typography>
                                </AccordionSummary>
                                <ListItemButton
                                    selected={path === "Library"}
                                    onClick={() => {
                                        navigate("Library")
                                    }}
                                >
                                    Library
                                </ListItemButton>
                                <ListItemButton
                                    selected={path === "Upload"}
                                    onClick={() => {
                                        navigate("Upload")
                                    }}
                                >
                                    Upload
                                </ListItemButton>
                            </Accordion>
                        </ListItem>
                        <ListItem>
                            <Accordion sx={{ width: "100%" }}>
                                <AccordionSummary
                                    expandIcon={<ArrowDropDownIcon />}
                                    aria-controls="panel2-content"
                                    id="panel2-header"
                                >
                                    <Typography component="span">Translate</Typography>
                                </AccordionSummary>
                                <ListItemButton
                                    selected={path === "Translate"}
                                    onClick={() => {
                                        navigate("Translate")
                                    }}
                                >
                                    Translate
                                </ListItemButton>
                            </Accordion>
                        </ListItem>
                    </List>

                    <Divider />
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
