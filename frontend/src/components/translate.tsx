import React, { useRef, useState } from "react"
import Editor from "./component_editor_translate"
import Quill, { RangeStatic, DeltaStatic } from "quill"
import { Grid2 } from "@mui/material"

const Delta = Quill.import("delta")

const Translate = () => {
    const [range, setRange] = useState<RangeStatic | null>(null)
    const [lastChange, setLastChange] = useState<DeltaStatic | null>(null)
    const [readOnly, setReadOnly] = useState<boolean>(false)

    // Use a ref to access the quill instance directly
    const quillRef = useRef<Quill | null>(null)

    return (
        <Grid2 container spacing={4}>
            <Grid2 size={5}>
                <Editor
                    ref={quillRef}
                    readOnly={readOnly}
                    defaultValue={new Delta().insert("Hello World!", { bold: true, size: "16pt" })}
                    onSelectionChange={setRange}
                    onTextChange={setLastChange}
                />
            </Grid2>
            <Grid2 sx={{ border: "solid red 1px" }} size={5}>
                <Editor
                    ref={quillRef}
                    readOnly={readOnly}
                    defaultValue={new Delta().insert("Hello World2!", { bold: true, size: "16pt" })}
                    onSelectionChange={setRange}
                    onTextChange={setLastChange}
                />
            </Grid2>
        </Grid2>
    )
}
export default Translate
