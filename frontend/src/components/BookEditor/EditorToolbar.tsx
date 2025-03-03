import React from "react"
import { Box, Button, Divider } from "@mui/material"
import FormatBoldIcon from "@mui/icons-material/FormatBold"
import FormatItalicIcon from "@mui/icons-material/FormatItalic"
import FormatUnderlinedIcon from "@mui/icons-material/FormatUnderlined"
import FormatListBulletedIcon from "@mui/icons-material/FormatListBulleted"
import FormatListNumberedIcon from "@mui/icons-material/FormatListNumbered"
import FormatAlignLeftIcon from "@mui/icons-material/FormatAlignLeft"
import FormatAlignCenterIcon from "@mui/icons-material/FormatAlignCenter"
import FormatAlignRightIcon from "@mui/icons-material/FormatAlignRight"

export const EditorToolbar: React.FC = () => {
    return (
        <Box
            sx={{
                display: "flex",
                flexWrap: "wrap",
                gap: 1,
                mb: 2,
                p: 1,
                backgroundColor: "#f5f5f5",
                borderRadius: 1,
            }}
        >
            <Button size="small" startIcon={<FormatBoldIcon />}>
                Bold
            </Button>

            <Button size="small" startIcon={<FormatItalicIcon />}>
                Italic
            </Button>

            <Button size="small" startIcon={<FormatUnderlinedIcon />}>
                Underline
            </Button>

            <Divider orientation="vertical" flexItem />

            <Button size="small" startIcon={<FormatListBulletedIcon />}>
                Bullet List
            </Button>

            <Button size="small" startIcon={<FormatListNumberedIcon />}>
                Number List
            </Button>

            <Divider orientation="vertical" flexItem />

            <Button size="small" startIcon={<FormatAlignLeftIcon />}>
                Left
            </Button>

            <Button size="small" startIcon={<FormatAlignCenterIcon />}>
                Center
            </Button>

            <Button size="small" startIcon={<FormatAlignRightIcon />}>
                Right
            </Button>
        </Box>
    )
}
