import React from "react"
import { Element, useNode } from "@craftjs/core"
import {
    Box,
    Typography,
    Slider,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Switch,
    FormControlLabel,
} from "@mui/material"

export const Container = ({
    children,
    background,
    padding,
    position,
    left,
    top,
    width,
    float,
}: {
    children?: React.ReactNode
    background?: string
    padding?: number
    position?: "static" | "relative" | "absolute"
    left?: number | string
    top?: number | string
    width?: string
    float?: "none" | "left" | "right"
}) => {
    const {
        connectors: { connect, drag },
        selected,
    } = useNode((state) => ({
        selected: state.events.selected,
    }))

    return (
        <Box
            ref={(ref: any) => connect(drag(ref))}
            sx={{
                margin: position === "absolute" ? 0 : "5px 0",
                background: background || "transparent",
                padding: `${padding || 20}px`,
                border: selected ? "2px solid #2684ff" : "2px solid #f5f5f5",
                borderRadius: "4px",
                position: position || "static",
                left: position === "absolute" ? left : "auto",
                top: position === "absolute" ? top : "auto",
                width: width || "100%",
                float: float || "none",
                zIndex: position === "absolute" ? 10 : "auto",
                boxSizing: "border-box",
            }}
        >
            {children}
        </Box>
    )
}

const ContainerSettings = () => {
    const { actions, background, padding, position, left, top, width, float } = useNode((node) => ({
        background: node.data.props.background,
        padding: node.data.props.padding,
        position: node.data.props.position,
        left: node.data.props.left,
        top: node.data.props.top,
        width: node.data.props.width,
        float: node.data.props.float,
    }))

    // Toggle between absolute and relative positioning
    const handlePositioningChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const useAbsolute = e.target.checked
        actions.setProp((props: any) => {
            props.position = useAbsolute ? "absolute" : "static"
            props.float = "none" // Reset float when switching to absolute
        })
    }

    return (
        <Box>
            <FormControl fullWidth margin="normal">
                <InputLabel>Background</InputLabel>
                <Select
                    value={background || "transparent"}
                    onChange={(e) => actions.setProp((props: any) => (props.background = e.target.value))}
                >
                    <MenuItem value="transparent">Transparent</MenuItem>
                    <MenuItem value="#f5f5f5">Light Gray</MenuItem>
                    <MenuItem value="#e0f7fa">Light Blue</MenuItem>
                    <MenuItem value="#fff8e1">Light Yellow</MenuItem>
                    <MenuItem value="#f1f8e9">Light Green</MenuItem>
                </Select>
            </FormControl>

            <Typography gutterBottom>Width (%)</Typography>
            <Slider
                value={parseInt(width as string) || 100}
                step={5}
                min={10}
                max={100}
                onChange={(_, value) => actions.setProp((props: any) => (props.width = `${value}%`))}
            />

            <Typography gutterBottom>Padding</Typography>
            <Slider
                value={padding || 20}
                step={5}
                min={0}
                max={100}
                onChange={(_, value) => actions.setProp((props: any) => (props.padding = value as number))}
            />

            <FormControlLabel
                control={<Switch checked={position === "absolute"} onChange={handlePositioningChange} />}
                label="Free positioning"
                sx={{ my: 1 }}
            />

            {position === "absolute" ? (
                <Box sx={{ mt: 2 }}>
                    <Typography gutterBottom>Position X (px)</Typography>
                    <Slider
                        value={parseInt(left as string) || 0}
                        step={5}
                        min={0}
                        max={500}
                        onChange={(_, value) => actions.setProp((props: any) => (props.left = `${value}px`))}
                    />

                    <Typography gutterBottom>Position Y (px)</Typography>
                    <Slider
                        value={parseInt(top as string) || 0}
                        step={5}
                        min={0}
                        max={500}
                        onChange={(_, value) => actions.setProp((props: any) => (props.top = `${value}px`))}
                    />
                </Box>
            ) : (
                <FormControl fullWidth margin="normal">
                    <InputLabel>Float</InputLabel>
                    <Select
                        value={float || "none"}
                        onChange={(e) => actions.setProp((props: any) => (props.float = e.target.value))}
                    >
                        <MenuItem value="none">None (Full Width)</MenuItem>
                        <MenuItem value="left">Left</MenuItem>
                        <MenuItem value="right">Right</MenuItem>
                    </Select>
                </FormControl>
            )}
        </Box>
    )
}

// Add this at the end of the file, replacing the existing Container.craft definition:

Container.craft = {
    props: {
        background: "transparent",
        padding: 20,
        position: "static",
        left: "0px",
        top: "0px",
        width: "100%",
        float: "none",
    },
    related: {
        settings: ContainerSettings,
    },
    custom: {
        displayName: "Container",
    },
    isCanvas: true,
}
