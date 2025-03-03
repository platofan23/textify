import React, { useState, useEffect, useRef } from "react"
import { Box, Paper } from "@mui/material"
import Quill from "quill"
import "quill/dist/quill.snow.css"

interface PageContentProps {
    content: any
    onChange: (content: any) => void
    isPreview: boolean
}

export const PageContent: React.FC<PageContentProps> = ({ content, onChange, isPreview }) => {
    const editorRef = useRef<HTMLDivElement>(null)
    const quillRef = useRef<Quill | null>(null)

    // Initialize Quill editor
    useEffect(() => {
        if (!editorRef.current) return

        if (!quillRef.current) {
            const quill = new Quill(editorRef.current, {
                theme: "snow",
                modules: {
                    toolbar: [
                        [{ header: [1, 2, 3, 4, 5, 6, false] }],
                        ["bold", "italic", "underline", "strike"],
                        [{ list: "ordered" }, { list: "bullet" }],
                        [{ indent: "-1" }, { indent: "+1" }],
                        [{ align: [] }],
                        ["link", "image"],
                        ["clean"],
                    ],
                },
                placeholder: "Start writing...",
                readOnly: isPreview,
            })

            quillRef.current = quill

            // Set initial content if available
            if (content && content.html) {
                quill.clipboard.dangerouslyPasteHTML(content.html)
            } else if (content && content.text) {
                quill.setText(content.text)
            }

            // Listen for changes
            quill.on("text-change", () => {
                const html = quill.root.innerHTML
                const text = quill.getText()
                onChange({ html, text })
            })
        }

        // Update readonly status when isPreview changes
        if (quillRef.current) {
            quillRef.current.enable(!isPreview)
        }
    }, [isPreview])

    // Update content when it changes from external source
    useEffect(() => {
        if (quillRef.current && content) {
            if (content.html && !quillRef.current.root.innerHTML.includes(content.html)) {
                quillRef.current.clipboard.dangerouslyPasteHTML(content.html)
            }
        }
    }, [content])

    if (isPreview) {
        return (
            <Paper
                elevation={1}
                sx={{
                    padding: 3,
                    minHeight: "500px",
                    backgroundColor: "#fff",
                    border: "1px solid #e0e0e0",
                    "& .ql-editor": {
                        padding: 0,
                        fontFamily: "Georgia, serif",
                        fontSize: "16px",
                        lineHeight: 1.6,
                    },
                }}
            >
                <div ref={editorRef} />
            </Paper>
        )
    }

    return (
        <Box sx={{ height: "100%", "& .ql-container": { height: "calc(100% - 42px)", fontSize: "16px" } }}>
            <div ref={editorRef} />
        </Box>
    )
}
