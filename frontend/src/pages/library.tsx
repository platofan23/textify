import { Divider, Grid2, List, ListItem, ListItemButton, Paper, Typography } from "@mui/material"
import React from "react"

export function Library() {
    return (
        <>
            <Grid2 sx={{ mt: 5 }} container spacing={2}>
                <Paper>
                    <Typography margin={2} variant="h4">
                        Library
                    </Typography>
                    <Divider />
                    <List sx={{ width: "100%", maxWidth: 400 }}>
                        <ListItem disablePadding>
                            <ListItemButton>
                                <Typography>Book 1</Typography>
                            </ListItemButton>
                        </ListItem>
                        <ListItem disablePadding>
                            <ListItemButton>
                                <Typography>Book 2</Typography>
                            </ListItemButton>
                        </ListItem>
                        <ListItem disablePadding>
                            <ListItemButton>
                                <Typography>Book 3</Typography>
                            </ListItemButton>
                        </ListItem>
                    </List>
                </Paper>
            </Grid2>
        </>
    )
}
