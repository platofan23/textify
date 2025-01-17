import { Grid2, Paper, Stack, Typography } from "@mui/material"
import React from "react"

export function Library() {
    const [fileList, setFileList] = React.useState<File[]>([])

    function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
        if (e.target.files) {
            const files = Array.from(e.target.files)
            setFileList(files)
        }
    }

    return (
        <>
            <Grid2 container spacing={2}>
                <Paper>
                    <Typography variant="h4">Library</Typography>

                    <input type="file" multiple onChange={handleFileUpload} />
                    {fileList.map((file, index) => (
                        <section key={file.name}>
                            File number {index + 1} details:
                            <ul>
                                <li>Name: {file.name}</li>
                                <li>Type: {file.type}</li>
                                <li>Size: {file.size} bytes</li>
                            </ul>
                        </section>
                    ))}
                </Paper>
            </Grid2>
        </>
    )
}
