import React, { useState } from "react"
import { useNode } from "@craftjs/core"
import { TextField, Box, Typography, FormControl, InputLabel, Select, MenuItem } from "@mui/material"

export const Heading = ({ text, variant }: { text: string; variant?: "h1" | "h2" | "h3" | "h4" | "h5" | "h6" }) => {
    const {
        connectors: { connect, drag },
        selected,
        actions,
    } = useNode((state) => ({
        selected: state.events.selected,
    }))

    const [editable, setEditable] = useState(false)

    const variantMapping = {
        h1: { size: 32, weight: 800 },
        h2: { size: 28, weight: 700 },
        h3: { size: 24, weight: 700 },
        h4: { size: 20, weight: 600 },
        h5: { size: 18, weight: 600 },
        h6: { size: 16, weight: 600 },
    }

    const currentVariant = variant || "h2"
    const { size, weight } = variantMapping[currentVariant]

    return (
        <Box
            ref={(ref: any) => connect(drag(ref))}
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
                    value={text}
                    autoFocus
                    onChange={(e) => actions.setProp((props: any) => (props.text = e.target.value))}
                />
            ) : (
                <Typography
                    sx={{
                        fontSize: `${size}px`,
                        fontWeight: weight,
                    }}
                >
                    {text}
                </Typography>
            )}
        </Box>
    )
}

const HeadingSettings = () => {
    const { actions, variant } = useNode((node) => ({
        variant: node.data.props.variant,
    }))

    return (
        <Box>
            <FormControl fullWidth margin="normal">
                <InputLabel>Heading Type</InputLabel>
                <Select
                    value={variant || "h2"}
                    onChange={(e) => actions.setProp((props: any) => (props.variant = e.target.value))}
                >
                    <MenuItem value="h1">Heading 1</MenuItem>
                    <MenuItem value="h2">Heading 2</MenuItem>
                    <MenuItem value="h3">Heading 3</MenuItem>
                    <MenuItem value="h4">Heading 4</MenuItem>
                    <MenuItem value="h5">Heading 5</MenuItem>
                    <MenuItem value="h6">Heading 6</MenuItem>
                </Select>
            </FormControl>
        </Box>
    )
}

Heading.craft = {
    props: {
        text: "Heading",
        variant: "h2",
    },
    related: {
        settings: HeadingSettings,
    },
    custom: {
        displayName: "Heading",
    },
}
