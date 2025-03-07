import { Box, Grid2, Paper, Typography } from "@mui/material"
import * as React from "react"
import bg from "../assets/asset_menu_background.webp"

export function Home() {
    return (
        <Box
            sx={{
                background: `url(${bg})`,
                height: "100vh",
                backgroundSize: "cover",
            }}
        >
            <Paper
                sx={{
                    marginLeft: "auto",
                    marginRight: "auto",
                    marginTop: 25,
                    width: "fit-content",
                    padding: 2,
                    opacity: 0.9,
                }}
            >
                <Typography variant="h1" textAlign="center" sx={{ opacity: 1 }}>
                    Textify
                </Typography>
            </Paper>

            <Grid2 container spacing={2} sx={{ justifyContent: "center", alignItems: "center", marginTop: 10 }}>
                <Grid2>
                    <Paper
                        sx={{
                            width: "fit-content",
                            padding: 2,
                            opacity: 0.9,
                        }}
                    >
                        <Typography variant="h3" textAlign="center" sx={{ opacity: 1 }}>
                            Text to speech
                        </Typography>
                    </Paper>
                </Grid2>
                <Grid2>
                    <Paper
                        sx={{
                            width: "fit-content",
                            padding: 2,
                            opacity: 0.9,
                        }}
                    >
                        <Typography variant="h3" textAlign="center" sx={{ opacity: 1 }}>
                            Translate
                        </Typography>
                    </Paper>
                </Grid2>
            </Grid2>
        </Box>
    )
}
