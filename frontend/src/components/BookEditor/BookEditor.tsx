import React, { useState, useEffect } from "react"
import {
    Box,
    Paper,
    Typography,
    Button,
    AppBar,
    Toolbar,
    Tabs,
    Tab,
    IconButton,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
} from "@mui/material"
import AddIcon from "@mui/icons-material/Add"
import DeleteIcon from "@mui/icons-material/Delete"
import VisibilityIcon from "@mui/icons-material/Visibility"
import EditIcon from "@mui/icons-material/Edit"
import DownloadIcon from "@mui/icons-material/Download"
import { PageContent } from "./PageContent"
import { EditorToolbar } from "./EditorToolbar"
import { exportToHtml } from "../HtmlExport/exportToHtml"

interface Page {
    id: string
    title: string
    content: any
}

interface BookEditorProps {
    initialBook: any | null
    onSave: (bookContent: any) => void
}

const BookEditor: React.FC<BookEditorProps> = ({ initialBook, onSave }) => {
    const [pages, setPages] = useState<Page[]>([])
    const [currentPageIndex, setCurrentPageIndex] = useState(0)
    const [isPreviewMode, setIsPreviewMode] = useState(false)
    const [showPageDialog, setShowPageDialog] = useState(false)
    const [newPageTitle, setNewPageTitle] = useState("")

    // Initialize book content
    useEffect(() => {
        if (initialBook && initialBook.content && initialBook.content.pages) {
            setPages(initialBook.content.pages)
        } else {
            // Create default first page if new book
            setPages([
                {
                    id: `page_${Date.now()}`,
                    title: "Page 1",
                    content: {
                        blocks: [],
                        elements: [],
                    },
                },
            ])
        }
    }, [initialBook])

    const handlePageChange = (event: React.SyntheticEvent, newValue: number) => {
        setCurrentPageIndex(newValue)
    }

    const handleContentChange = (content: any) => {
        const updatedPages = [...pages]
        updatedPages[currentPageIndex].content = content
        setPages(updatedPages)
    }

    const handleAddPage = () => {
        setShowPageDialog(true)
    }

    const handleCreatePage = () => {
        const newPage: Page = {
            id: `page_${Date.now()}`,
            title: newPageTitle || `Page ${pages.length + 1}`,
            content: {
                blocks: [],
                elements: [],
            },
        }

        setPages([...pages, newPage])
        setCurrentPageIndex(pages.length)
        setShowPageDialog(false)
        setNewPageTitle("")
    }

    const handleDeletePage = (index: number) => {
        if (pages.length <= 1) {
            return // Prevent deleting the last page
        }

        const updatedPages = pages.filter((_, i) => i !== index)
        setPages(updatedPages)

        if (currentPageIndex >= updatedPages.length) {
            setCurrentPageIndex(updatedPages.length - 1)
        }
    }

    const handleSaveBook = () => {
        const bookContent = {
            pages: pages,
            metadata: {
                lastUpdated: new Date().toISOString(),
                pageCount: pages.length,
            },
        }
        onSave(bookContent)
    }

    const handleExportHtml = () => {
        const html = exportToHtml(pages)

        // Create a download link for the HTML file
        const blob = new Blob([html], { type: "text/html" })
        const url = URL.createObjectURL(blob)
        const a = document.createElement("a")
        a.href = url
        a.download = `${initialBook?._id || "book"}.html`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
    }

    const currentPage = pages[currentPageIndex] || null

    return (
        <Box sx={{ display: "flex", flexDirection: "column", height: "100%" }}>
            <AppBar position="static" color="default">
                <Toolbar>
                    <Typography variant="h6" sx={{ flexGrow: 0, mr: 2 }}>
                        {initialBook ? `Editing: ${initialBook._id}` : "New Book"}
                    </Typography>

                    <Box sx={{ flexGrow: 1 }}>
                        <Tabs
                            value={currentPageIndex}
                            onChange={handlePageChange}
                            variant="scrollable"
                            scrollButtons="auto"
                        >
                            {pages.map((page, index) => (
                                <Tab
                                    key={page.id}
                                    label={
                                        <Box sx={{ display: "flex", alignItems: "center" }}>
                                            {page.title}
                                            <IconButton
                                                size="small"
                                                onClick={(e) => {
                                                    e.stopPropagation()
                                                    handleDeletePage(index)
                                                }}
                                                sx={{ ml: 1 }}
                                            >
                                                <DeleteIcon fontSize="small" />
                                            </IconButton>
                                        </Box>
                                    }
                                />
                            ))}
                        </Tabs>
                    </Box>

                    <IconButton onClick={handleAddPage} color="primary">
                        <AddIcon />
                    </IconButton>

                    <IconButton onClick={() => setIsPreviewMode(!isPreviewMode)} color="primary" sx={{ ml: 1 }}>
                        {isPreviewMode ? <EditIcon /> : <VisibilityIcon />}
                    </IconButton>

                    <IconButton onClick={handleExportHtml} color="primary" sx={{ ml: 1 }}>
                        <DownloadIcon />
                    </IconButton>

                    <Button variant="contained" color="primary" onClick={handleSaveBook} sx={{ ml: 2 }}>
                        Save Book
                    </Button>
                </Toolbar>
            </AppBar>

            {currentPage && (
                <Paper
                    elevation={3}
                    sx={{
                        flex: 1,
                        m: 2,
                        p: 2,
                        minHeight: "600px",
                        display: "flex",
                        flexDirection: "column",
                    }}
                >
                    <Typography variant="h5" sx={{ mb: 2 }}>
                        {currentPage.title}
                    </Typography>

                    {!isPreviewMode && <EditorToolbar />}

                    <Box sx={{ flex: 1, mt: 2 }}>
                        <PageContent
                            content={currentPage.content}
                            onChange={handleContentChange}
                            isPreview={isPreviewMode}
                        />
                    </Box>
                </Paper>
            )}

            {/* Dialog for adding new page */}
            <Dialog open={showPageDialog} onClose={() => setShowPageDialog(false)}>
                <DialogTitle>Add New Page</DialogTitle>
                <DialogContent>
                    <TextField
                        autoFocus
                        margin="dense"
                        label="Page Title"
                        fullWidth
                        variant="outlined"
                        value={newPageTitle}
                        onChange={(e) => setNewPageTitle(e.target.value)}
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setShowPageDialog(false)}>Cancel</Button>
                    <Button onClick={handleCreatePage} variant="contained">
                        Create
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    )
}

export default BookEditor
