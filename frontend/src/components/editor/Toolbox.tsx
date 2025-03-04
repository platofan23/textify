import React from "react"
import { Box, Typography, Button, Divider } from "@mui/material"
import { useEditor } from "@craftjs/core"
import { Text } from "./user-components/Text.tsx"
import { Container } from "./user-components/Container.tsx"
import { Image } from "./user-components/Image.tsx"
import { Heading } from "./user-components/Heading.tsx"

export const Toolbox = () => {
    const { connectors } = useEditor()

    return (
        <Box sx={{ p: 2, border: "1px solid #e0e0e0", borderRadius: 1, mb: 2 }}>
            <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                Elements
            </Typography>
            <Divider sx={{ mb: 2 }} />

            <Box sx={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 1 }}>
                <Button
                    variant="outlined"
                    ref={(ref) => connectors.create(ref!, <Heading text="Heading" />)}
                    sx={{ textTransform: "none" }}
                >
                    Heading
                </Button>

                <Button
                    variant="outlined"
                    ref={(ref) => connectors.create(ref!, <Text text="Text block" />)}
                    sx={{ textTransform: "none" }}
                >
                    Text
                </Button>

                <Button
                    variant="outlined"
                    ref={(ref) => connectors.create(ref!, <Image />)}
                    sx={{ textTransform: "none" }}
                >
                    Image
                </Button>

                <Button
                    variant="outlined"
                    ref={(ref) =>
                        connectors.create(
                            ref!,
                            <Container>
                                <Text text="Container content" />
                            </Container>
                        )
                    }
                    sx={{ textTransform: "none" }}
                >
                    Container
                </Button>
            </Box>
        </Box>
    )
}
