import React from "react"
import { Box, Typography, Divider, Alert } from "@mui/material"
import { useEditor } from "@craftjs/core"

export const SettingsPanel = () => {
    const { selected, displayName, settingsComponent, error } = useEditor((state, query) => {
        const selectedIdSet = state.events.selected
        let settingsComponent = null
        let displayName = null
        let error = null

        try {
            const selectedId = selectedIdSet.keys().next().value
            // Only attempt to access node if selectedId exists and is valid
            if (selectedId && typeof selectedId === "string") {
                // Get all nodes to check if the selected node exists
                const nodes = state.nodes || {}

                if (nodes[selectedId]) {
                    const node = query.node(selectedId).get()

                    console.log("Node", node)

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
        <Box sx={{ p: 2, border: "1px solid #e0e0e0", borderRadius: 1 }}>
            <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                Settings
            </Typography>
            <Divider sx={{ mb: 2 }} />

            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
            )}

            {!selected && (
                <Typography variant="body2" color="text.secondary">
                    Select an element to edit its properties
                </Typography>
            )}

            {selected && !settingsComponent && (
                <Typography variant="body2" color="text.secondary">
                    {displayName
                        ? `No settings available for ${displayName}`
                        : "No settings available for this element"}
                </Typography>
            )}

            {selected && settingsComponent && React.createElement(settingsComponent)}
        </Box>
    )
}
