import React, { useState } from "react"
import { useNode } from "@craftjs/core"
import { TextField, Box, Typography, Slider, FormControl, InputLabel, Select, MenuItem } from "@mui/material"

export const Text = ({ text, fontSize, textAlign }: { text: string; fontSize?: number; textAlign?: string }) => {
    const {
        connectors: { connect, drag },
        selected,
        actions,
    } = useNode((state) => ({
        selected: state.events.selected,
    }))

    const [editable, setEditable] = useState(false)

    return (
        <Box
            ref={(ref) => connect(drag(ref))}
            onClick={() => selected && setEditable(true)}
            onBlur={() => setEditable(false)}
            sx={{
                padding: "10px",
                margin: "5px 0",
                borderRadius: "4px",
                cursor: "pointer",
                border: selected ? "2px solid #2684ff" : "2px solid transparent",
            }}
        >
            {editable ? (
                <TextField
                    fullWidth
                    multiline
                    value={text}
                    autoFocus
                    onChange={(e) => actions.setProp((props: any) => (props.text = e.target.value))}
                />
            ) : (
                <Typography
                    sx={{
                        fontSize: `${fontSize || 16}px`,
                        textAlign: (textAlign as any) || "left",
                    }}
                >
                    {text}
                </Typography>
            )}
        </Box>
    )
}

// This is the settings component that will be shown in the settings panel
const TextSettings = () => {
    const { actions, propValue } = useNode((node) => ({
        propValue: node.data.props,
    }))

    return (
        <Box>
            <Typography gutterBottom>Font Size</Typography>
            <Slider
                value={propValue.fontSize || 16}
                step={1}
                min={10}
                max={80}
                onChange={(_, value) => actions.setProp((props: any) => (props.fontSize = value as number))}
            />

            <FormControl fullWidth margin="normal">
                <InputLabel>Text Align</InputLabel>
                <Select
                    value={propValue.textAlign || "left"}
                    onChange={(e) => actions.setProp((props: any) => (props.textAlign = e.target.value))}
                >
                    <MenuItem value="left">Left</MenuItem>
                    <MenuItem value="center">Center</MenuItem>
                    <MenuItem value="right">Right</MenuItem>
                    <MenuItem value="justify">Justify</MenuItem>
                </Select>
            </FormControl>
        </Box>
    )
}

// This is the critical part that connects the component to its settings
Text.craft = {
    props: {
        text: "Click to edit text",
        fontSize: 16,
        textAlign: "left",
    },
    related: {
        settings: TextSettings,
    },
    displayName: "Text",
}
