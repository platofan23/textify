import React, { useEffect, useRef, useState } from "react"
import Editor from "./component_editor_translate"
import Quill, { RangeStatic, DeltaStatic } from "quill"
import streamText from "./text_stream"
import { Alert, Box, Button, Grid2, MenuItem, Modal, Select, Typography } from "@mui/material"

const Delta = Quill.import("delta")

const Translate = () => {
    const [range, setRange] = useState<RangeStatic | null>(null)
    const [lastChange, setLastChange] = useState<DeltaStatic | null>(null)
    const [readOnly, setReadOnly] = useState<boolean>(false)

    // Use a ref to access the quill instance directly
    const quillRefInput = useRef<Quill | null>(null)
    const quillRefOutput = useRef<Quill | null>(null)

    const [text, setText] = useState<string>("")
    const [LanguageError, setLanguageError] = useState<boolean>(false)
    const [sourcelanguage, setSourcelanguage] = useState<string>("de")
    const [targetlanguage, setTargetlanguage] = useState<string>("en")
    const [readButton, setReadButton] = useState<
        "inherit" | "error" | "primary" | "secondary" | "info" | "success" | "warning"
    >("primary")
    const Language = [
        { value: "de", label: "German" },
        { value: "en", label: "English" },
        { value: "es", label: "Spanish" },
        { value: "fr", label: "French" },
        { value: "it", label: "Italian" },
        { value: "jap", label: "Japanese" },
        { value: "ko", label: "Korean" },
        { value: "nl", label: "Dutch" },
        { value: "pl", label: "Polish" },
        { value: "pt", label: "Portuguese" },
        { value: "ru", label: "Russian" },
        { value: "zh", label: "Chinese" },
    ]

    const appendText = (newText: string | undefined) => {
        if (newText === undefined) {
            setLanguageError(true)

            return
        }
        setText((prevText) => prevText + newText)
    }

    useEffect(() => {
        quillRefOutput.current?.setText(text)
    }, [text])

    function readTranslatedText() {
        if (quillRefOutput.current?.getText() !== null) {
            setReadButton("error")
            setTimeout(() => {
                setReadButton("primary")
            }, 1000)
        }

        let textToRead = quillRefOutput.current?.getText()
    }

    async function translateText() {
        setText("")
        streamText(appendText, quillRefInput.current?.getText().split("\n"), sourcelanguage, targetlanguage)
    }

    return (
        <Box
            sx={{
                p: 3,
                maxWidth: 1200,
                mx: "auto",
                bgcolor: "background.paper",
                borderRadius: 2,
                boxShadow: 3,
            }}
        >
            <Typography variant="h4" gutterBottom sx={{ mb: 3, fontWeight: 500 }}>
                Text Translator
            </Typography>

            {LanguageError && (
                <Alert severity="error" onClose={() => setLanguageError(false)} sx={{ mb: 3 }}>
                    Error: Translating text from {sourcelanguage} to {targetlanguage} is not supported.
                </Alert>
            )}

            <Grid2 container spacing={3}>
                {/* Language Selection */}
                <Grid2 size={{ xs: 12 }}>
                    <Box
                        sx={{
                            display: "flex",
                            alignItems: "center",
                            gap: 2,
                            mb: 2,
                            flexWrap: "wrap",
                        }}
                    >
                        <Box sx={{ minWidth: 200 }}>
                            <Typography variant="body2" color="text.secondary" mb={0.5}>
                                Source Language
                            </Typography>
                            <Select
                                fullWidth
                                id="input-language"
                                value={sourcelanguage}
                                size="small"
                                onChange={(e) => setSourcelanguage(e.target.value)}
                            >
                                {Language.map((lang) => (
                                    <MenuItem key={lang.value} value={lang.value}>
                                        {lang.label}
                                    </MenuItem>
                                ))}
                            </Select>
                        </Box>

                        <Box
                            sx={{
                                display: "flex",
                                alignItems: "center",
                                color: "text.secondary",
                                mx: 2,
                            }}
                        >
                            <Typography>→</Typography>
                        </Box>

                        <Box sx={{ minWidth: 200 }}>
                            <Typography variant="body2" color="text.secondary" mb={0.5}>
                                Target Language
                            </Typography>
                            <Select
                                fullWidth
                                id="output-language"
                                value={targetlanguage}
                                size="small"
                                onChange={(e) => setTargetlanguage(e.target.value)}
                            >
                                {Language.map((lang) => (
                                    <MenuItem key={lang.value} value={lang.value}>
                                        {lang.label}
                                    </MenuItem>
                                ))}
                            </Select>
                        </Box>
                    </Box>
                </Grid2>

                {/* Editors */}
                <Grid2 size={{ xs: 12, md: 6 }}>
                    <Typography variant="body1" fontWeight={500} mb={1}>
                        Original Text
                    </Typography>
                    <Box
                        sx={{
                            height: 300,
                            border: "1px solid #e0e0e0",
                            borderRadius: 1,
                            "& .ql-container": { borderRadius: "0 0 4px 4px" },
                            "& .ql-toolbar": { borderRadius: "4px 4px 0 0" },
                        }}
                    >
                        <Editor
                            ref={quillRefInput}
                            readOnly={readOnly}
                            defaultValue={new Delta().insert("", { bold: true, size: "16pt" })}
                            onSelectionChange={setRange}
                            onTextChange={setLastChange}
                        />
                    </Box>
                </Grid2>

                <Grid2 size={{ xs: 12, md: 6 }}>
                    <Typography variant="body1" fontWeight={500} mb={1}>
                        Translated Text
                    </Typography>
                    <Box
                        sx={{
                            height: 300,
                            border: "1px solid #e0e0e0",
                            borderRadius: 1,
                            bgcolor: "rgba(0, 0, 0, 0.01)",
                            "& .ql-container": { borderRadius: "0 0 4px 4px" },
                            "& .ql-toolbar": { borderRadius: "4px 4px 0 0" },
                        }}
                    >
                        <Editor
                            ref={quillRefOutput}
                            readOnly={true}
                            defaultValue={new Delta().insert("", { bold: true, size: "16pt" })}
                            onSelectionChange={setRange}
                            onTextChange={setLastChange}
                        />
                    </Box>
                </Grid2>

                {/* Action Buttons */}
                <Grid2
                    container
                    size={{ xs: 12 }}
                    columnSpacing={1}
                    sx={{ mt: 2, display: "flex", justifyContent: "center" }}
                >
                    <Button
                        onClick={translateText}
                        variant="contained"
                        size="large"
                        sx={{
                            minWidth: 150,
                            fontWeight: 600,
                            textTransform: "none",
                        }}
                    >
                        Translate
                    </Button>
                    <Button
                        onClick={readTranslatedText}
                        variant="contained"
                        size="large"
                        sx={{
                            minWidth: 150,
                            fontWeight: 600,
                            textTransform: "none",
                        }}
                        color={readButton}
                    >
                        Read
                    </Button>
                </Grid2>
            </Grid2>
        </Box>
    )
}
export default Translate
