import React from "react"
import { Box, Typography, Button, Divider, Tooltip, Paper, Grid } from "@mui/material"
import { useEditor } from "@craftjs/core"
import { Text } from "./user-components/Text.tsx"
import { Container } from "./user-components/Container.tsx"
import { Image } from "./user-components/Image.tsx"
import { Heading } from "./user-components/Heading.tsx"
// Import icons
import TitleIcon from "@mui/icons-material/Title"
import TextFieldsIcon from "@mui/icons-material/TextFields"
import ImageIcon from "@mui/icons-material/Image"
import CheckBoxOutlineBlankIcon from "@mui/icons-material/CheckBoxOutlineBlank"

export const Toolbox = () => {
    const { connectors } = useEditor()

    // Component category definitions
    const categories = [
        {
            name: "Content",
            items: [
                {
                    name: "Heading",
                    icon: <TitleIcon />,
                    component: <Heading text="Heading" />,
                },
                {
                    name: "Text",
                    icon: <TextFieldsIcon />,
                    component: <Text text="Text block" />,
                },
            ],
        },
        {
            name: "Media",
            items: [
                {
                    name: "Image",
                    icon: <ImageIcon />,
                    component: <Image />,
                },
            ],
        },
        {
            name: "Layout",
            items: [
                {
                    name: "Container",
                    icon: <CheckBoxOutlineBlankIcon />,
                    component: (
                        <Container>
                            <Text text="Container content" />
                        </Container>
                    ),
                },
            ],
        },
    ]

    return (
        <Paper elevation={0} sx={{ p: 2, border: "1px solid #e0e0e0", borderRadius: 1, mb: 2 }}>
            <Typography
                variant="subtitle1"
                gutterBottom
                fontWeight="bold"
                sx={{ display: "flex", alignItems: "center" }}
            >
                Elements
            </Typography>
            <Divider sx={{ mb: 2 }} />

            {categories.map((category) => (
                <Box key={category.name} sx={{ mb: 2 }}>
                    <Typography
                        variant="caption"
                        color="text.secondary"
                        sx={{ display: "block", mb: 1, fontWeight: "medium" }}
                    >
                        {category.name}
                    </Typography>

                    <Grid container spacing={1}>
                        {category.items.map((item) => (
                            <Grid item xs={6} key={item.name}>
                                <Tooltip title={`Add ${item.name}`} placement="top">
                                    <Button
                                        variant="outlined"
                                        ref={(ref) => ref && connectors.create(ref, item.component)}
                                        sx={{
                                            textTransform: "none",
                                            justifyContent: "flex-start",
                                            width: "100%",
                                            borderColor: "#e0e0e0",
                                            "&:hover": {
                                                borderColor: "primary.main",
                                                backgroundColor: "rgba(25, 118, 210, 0.04)",
                                            },
                                        }}
                                        startIcon={item.icon}
                                        size="small"
                                    >
                                        {item.name}
                                    </Button>
                                </Tooltip>
                            </Grid>
                        ))}
                    </Grid>
                </Box>
            ))}
        </Paper>
    )
}
