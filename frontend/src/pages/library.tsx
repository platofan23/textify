import { Divider, Grid2, List, ListItem, ListItemButton, Paper, Typography, Button, Box } from "@mui/material"
import React, { useEffect, useState } from "react"
import { User } from "../main"
import { Book } from "../main"
import { loadBooks } from "../components/load_books"
import { BookEditor } from "../components/BookEditor"

export function Library({
    user,
    books,
    setBooks,
}: {
    user: User | null
    books: Book[]
    setBooks: (books: Book[]) => void
}) {
    const [selectedBookId, setSelectedBookId] = useState<string | null>(null)
    const [isEditing, setIsEditing] = useState(false)

    useEffect(() => {
        loadBooks(user, setBooks)
    }, [user, setBooks])

    // Handle book selection for editing
    const handleEditBook = (bookId: string) => {
        setSelectedBookId(bookId)
        setIsEditing(true)
    }

    // Handle creating a new book
    const handleNewBook = () => {
        setSelectedBookId(null)
        setIsEditing(true)
    }

    // Handle saving the book after editing
    const handleSaveBook = (bookContent: any) => {
        // If editing existing book
        if (selectedBookId) {
            const updatedBooks = books.map((book) =>
                book._id === selectedBookId ? { ...book, content: bookContent } : book
            )
            setBooks(updatedBooks)
        }
        // If creating new book
        else {
            const newBook: Book = {
                _id: `book_${Date.now()}`,
                count: 1,
                content: bookContent,
                // Add other required book properties
            }
            setBooks([...books, newBook])
        }

        setIsEditing(false)
    }

    // Return to library view
    const handleCancel = () => {
        setIsEditing(false)
    }

    // Display book editor when editing
    if (isEditing) {
        const currentBook = selectedBookId ? books.find((book) => book._id === selectedBookId) : null

        return (
            <Box sx={{ width: "100%" }}>
                <Button variant="contained" onClick={handleCancel} sx={{ mb: 2 }}>
                    Back to Library
                </Button>

                <BookEditor initialBook={currentBook} onSave={handleSaveBook} />
            </Box>
        )
    }

    // Display library view
    return (
        <>
            <Grid2 sx={{ mt: 5 }} container spacing={2}>
                <Grid2 size={{ xs: 12 }}>
                    <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
                        <Typography variant="h4">Book Library</Typography>
                        <Button variant="contained" color="primary" onClick={handleNewBook}>
                            Create New Book
                        </Button>
                    </Box>
                </Grid2>

                <Grid2 size={{ xs: 12 }}>
                    <Paper sx={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                        <Divider sx={{ width: "100%", mt: 2, mb: 2 }} />
                        <List sx={{ width: "100%", maxWidth: 600 }}>
                            {books.map((book) => (
                                <ListItem key={book._id} disablePadding>
                                    <ListItemButton
                                        sx={{
                                            justifyContent: "space-between",
                                            padding: 2,
                                        }}
                                    >
                                        <Typography>{book._id}</Typography>
                                        <Box>
                                            <Typography sx={{ mr: 2, display: "inline-block" }}>
                                                {"Pages: " + book.count}
                                            </Typography>
                                            <Button
                                                variant="outlined"
                                                size="small"
                                                onClick={() => handleEditBook(book._id)}
                                            >
                                                Edit
                                            </Button>
                                        </Box>
                                    </ListItemButton>
                                </ListItem>
                            ))}
                        </List>
                    </Paper>
                </Grid2>
            </Grid2>
        </>
    )
}
