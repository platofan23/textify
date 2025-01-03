import React, { useRef, useState } from "react"
import Editor from "./Editor"
import Quill, { RangeStatic, DeltaStatic } from "quill"

const Delta = Quill.import("delta")

const Translate = () => {
    const [range, setRange] = useState<RangeStatic | null>(null)
    const [lastChange, setLastChange] = useState<DeltaStatic | null>(null)
    const [readOnly, setReadOnly] = useState<boolean>(false)

    // Use a ref to access the quill instance directly
    const quillRef = useRef<Quill | null>(null)

    return (
        <div>
            <Editor
                ref={quillRef}
                readOnly={readOnly}
                defaultValue={new Delta().insert("Hello World!", { bold: true, size: "16pt" })}
                onSelectionChange={setRange}
                onTextChange={setLastChange}
            />
        </div>
    )
}
export default Translate
