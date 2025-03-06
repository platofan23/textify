import { useState, useEffect } from "react"
import { Box, Grid2 } from "@mui/material"
import { Button, Typography, TextField, Grid, Paper, Alert, IconButton } from "@mui/material"
import { CloudUpload, Delete } from "@mui/icons-material"
import { useDropzone, FileWithPath } from "react-dropzone"
import { User } from "../main.tsx"
type FileWithPreview = FileWithPath & { preview: string }

const FileUploadPage = ({ user }: { user: User | null }) => {
    const [title, setTitle] = useState<string>("")
    const [files, setFiles] = useState<FileWithPreview[]>([])
    const [error, setError] = useState<string>("")

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        accept: {
            "image/png": [".png"],
        },
        multiple: true,
        onDrop: (acceptedFiles: File[], rejectedFiles) => {
            if (rejectedFiles.length > 0) {
                setError("Please upload only PNG files")
                return
            }
            setError("")
            setFiles((prev) => [
                ...prev,
                ...acceptedFiles.map((file) =>
                    Object.assign(file, {
                        preview: URL.createObjectURL(file),
                    })
                ),
            ])
        },
    })

    useEffect(() => {
        // Cleanup preview URLs
        return () => files.forEach((file) => URL.revokeObjectURL(file.preview))
    }, [files])

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        if (!title) {
            setError("Please enter a book title")
            return
        }
        if (files.length === 0) {
            setError("Please upload at least one page")
            return
        }

        // Upload the book
        const formData = new FormData()

        files.forEach((file) => formData.append("Files", file))

        fetch("http://localhost:5558/upload_files", {
            method: "POST",
            headers: {
                // Let the browser set the correct boundary for multipart/form-data automatically
                // "Content-Type": "multipart/form-data",
                User: user?.Username ?? "",
                Title: title,
            },
            body: formData,
        })

        // Reset form
        setTitle("")
        setFiles([])
        setError("")
    }

    const removeFile = (fileName: string) => {
        setFiles((prev) => prev.filter((file) => file.name !== fileName))
    }

    return (
        <Box sx={{ maxWidth: 800, mx: "auto", p: 3 }}>
            <Typography variant="h4" gutterBottom>
                Upload a Book
            </Typography>

            <form onSubmit={handleSubmit}>
                <TextField
                    fullWidth
                    label="Book Title"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    margin="normal"
                    required
                />

                <Paper
                    variant="outlined"
                    sx={{
                        p: 3,
                        mt: 2,
                        borderStyle: "dashed",
                        backgroundColor: isDragActive ? "action.hover" : "background.paper",
                    }}
                    {...getRootProps()}
                >
                    <input {...getInputProps()} />
                    <Box textAlign="center">
                        <CloudUpload fontSize="large" />
                        <Typography>
                            {isDragActive ? "Drop the files here" : "Drag & drop pages here, or click to select"}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                            (PNG files only)
                        </Typography>
                    </Box>
                </Paper>

                {error && (
                    <Alert severity="error" sx={{ mt: 2 }}>
                        {error}
                    </Alert>
                )}

                <Grid2 container spacing={2} sx={{ mt: 2 }}>
                    {files.map((file) => (
                        <Grid2 columns={{ xs: 3, sm: 4 }} key={file.name}>
                            <Paper sx={{ p: 1, position: "relative" }}>
                                <img
                                    src={file.preview}
                                    alt={file.name}
                                    style={{ width: "100%", height: 150, objectFit: "contain" }}
                                />
                                <IconButton
                                    size="small"
                                    onClick={() => removeFile(file.name)}
                                    sx={{
                                        position: "absolute",
                                        top: 4,
                                        right: 4,
                                        backgroundColor: "background.paper",
                                    }}
                                >
                                    <Delete fontSize="small" />
                                </IconButton>
                            </Paper>
                        </Grid2>
                    ))}
                </Grid2>

                <Button type="submit" variant="contained" size="large" fullWidth sx={{ mt: 3 }}>
                    Upload Book
                </Button>
            </form>
        </Box>
    )
}

export default FileUploadPage
