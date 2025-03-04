import {
    Divider,
    Grid2,
    List,
    ListItem,
    ListItemButton,
    Paper,
    Typography,
    Button,
    Box,
    Tab,
    Tabs,
} from "@mui/material"
import React, { useEffect, useState } from "react"
import { User } from "../main"
import { Book } from "../main"
import { loadBooks } from "../components/load_books"
import { Editor, Frame, Element } from "@craftjs/core"
import { Text } from "../components/editor/user-components/Text.tsx"
import { Container } from "../components/editor/user-components/Container.tsx"
import { Image } from "../components/editor/user-components/Image.tsx"
import { Heading } from "../components/editor/user-components/Heading.tsx"
import { Toolbox } from "../components/editor/Toolbox.tsx"
import { SettingsPanel } from "../components/editor/SettingsPanel.tsx"
import { exportHtml } from "../utils/exportHtml.tsx"

export function Library({
    user,
    books,
    setBooks,
}: {
    user: User | null
    books: Book[]
    setBooks: (fn: Book[]) => void
}) {
    useEffect(() => {
        loadBooks(user, setBooks)
        console.log(books)
    }, [])

    const [selectedBook, setSelectedBook] = useState<string | null>(null)
    const [currentPage, setCurrentPage] = useState<number>(1)
    const [bookPages, setBookPages] = useState<Record<string, any>>({})
    const [tabValue, setTabValue] = useState<number>(0)

    // Handle book selection
    const handleBookSelect = (bookId: string) => {
        setSelectedBook(bookId)
        setTabValue(0) // Switch to editor tab
        // Load existing book content if available
        if (!bookPages[bookId]) {
            setBookPages((prev) => ({
                ...prev,
                [bookId]: { pages: { 1: {} } },
            }))
        }
    }

    // Handle page change
    const handlePageChange = (pageNum: number) => {
        setCurrentPage(pageNum)
    }

    // Add new page
    const addNewPage = () => {
        if (selectedBook) {
            const newPageNum = Object.keys(bookPages[selectedBook].pages).length + 1
            setBookPages((prev) => ({
                ...prev,
                [selectedBook]: {
                    ...prev[selectedBook],
                    pages: {
                        ...prev[selectedBook].pages,
                        [newPageNum]: {},
                    },
                },
            }))
            setCurrentPage(newPageNum)
        }
    }

    // Export book to HTML
    const handleExportHtml = () => {
        if (selectedBook) {
            try {
                console.log("Book data for export:", bookPages[selectedBook])
                const html = exportHtml(bookPages[selectedBook])
                const blob = new Blob([html], { type: "text/html" })
                const url = URL.createObjectURL(blob)
                const a = document.createElement("a")
                a.href = url
                a.download = `${selectedBook}.html`
                a.click()
                URL.revokeObjectURL(url)
            } catch (error) {
                console.error("Export failed:", error)
                alert("Export failed. Check the console for details.")
            }
        }
    }

    const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
        setTabValue(newValue)
    }

    return (
        <>
            <Grid2 container spacing={2} sx={{ mt: 5 }}>
                {/* Book List */}
                <Grid2 size={{ xs: 12 }} sx={{ md: 3 }}>
                    <Paper sx={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                        <Typography p={1} variant="h4">
                            Book Library
                        </Typography>
                        <Divider sx={{ width: "100%", mt: 2, mb: 2 }} />
                        <List sx={{ width: "100%" }}>
                            {books.map((book) => (
                                <ListItem key={book._id} disablePadding>
                                    <ListItemButton
                                        sx={{ justifyContent: "space-between" }}
                                        onClick={() => handleBookSelect(book._id)}
                                        selected={selectedBook === book._id}
                                    >
                                        <Typography>{book._id}</Typography>
                                        <Typography>{"Pages: " + book.count}</Typography>
                                    </ListItemButton>
                                </ListItem>
                            ))}
                        </List>
                    </Paper>
                </Grid2>

                {/* Editor Area */}
                {selectedBook && (
                    <Grid2 size={{ xs: 12 }} sx={{ md: 9 }}>
                        <Paper sx={{ p: 2, minHeight: "600px" }}>
                            <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 2 }}>
                                <Tabs value={tabValue} onChange={handleTabChange}>
                                    <Tab label="Editor" />
                                    <Tab label="Preview" />
                                </Tabs>
                            </Box>

                            <Box sx={{ display: tabValue === 0 ? "block" : "none" }}>
                                <Typography variant="h5" gutterBottom>
                                    Editing: {selectedBook} - Page {currentPage}
                                </Typography>

                                <Editor
                                    resolver={{
                                        Text,
                                        Container,
                                        Image,
                                        Heading,
                                    }}
                                    onNodesChange={(query) => {
                                        // Save editor state when nodes change
                                        if (selectedBook) {
                                            console.log("Saving editor state...")
                                            console.log(query.getNodes())
                                            const json = query.serialize()
                                            setBookPages((prev) => ({
                                                ...prev,
                                                [selectedBook]: {
                                                    ...prev[selectedBook],
                                                    pages: {
                                                        ...prev[selectedBook].pages,
                                                        [currentPage]: json,
                                                    },
                                                },
                                            }))
                                        }
                                    }}
                                >
                                    <Box sx={{ display: "flex" }}>
                                        <Box
                                            sx={{
                                                width: "70%",
                                                p: 2,
                                                border: "1px solid #ccc",
                                                minHeight: "500px",
                                                position: "relative",
                                            }}
                                        >
                                            <Frame>
                                                <Element is={Container} canvas>
                                                    <Heading text="Book Page Title" />
                                                    <Text text="Start typing your book content here..." />
                                                </Element>
                                            </Frame>
                                        </Box>
                                        <Box sx={{ width: "30%" }}>
                                            <Toolbox />
                                            <SettingsPanel />
                                        </Box>
                                    </Box>

                                    <Box sx={{ mt: 2, display: "flex", justifyContent: "space-between" }}>
                                        <Box>
                                            <Button
                                                variant="outlined"
                                                onClick={() => handlePageChange(Math.max(1, currentPage - 1))}
                                                disabled={currentPage <= 1}
                                            >
                                                Previous Page
                                            </Button>
                                            <Button
                                                variant="outlined"
                                                onClick={() => handlePageChange(currentPage + 1)}
                                                sx={{ ml: 1 }}
                                            >
                                                Next Page
                                            </Button>
                                            <Button variant="outlined" onClick={addNewPage} sx={{ ml: 1 }}>
                                                Add Page
                                            </Button>
                                        </Box>
                                        <Button variant="contained" color="primary" onClick={handleExportHtml}>
                                            Export HTML
                                        </Button>
                                    </Box>
                                </Editor>
                            </Box>

                            <Box sx={{ display: tabValue === 1 ? "block" : "none" }}>
                                <Typography variant="h5" gutterBottom>
                                    Preview: {selectedBook}
                                </Typography>
                                <Box
                                    sx={{
                                        border: "1px solid #ccc",
                                        p: 2,
                                        minHeight: "500px",
                                        bgcolor: "#fff",
                                    }}
                                    dangerouslySetInnerHTML={{
                                        __html:
                                            selectedBook && bookPages[selectedBook]?.pages[currentPage]
                                                ? exportHtml({
                                                      pages: {
                                                          [currentPage]: bookPages[selectedBook].pages[currentPage],
                                                      },
                                                  })
                                                : "<p>No content to preview</p>",
                                    }}
                                />
                            </Box>
                        </Paper>
                    </Grid2>
                )}
            </Grid2>
        </>
    )
}
