import React, { useEffect, useRef, useState } from "react"
import Editor from "./component_editor_translate"
import Quill, { RangeStatic, DeltaStatic } from "quill"
import streamText from "./text_stream"
import { Alert, Box, Button, MenuItem, Modal, Select, Typography } from "@mui/material"

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

    async function translateText() {
        setText("")
        streamText(appendText, quillRefInput.current?.getText().split("\n"), sourcelanguage, targetlanguage)
    }

    return (
        <div>
            <Select
                id="input-language"
                value={sourcelanguage}
                label="Input language"
                onChange={(e) => setSourcelanguage(e.target.value)}
            >
                {Language.map((lang) => (
                    <MenuItem value={lang.value}>{lang.label}</MenuItem>
                ))}
            </Select>
            <Select
                id="output-language"
                value={targetlanguage}
                label="Output language"
                onChange={(e) => setTargetlanguage(e.target.value)}
            >
                {Language.map((lang) => (
                    <MenuItem value={lang.value}>{lang.label}</MenuItem>
                ))}
            </Select>
            {LanguageError && (
                <Alert severity="error" onClose={() => setLanguageError(false)}>
                    Error: Translating text from {sourcelanguage} to {targetlanguage} is not supported.
                </Alert>
            )}
            <Editor
                ref={quillRefInput}
                readOnly={readOnly}
                defaultValue={new Delta().insert("", { bold: true, size: "16pt" })}
                onSelectionChange={setRange}
                onTextChange={setLastChange}
            />
            <Editor
                ref={quillRefOutput}
                readOnly={readOnly}
                defaultValue={new Delta().insert("", { bold: true, size: "16pt" })}
                onSelectionChange={setRange}
                onTextChange={setLastChange}
            />

            <Button onClick={translateText}>Translate</Button>
        </div>
    )
}
export default Translate
