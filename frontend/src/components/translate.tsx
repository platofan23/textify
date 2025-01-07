import React, { useEffect, useRef, useState } from "react"
import Editor from "./Editor"
import Quill, { RangeStatic, DeltaStatic } from "quill"
import streamText from "./text_stream"
import { Button } from "@mui/material"

const Delta = Quill.import("delta")

const Translate = () => {
    const [range, setRange] = useState<RangeStatic | null>(null)
    const [lastChange, setLastChange] = useState<DeltaStatic | null>(null)
    const [readOnly, setReadOnly] = useState<boolean>(false)

    // Use a ref to access the quill instance directly
    const quillRefInput = useRef<Quill | null>(null)
    const quillRefOutput = useRef<Quill | null>(null)

    const [text, setText] = useState<string>("")

    const appendText = (newText: string) => {
        setText((prevText) => prevText + newText)
    }

    useEffect(() => {
        quillRefOutput.current?.setText(text)
    }, [text])

    async function translateText() {
        setText("")
        streamText(appendText, quillRefInput.current?.getText().split("\n"))
    }

    return (
        <div>
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
