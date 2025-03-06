import React from "react"
import { Box, Typography, Divider, Alert, Paper, CircularProgress } from "@mui/material"
import { useEditor } from "@craftjs/core"
import SettingsIcon from "@mui/icons-material/Settings"
import TuneIcon from "@mui/icons-material/Tune"

export const SettingsPanel = () => {
    const { selected, displayName, settingsComponent, error } = useEditor((state, query) => {
        const selectedIdSet = state.events.selected
        let settingsComponent = null
        let displayName = null
        let error = null
        const selectedId = selectedIdSet.keys().next().value

        try {
            // Only attempt to access node if selectedId exists and is valid
            if (selectedId && typeof selectedId === "string") {
                // Get all nodes to check if the selected node exists
                const nodes = state.nodes || {}

                if (nodes[selectedId]) {
                    const node = query.node(selectedId).get()

                    displayName =
                        node.data.custom?.displayName ||
                        node.data.displayName ||
                        node.data.type?.resolvedName ||
                        "Unknown"

                    // Access settings from related field if it exists
                    if (node.related && node.related.settings) {
                        settingsComponent = node.related.settings
                    }
                } else {
                    // Node with this ID doesn't exist in state
                    error = `Node with ID ${selectedId} not found in editor state`
                }
            }
        } catch (e) {
            console.error("Error in SettingsPanel:", e)
            error = e.message
        }

        return {
            selected: selectedId,
            displayName,
            settingsComponent,
            error,
        }
    })

    return (
        <Paper
            elevation={0}
            sx={{
                p: 2,
                border: "1px solid #e0e0e0",
                borderRadius: 1,
                height: "100%",
                overflow: "auto",
                maxHeight: "calc(100vh - 280px)",
            }}
        >
            <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                <SettingsIcon sx={{ mr: 1, color: "text.secondary", fontSize: 20 }} />
                <Typography variant="subtitle1" fontWeight="bold">
                    Element Settings
                </Typography>
            </Box>
            <Divider sx={{ mb: 2 }} />

            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
            )}

            {!selected && (
                <Box
                    sx={{
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        justifyContent: "center",
                        py: 6,
                        color: "text.secondary",
                    }}
                >
                    <TuneIcon sx={{ fontSize: 40, mb: 2, opacity: 0.7 }} />
                    <Typography variant="body2" color="text.secondary" align="center">
                        Select an element in the editor to modify its properties
                    </Typography>
                </Box>
            )}

            {selected && !settingsComponent && (
                <Box
                    sx={{
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        justifyContent: "center",
                        py: 4,
                        color: "text.secondary",
                    }}
                >
                    <Typography variant="body2" color="text.secondary" align="center">
                        {displayName
                            ? `No configuration options available for this ${displayName}`
                            : "This element has no configurable properties"}
                    </Typography>
                </Box>
            )}

            {selected && settingsComponent && (
                <Box>
                    <Typography
                        variant="subtitle2"
                        gutterBottom
                        sx={{
                            mb: 2,
                            color: "primary.main",
                            fontWeight: "medium",
                            display: "flex",
                            alignItems: "center",
                        }}
                    >
                        {displayName}
                    </Typography>
                    <Box sx={{ px: 0.5 }}>{React.createElement(settingsComponent)}</Box>
                </Box>
            )}
        </Paper>
    )
}
