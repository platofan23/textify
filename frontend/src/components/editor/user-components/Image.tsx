import React, { useState } from "react"
import { useNode } from "@craftjs/core"
import { Box, TextField, Button, Typography, Slider } from "@mui/material"

export const Image = ({ src, alt, width }: { src?: string; alt?: string; width?: number }) => {
    const {
        connectors: { connect, drag },
        selected,
        actions,
    } = useNode((state) => ({
        selected: state.events.selected,
    }))

    const defaultImg = "https://via.placeholder.com/350x150?text=Select+to+change+image"
    const [imageSrc, setImageSrc] = useState(src || defaultImg)

    return (
        <Box
            ref={(ref: any) => connect(drag(ref))}
            sx={{
                padding: "10px",
                margin: "5px 0",
                borderRadius: "4px",
                cursor: "pointer",
                border: selected ? "2px solid #2684ff" : "2px solid transparent",
                textAlign: "center",
            }}
        >
            <img
                src={imageSrc}
                alt={alt || "Book image"}
                style={{
                    maxWidth: "100%",
                    width: `${width || 100}%`,
                }}
            />
        </Box>
    )
}

const ImageSettings = () => {
    const { actions, src, alt, width } = useNode((node) => ({
        src: node.data.props.src,
        alt: node.data.props.alt,
        width: node.data.props.width,
    }))

    return (
        <Box>
            <TextField
                fullWidth
                margin="normal"
                label="Image URL"
                value={src || ""}
                onChange={(e) => actions.setProp((props: any) => (props.src = e.target.value))}
            />

            <TextField
                fullWidth
                margin="normal"
                label="Alt Text"
                value={alt || ""}
                onChange={(e) => actions.setProp((props: any) => (props.alt = e.target.value))}
            />

            <Typography gutterBottom>Width (%)</Typography>
            <Slider
                value={width || 100}
                step={5}
                min={10}
                max={100}
                onChange={(_, value) => actions.setProp((props: any) => (props.width = value as number))}
            />
        </Box>
    )
}

Image.craft = {
    props: {
        src: "",
        alt: "Book image",
        width: 100,
    },
    related: {
        settings: ImageSettings,
    },
    custom: {
        displayName: "Image",
    },
}
