import React, { forwardRef, useEffect, useLayoutEffect, useRef } from "react"
import Quill from "quill"
import "quill/dist/quill.bubble.css" // Import Quill styles
import { Sick } from "@mui/icons-material"
// Editor is an uncontrolled React component
const Editor = forwardRef(({ readOnly, defaultValue, onTextChange, onSelectionChange }, ref) => {
    const containerRef = useRef(null)
    const defaultValueRef = useRef(defaultValue)
    const onTextChangeRef = useRef(onTextChange)
    const onSelectionChangeRef = useRef(onSelectionChange)

    useLayoutEffect(() => {
        onTextChangeRef.current = onTextChange
        onSelectionChangeRef.current = onSelectionChange
    })

    useEffect(() => {
        ref.current?.enable(!readOnly)
    }, [ref, readOnly])

    useEffect(() => {
        const container = containerRef.current

        const editorContainer = container.appendChild(container.ownerDocument.createElement("div"))

        const fontSizeArr = [
            "8pt",
            "9pt",
            "10pt",
            "12pt",
            "14pt",
            "16pt",
            "20pt",
            "24pt",
            "32pt",
            "42pt",
            "54pt",
            "68pt",
            "84pt",
            "98pt",
        ]

        var Size = Quill.import("attributors/style/size")
        Size.whitelist = fontSizeArr
        Quill.register(Size, true)

        const toolbarOptions = [[{ font: [] }], [{ size: fontSizeArr }], ["bold", "italic", "underline", "strike"]]
        const quill = new Quill(editorContainer, {
            theme: "bubble",
            modules: {
                toolbar: toolbarOptions,
            },
        })

        ref.current = quill

        if (defaultValueRef.current) {
            quill.setContents(defaultValueRef.current)
        }

        quill.on(Quill.events.TEXT_CHANGE, (...args) => {
            onTextChangeRef.current?.(...args)
            console.log(quill.getContents())
        })

        quill.on(Quill.events.SELECTION_CHANGE, (...args) => {
            onSelectionChangeRef.current?.(...args)
        })

        return () => {
            ref.current = null
            container.innerHTML = ""
        }
    }, [ref])

    return (
        <>
            <style>{`
            
            .ql-snow .ql-picker.ql-size .ql-picker-label::before,
            .ql-snow .ql-picker.ql-size .ql-picker-item::before {
                content: attr(data-value) !important;
            }
        `}</style>
            <div ref={containerRef}></div>
        </>
    )
})

Editor.displayName = "Editor"

export default Editor
