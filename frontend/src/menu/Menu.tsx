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
import SignIn from "./SignIn"
import { User } from "../main"
import { red } from "@mui/material/colors"

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
    const [buttonSelecter, setButtonSelecter] = React.useState("Home")

    return (
        <Box sx={{ display: "flex" }}>
            <CssBaseline />
            <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
                <Toolbar>
                    <Typography variant="h6" noWrap component="div">
                        Clipped drawer
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
                                selected={buttonSelecter === "Home"}
                                onClick={() => setButtonSelecter("Home")}
                            >
                                Home
                            </ListItemButton>
                        </ListItem>
                        <Divider />
                        <ListItem>
                            <ListItemButton
                                selected={buttonSelecter === "TTS"}
                                onClick={() => setButtonSelecter("TTS")}
                            >
                                OCR
                            </ListItemButton>
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
                    if (React.isValidElement(child) && child.key === buttonSelecter) {
                        return child
                    }
                })}
            </Box>
        </Box>
    )
}
