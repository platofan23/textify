import { Divider, Grid2, List, ListItem, ListItemButton, Paper, Typography } from "@mui/material"
import React, { useEffect, useState } from "react"
import { User } from "../main"
import { Book } from "../main"
import { loadBooks } from "../components/load_books"

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

    return (
        <>
            <Grid2 sx={{ mt: 5 }} container spacing={2}>
                <Paper sx={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                    <Typography p={1} variant="h4">
                        Book Library
                    </Typography>
                    <Divider sx={{ width: "100%", mt: 2, mb: 2 }} />
                    <List sx={{ width: "100%", maxWidth: 400 }}>
                        {books.map((book) => (
                            <ListItem key={book._id} disablePadding>
                                <ListItemButton sx={{ justifyContent: "space-between" }}>
                                    <Typography>{book._id}</Typography>
                                    <Typography>{"Pages: " + book.count}</Typography>
                                </ListItemButton>
                            </ListItem>
                        ))}
                    </List>
                </Paper>
            </Grid2>
        </>
    )
}
