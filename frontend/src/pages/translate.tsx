import React, { useEffect, useRef, useState } from "react"
import { Alert, Box, Button, Grid2, MenuItem, Select, Typography, Slider } from "@mui/material"
import Editor from "../components/component_editor_translate"
import Quill, { RangeStatic, DeltaStatic } from "quill"
import streamText from "../components/text_stream"
import { useRecorder } from "../components/recording/Recorder"

const Delta = Quill.import("delta")

const Translate = () => {
    const [range, setRange] = useState<RangeStatic | null>(null)
    const [lastChange, setLastChange] = useState<DeltaStatic | null>(null)
    const [readOnly, setReadOnly] = useState<boolean>(false)

    // Use a ref to access the quill instance directly
    const quillRefInput = useRef<Quill | null>(null)
    const quillRefOutput = useRef<Quill | null>(null)
    const audioRef = useRef<HTMLAudioElement | null>(null) // Add ref to track audio element
    const [readBlock, setReadBlock] = useState<boolean>(false)
    const [text, setText] = useState<string>("")
    const [LanguageError, setLanguageError] = useState<boolean>(false)
    const [sourcelanguage, setSourcelanguage] = useState<string>("de")
    const [targetlanguage, setTargetlanguage] = useState<string>("en")
    const [volume, setVolume] = useState<number>(1.0)
    const [readButton, setReadButton] = useState<
        "inherit" | "error" | "primary" | "secondary" | "info" | "success" | "warning"
    >("primary")

    // TTS States
    const [speaker, setSpeaker] = useState<string>("Claribel Dervla")
    const [speakers, setSpeakers] = useState<string[]>([])

    // Recorder
    const { isRecording, recordingTime, recordedAudio, handleRecordButtonClick } = useRecorder({
        quillRefInput,
        sourcelanguage,
    })

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

    // TTS
    useEffect(() => {
        fetch("https://localhost:5558/tts/speakers")
            .then((res) => res.json())
            .then((data) => {
                if (data.speakers && Array.isArray(data.speakers)) {
                    setSpeakers(data.speakers)
                }
            })
            .catch((error) => {
                console.error("Failed to fetch speakers:", error)
            })
    }, [])

    useEffect(() => {
        quillRefOutput.current?.setText(text)
    }, [text])

    // Read translated text using TTS
    function readTranslatedText() {
        // If audio is currently playing, stop it
        if (readBlock) {
            if (audioRef.current) {
                audioRef.current.pause()
                audioRef.current.remove()
            }
            setReadButton("primary")
            setReadBlock(false)
            return
        }

        if (quillRefOutput.current?.getText() == null) {
            setReadButton("error")
            setTimeout(() => {
                setReadButton("primary")
            }, 1000)
            return
        }

        if (quillRefOutput.current?.getText() !== null) {
            setReadButton("secondary")
            setReadBlock(true)
        }

        const textToRead = quillRefOutput.current?.getText().slice(0, -1)
        const requestData = {
            data: {
                text: textToRead,
                model: "tts_models/multilingual/multi-dataset/xtts_v2",
                language: targetlanguage,
                speaker: speaker, // Use the selected speaker from state
            },
        }

        fetch("https://localhost:5558/tts", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(requestData),
        })
            .then((res) => res.blob())
            .then((blob) => {
                const audioURL = URL.createObjectURL(blob)
                const audio = new Audio(audioURL)
                audioRef.current = audio // Store reference to audio element
                audio.volume = volume
                audio.play()
                audio.onended = () => {
                    setReadButton("primary")
                    setReadBlock(false)
                    audioRef.current = null
                }
            })
            .catch((error) => {
                console.error("TTS request failed:", error)
                setReadButton("primary")
                setReadBlock(false)
            })
    }

    async function translateText() {
        setText("")
        streamText(appendText, quillRefInput.current?.getText().split("\n"), sourcelanguage, targetlanguage)
    }

    // Clean up audio on component unmount
    useEffect(() => {
        return () => {
            if (audioRef.current) {
                audioRef.current.pause()
                audioRef.current = null
            }
        }
    }, [])

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
                    {/*Record button */}
                    <Button
                        onClick={handleRecordButtonClick}
                        variant="contained"
                        size="large"
                        color={isRecording ? "error" : "secondary"}
                        sx={{
                            minWidth: 150,
                            fontWeight: 600,
                            textTransform: "none",
                        }}
                    >
                        {isRecording ? `Recording (${recordingTime}s)` : " Record Voice WIP"}
                    </Button>
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
                        {readBlock ? "Stop" : "Read"}
                    </Button>
                </Grid2>
                {/* Speaker Selection */}
                <Grid2
                    size={{ xs: 12 }}
                    sx={{ mt: 2, display: "flex", alignItems: "center", justifyContent: "center" }}
                >
                    <Typography variant="body2" sx={{ mr: 2, minWidth: "80px" }}>
                        Speaker:
                    </Typography>
                    <Select
                        value={speaker}
                        onChange={(e) => setSpeaker(e.target.value as string)}
                        size="small"
                        sx={{ maxWidth: 180, minWidth: 150 }}
                        aria-label="Speaker"
                        MenuProps={{
                            PaperProps: {
                                style: {
                                    maxHeight: 300, // Makes the dropdown scrollable
                                },
                            },
                        }}
                    >
                        {speakers.map((speakerName) => (
                            <MenuItem key={speakerName} value={speakerName}>
                                {speakerName}
                            </MenuItem>
                        ))}
                    </Select>
                </Grid2>

                {/* Volume Control */}
                <Grid2
                    size={{ xs: 12 }}
                    sx={{ mt: 2, display: "flex", alignItems: "center", justifyContent: "center" }}
                >
                    <Typography variant="body2" sx={{ mr: 2, minWidth: "60px" }}>
                        Volume: {Math.round(volume * 100)}%
                    </Typography>
                    <Slider
                        value={volume}
                        min={0}
                        max={1}
                        step={0.01}
                        onChange={(_, newValue) => setVolume(newValue as number)}
                        sx={{ maxWidth: 250 }}
                        aria-label="Volume"
                    />
                </Grid2>
            </Grid2>
        </Box>
    )
}

export default Translate
