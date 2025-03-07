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
    CircularProgress,
    Alert,
    Menu,
    MenuItem,
} from "@mui/material"
import React, { useEffect, useState } from "react"
import { User } from "../main"
import { Book } from "../main"
import { loadBooks } from "../components/load_books"
import { Editor, Frame, Element, deserialize } from "@craftjs/core"
import { Text } from "../components/editor/user-components/Text.tsx"
import { Container } from "../components/editor/user-components/Container.tsx"
import { Image } from "../components/editor/user-components/Image.tsx"
import { Heading } from "../components/editor/user-components/Heading.tsx"
import { Toolbox } from "../components/editor/Toolbox.tsx"
import { SettingsPanel } from "../components/editor/SettingsPanel.tsx"
import { exportHtml } from "../utils/exportHtml.tsx"
import { getTranslationLanguages, useBookTranslations } from "../components/library_functions/get_book_translations.ts"

// Define prop and state types for ErrorBoundary
interface ErrorBoundaryProps {
    children: React.ReactNode
    onReset?: () => void
}

interface ErrorBoundaryState {
    hasError: boolean
    error: Error | null
}

// Error boundary component
class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
    constructor(props: ErrorBoundaryProps) {
        super(props)
        this.state = { hasError: false, error: null }
    }

    static getDerivedStateFromError(error: Error) {
        return { hasError: true, error }
    }

    componentDidCatch(error, info) {
        console.error("Editor error:", error, info)
    }

    render() {
        if (this.state.hasError) {
            return (
                <Box sx={{ p: 3, textAlign: "center" }}>
                    <Alert severity="error">An error occurred in the editor. Try resetting the page.</Alert>
                    <Button
                        variant="outlined"
                        sx={{ mt: 2 }}
                        onClick={() => {
                            this.setState({ hasError: false })
                            this.props.onReset?.()
                        }}
                    >
                        Reset
                    </Button>
                </Box>
            )
        }
        return this.props.children
    }
}

export function Library({
    user,
    books,
    setBooks,
}: {
    user: User | null
    books: Book[]
    setBooks: (fn: Book[]) => void
}) {
    // Load books when component mounts
    useEffect(() => {
        loadBooks(user, setBooks)
    }, [user, setBooks])

    // Clear potentially corrupted craft.js data from localStorage
    useEffect(() => {
        try {
            const localStorageKeys = Object.keys(localStorage)
            const craftKeys = localStorageKeys.filter(
                (key) => key.startsWith("craftjs") || key.includes("craft") || key.includes("editor")
            )

            craftKeys.forEach((key) => {
                console.log(`Clearing potentially corrupted data: ${key}`)
                localStorage.removeItem(key)
            })
        } catch (error) {
            console.error("Error clearing localStorage:", error)
        }
    }, [])

    const [selectedBook, setSelectedBook] = useState<string | null>(null)
    const [currentPage, setCurrentPage] = useState<number>(1)
    const [bookPages, setBookPages] = useState<Record<string, any>>({})
    const [tabValue, setTabValue] = useState<number>(0)
    const [loading, setLoading] = useState<boolean>(false)
    const [editorKey, setEditorKey] = useState<number>(0) // Key to force editor re-render
    const [errorMessage, setErrorMessage] = useState<string | null>(null)
    const [contextMenu, setContextMenu] = useState<{
        mouseX: number
        mouseY: number
        bookId: string | null
    } | null>(null)

    const { translations, isLoading, error } = useBookTranslations(user?.Username || "", selectedBook || "")

    // Handle book context menu
    const handleBookContextMenu = (event: React.MouseEvent, bookId: string) => {
        event.preventDefault()
        setContextMenu({
            mouseX: event.clientX,
            mouseY: event.clientY,
            bookId,
        })
    }
    const handleContextMenuClose = () => {
        setContextMenu(null)
    }

    const [alertMessage, setAlertMessage] = useState<string | null>(null)
    const [alertSeverity, setAlertSeverity] = useState<"success" | "error" | "info" | "warning">("success")

    const handleTranslateBook = async (targetLanguage: string) => {
        if (!contextMenu?.bookId || !user) return

        try {
            const response = await fetch("http://localhost:5558/translate/page_all", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    data: {
                        model: await getTranslationLanguages(user.Username, contextMenu.bookId, targetLanguage),
                        title: contextMenu.bookId,
                        user: user.Username,
                    },
                }),
            })

            if (!response.ok) {
                throw new Error(`Translation failed: ${response.statusText}`)
            }

            const data = await response.json()
            console.log("Translation response:", data)

            // Set success alert
            setAlertSeverity("success")
            setAlertMessage(`Book "${contextMenu.bookId}" has been queued for translation.`)

            // Start polling to check when translation is complete
            const bookId = contextMenu.bookId
            const pollInterval = setInterval(async () => {
                try {
                    // Check if this language translation is now available
                    const availableTranslations = await getTranslationLanguages(user.Username, bookId, targetLanguage)

                    if (availableTranslations.includes(targetLanguage)) {
                        clearInterval(pollInterval)

                        // If this is the currently selected book, update the UI
                        if (selectedBook === bookId) {
                            // Update alert to indicate translation is complete
                            setAlertSeverity("success")
                            setAlertMessage(`Translation to ${targetLanguage} is now available!`)

                            // Force refresh of available translations
                            // This will update the language dropdown menu
                            fetchBookPage(bookId, currentPage, targetLanguage)
                        }
                    }
                } catch (error) {
                    console.error("Error polling for translation status:", error)
                    clearInterval(pollInterval)
                }
            }, 5000) // Check every 5 seconds

            // Clear the interval after 10 minutes (max wait time)
            setTimeout(() => clearInterval(pollInterval), 5 * 60 * 1000)
        } catch (error) {
            console.error("Translation error:", error)
            // Set error alert
            setAlertSeverity("error")
            setAlertMessage(`Translation failed: ${error.message}`)
        } finally {
            handleContextMenuClose()
        }
    }

    // Create a default empty page structure
    const createEmptyPageStructure = () => {
        // Create a minimal valid Craft.js node structure
        const rootId = "ROOT"
        const nodes = {
            [rootId]: {
                type: { resolvedName: "Container" },
                isCanvas: true,
                props: {
                    background: "transparent",
                    padding: 20,
                    position: "relative",
                    width: "100%",
                },
                displayName: "Container",
                custom: { displayName: "Page Container" },
                nodes: ["heading1", "text1"],
                linkedNodes: {},
                parent: null,
                hidden: false,
            },
            heading1: {
                type: { resolvedName: "Heading" },
                props: {
                    text: "Book Page Title",
                    variant: "h2",
                },
                displayName: "Heading",
                custom: { displayName: "Page Title" },
                nodes: [],
                linkedNodes: {},
                parent: rootId,
                hidden: false,
            },
            text1: {
                type: { resolvedName: "Text" },
                props: {
                    text: "Start typing your book content here...",
                    fontSize: 16,
                    textAlign: "left",
                },
                displayName: "Text",
                custom: { displayName: "Default Text" },
                nodes: [],
                linkedNodes: {},
                parent: rootId,
                hidden: false,
            },
        }

        return { nodes, ROOT: rootId }
    }

    // Fetch book page content from API
    const fetchBookPage = async (bookId: string, pageNum: number, lang: string) => {
        if (!user) return

        setLoading(true)
        setErrorMessage(null)
        try {
            const response = await fetch("http://localhost:5558/get_book_page", {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    user: user.Username,
                    title: bookId,
                    page: pageNum.toString(),
                    lang: lang || "source", // Default to "source" if lang is null or undefined
                },
            })

            if (!response.ok) {
                throw new Error(`Failed to fetch page: ${response.statusText}`)
            }

            const data = await response.json()
            console.log("Book page data:", data)

            // Convert API response to Craft.js nodes
            const craftNodes = convertApiResponseToCraftNodes(data)

            // Update bookPages state with the fetched content
            setBookPages((prev) => ({
                ...prev,
                [bookId]: {
                    ...prev[bookId],
                    pages: {
                        ...prev[bookId]?.pages,
                        [pageNum]: craftNodes,
                    },
                },
            }))

            // Force editor to re-render with new content
            setEditorKey((prevKey) => prevKey + 1)
        } catch (error) {
            console.error("Error fetching book page:", error)
            setErrorMessage(`Error loading page ${pageNum}: ${error.message}`)

            // If there's an error, set an empty page structure instead of leaving it blank
            setBookPages((prev) => ({
                ...prev,
                [bookId]: {
                    ...prev[bookId],
                    pages: {
                        ...prev[bookId]?.pages,
                        [pageNum]: createEmptyPageStructure(),
                    },
                },
            }))
            setEditorKey((prevKey) => prevKey + 1)
        } finally {
            setLoading(false)
        }
    }

    // Convert API response to Craft.js nodes structure
    const convertApiResponseToCraftNodes = (apiData: any) => {
        try {
            // Create a base nodes object with ROOT element
            const rootId = "ROOT"

            // Determine the highest y-coordinate in the data to set appropriate container height
            let maxY = 0
            if (Array.isArray(apiData)) {
                apiData.forEach((item) => {
                    if (item.Block?.Block_Geometry?.[1]?.[1]) {
                        const y2 = item.Block.Block_Geometry[1][1]
                        if (y2 > maxY) maxY = y2
                    }
                })
            }

            // Calculate a proper height based on the content - ensure it's at least 800px
            // Adding 10% margin to ensure all content is visible
            const dynamicHeight = Math.max(800, Math.ceil(maxY * 1000) + 500)

            const nodes: Record<string, any> = {
                [rootId]: {
                    type: {
                        resolvedName: "Container",
                    },
                    isCanvas: true,
                    props: {
                        background: "White",
                        padding: 10,
                        position: "relative",
                        width: "100%",
                        height: "100%", // Change from fixed 500px to auto
                        overflow: "auto", // Change from visible to auto
                        minHeight: "800px",
                    },
                    displayName: "Container",
                    custom: { displayName: "Page Container" },
                    nodes: [],
                    linkedNodes: {},
                    parent: null,
                    hidden: false,
                },
            }

            if (!apiData || !Array.isArray(apiData) || apiData.length === 0) {
                console.log("Invalid or empty API data, returning empty page")
                return createEmptyPageStructure()
            }

            let childNodes = []

            // Process each block from the API response
            apiData.forEach((item, blockIndex) => {
                if (
                    !item.Block ||
                    !item.Block.Block_Geometry ||
                    !Array.isArray(item.Block.Block_Geometry) ||
                    item.Block.Block_Geometry.length < 2
                ) {
                    console.log(`Skipping invalid block at index ${blockIndex}:`, item)
                    return
                }

                // Create a container for this block
                const containerId = `container-${blockIndex}`
                const geometry = item.Block.Block_Geometry

                // Calculate position from geometry
                // Block_Geometry is [[x1, y1], [x2, y2]] - top-left and bottom-right corners
                const [x1, y1] = geometry[0]
                const [x2, y2] = geometry[1]
                const left = `${x1 * 100}%`
                const top = `${y1 * 100}%`
                const width = `${(x2 - x1) * 100}%`

                nodes[containerId] = {
                    type: { resolvedName: "Container" }, // Ensure this matches exactly
                    isCanvas: true,
                    props: {
                        background: "transparent",
                        padding: 10,
                        position: "absolute",
                        left,
                        top,
                        width,
                    },
                    displayName: "Container",
                    custom: { displayName: `Block ${blockIndex + 1}` },
                    nodes: [],
                    linkedNodes: {},
                    parent: rootId,
                    hidden: false,
                }

                childNodes.push(containerId)

                // Process text data for this block
                const textItems = item.Block.Data || []
                let textNodes = []

                if (Array.isArray(textItems)) {
                    textItems.forEach((textItem, textIndex) => {
                        if (!textItem || !textItem.text) return

                        // Join text array into single string
                        const text = Array.isArray(textItem.text) ? textItem.text.join(" ") : textItem.text.toString()
                        const fontSize = Math.max(12, Math.min(36, (textItem.size || 0.1) * 200)) // Scale size to reasonable font size

                        // Create text node
                        const textNodeId = `text-${blockIndex}-${textIndex}`
                        nodes[textNodeId] = {
                            type: { resolvedName: "Text" }, // Ensure this matches exactly
                            props: {
                                text,
                                fontSize,
                                textAlign: "left",
                            },
                            displayName: "Text",
                            custom: { displayName: `Text ${textIndex + 1}` },
                            nodes: [],
                            linkedNodes: {},
                            parent: containerId,
                            hidden: false,
                        }

                        textNodes.push(textNodeId)
                    })
                } else {
                    console.log(`Block ${blockIndex} has invalid Data (not an array):`, textItems)
                }

                // Add text nodes to container
                nodes[containerId].nodes = textNodes
            })

            // Add all containers to ROOT node - this is where the issue was
            nodes[rootId].nodes = childNodes

            // Add debugging to verify containers are correctly added to ROOT
            console.log("ROOT nodes:", nodes[rootId].nodes)
            console.log("Child nodes to add:", childNodes)

            // Final validation check for any undefined types
            for (const nodeId in nodes) {
                const node = nodes[nodeId]
                if (!node.type || !node.type.resolvedName) {
                    console.error(`Invalid node type found in ${nodeId}:`, node)
                    return createEmptyPageStructure()
                }
            }

            console.log("Generated Craft.js nodes:", { nodes, ROOT: rootId })
            return { nodes, ROOT: rootId }
        } catch (error) {
            console.error("Error converting API response to Craft.js nodes:", error)
            return createEmptyPageStructure()
        }
    }

    // Handle book selection
    const handleBookSelect = (bookId: string) => {
        setSelectedBook(bookId)
        setTabValue(0) // Switch to editor tab
        setCurrentPage(1) // Reset to page 1
        setErrorMessage(null)

        // Initialize book pages with a proper empty structure for the first page
        setBookPages((prev) => ({
            ...prev,
            [bookId]: {
                ...prev[bookId],
                pages: {
                    ...(prev[bookId]?.pages || {}),
                    1: createEmptyPageStructure(),
                },
            },
        }))

        // Fetch the first page content
        fetchBookPage(bookId, 1)
    }

    // Handle page change
    const handlePageChange = (pageNum: number) => {
        if (!selectedBook) return

        setCurrentPage(pageNum)
        setErrorMessage(null)

        // Check if we already have this page loaded
        if (!bookPages[selectedBook]?.pages[pageNum]) {
            fetchBookPage(selectedBook, pageNum)
        } else {
            // Re-render the editor with existing content
            setEditorKey((prevKey) => prevKey + 1)
        }
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
                        [newPageNum]: createEmptyPageStructure(), // Use proper structure instead of empty object
                    },
                },
            }))
            setCurrentPage(newPageNum)
            setErrorMessage(null)
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
                setErrorMessage(`Export failed: ${error.message}`)
            }
        }
    }

    const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
        setTabValue(newValue)
    }

    // Helper function to render the default frame
    function renderDefaultFrame() {
        return (
            <Frame>
                <Element is={Container} canvas>
                    <Heading text="Book Page Title" />
                    <Text text="Start typing your book content here..." />
                </Element>
            </Frame>
        )
    }

    const validateSerializedData = (serializedData: any) => {
        try {
            // Check if the data has nodes property
            if (!serializedData || !serializedData.nodes) {
                return false
            }

            // Check that all node types are in our resolver
            const validTypes = ["Container", "Text", "Image", "Heading"]
            const nodes = serializedData.nodes

            for (const nodeId in nodes) {
                const node = nodes[nodeId]
                if (!node || !node.type) {
                    console.error(`Node ${nodeId} missing type property`)
                    return false
                }

                const resolvedName = node.type?.resolvedName
                if (!resolvedName) {
                    console.error(`Node ${nodeId} has undefined resolvedName`)
                    return false
                }

                if (!validTypes.includes(resolvedName)) {
                    console.error(`Invalid node type: ${resolvedName}`)
                    return false
                }
            }

            return true
        } catch (e) {
            console.error("Error validating serialized data:", e)
            return false
        }
    }

    const validateNodeTypes = (nodes: Record<string, any>): boolean => {
        try {
            const validTypes = ["Container", "Text", "Image", "Heading"]

            for (const nodeId in nodes) {
                const node = nodes[nodeId]

                // Check if node exists and has a valid type
                if (!node || !node.type || !node.type.resolvedName) {
                    console.error(`Invalid node found: ${nodeId}`, node)
                    return false
                }

                // Check if the type is one of our valid types
                const resolvedName = node.type.resolvedName
                if (!validTypes.includes(resolvedName)) {
                    console.error(`Unknown component type: ${resolvedName}`)
                    return false
                }
            }

            return true
        } catch (e) {
            console.error("Error validating node types:", e)
            return false
        }
    }

    const handleDeleteBook = async () => {
        if (!contextMenu?.bookId || !user) return

        // Ask for confirmation before deleting
        if (window.confirm(`Are you sure you want to delete "${contextMenu.bookId}"?`)) {
            try {
                const response = await fetch("http://localhost:5558/delete_book", {
                    method: "DELETE",
                    headers: {
                        "Content-Type": "application/json",
                        user: user.Username,
                        title: contextMenu.bookId,
                    },
                })

                if (!response.ok) {
                    throw new Error(`Deletion failed: ${response.statusText}`)
                }

                // Remove book from the books array
                setBooks(books.filter((book) => book._id !== contextMenu.bookId))

                // If this was the selected book, clear the selection
                if (selectedBook === contextMenu.bookId) {
                    setSelectedBook(null)
                }

                // Set success alert
                setAlertSeverity("success")
                setAlertMessage(`Book "${contextMenu.bookId}" has been deleted.`)
            } catch (error) {
                console.error("Delete error:", error)
                // Set error alert
                setAlertSeverity("error")
                setAlertMessage(`Failed to delete book: ${error.message}`)
            } finally {
                handleContextMenuClose()
            }
        } else {
            handleContextMenuClose()
        }
    }

    const resetCurrentPage = () => {
        if (selectedBook) {
            setBookPages((prev) => ({
                ...prev,
                [selectedBook]: {
                    ...prev[selectedBook],
                    pages: {
                        ...prev[selectedBook].pages,
                        [currentPage]: createEmptyPageStructure(),
                    },
                },
            }))
            setEditorKey((prev) => prev + 1)
            setErrorMessage(null)
        }
    }

    // Add state for menu anchor element
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)

    return (
        <>
            {/* Display Alert when message is present */}
            {alertMessage && (
                <Alert severity={alertSeverity} sx={{ mt: 2, mb: 2 }} onClose={() => setAlertMessage(null)}>
                    {alertMessage}
                </Alert>
            )}
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
                                        onContextMenu={(e) => handleBookContextMenu(e, book._id)}
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
                        <Paper
                            sx={{
                                p: 0,
                                minHeight: "600px",
                                overflow: "hidden",
                                boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
                            }}
                        >
                            <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
                                <Tabs
                                    value={tabValue}
                                    onChange={handleTabChange}
                                    sx={{
                                        px: 2,
                                        bgcolor: "#f8f9fa",
                                        "& .MuiTab-root": {
                                            minHeight: "48px",
                                            textTransform: "none",
                                            fontWeight: 500,
                                        },
                                    }}
                                >
                                    <Tab label="Editor" />
                                    <Tab label="Preview" />
                                </Tabs>
                            </Box>

                            {errorMessage && (
                                <Alert severity="error" sx={{ mx: 2, mt: 2 }} onClose={() => setErrorMessage(null)}>
                                    {errorMessage}
                                </Alert>
                            )}

                            <Box sx={{ display: tabValue === 0 ? "block" : "none", p: 2 }}>
                                <Box
                                    sx={{
                                        display: "flex",
                                        justifyContent: "space-between",
                                        alignItems: "center",
                                        mb: 2,
                                    }}
                                >
                                    <Typography variant="h6" fontWeight="medium">
                                        {selectedBook} - Page {currentPage}
                                    </Typography>

                                    <Box>
                                        <Button
                                            size="small"
                                            variant="outlined"
                                            color="inherit"
                                            sx={{ mr: 1, borderColor: "#ddd" }}
                                            onClick={() => handlePageChange(Math.max(1, currentPage - 1))}
                                            disabled={currentPage <= 1}
                                        >
                                            Previous
                                        </Button>
                                        <Button
                                            size="small"
                                            variant="outlined"
                                            color="inherit"
                                            sx={{ borderColor: "#ddd" }}
                                            onClick={() => handlePageChange(currentPage + 1)}
                                        >
                                            Next
                                        </Button>
                                    </Box>
                                </Box>

                                {loading ? (
                                    <Box sx={{ display: "flex", justifyContent: "center", p: 5 }}>
                                        <CircularProgress />
                                    </Box>
                                ) : (
                                    <ErrorBoundary onReset={resetCurrentPage}>
                                        <Editor
                                            key={editorKey}
                                            resolver={{
                                                Text,
                                                Container,
                                                Image,
                                                Heading,
                                            }}
                                            onNodesChange={(query) => {
                                                // Save editor state when nodes change
                                                if (selectedBook) {
                                                    try {
                                                        console.log("Saving editor state...")
                                                        const json = query.serialize()

                                                        // Extra validation before saving
                                                        const isValid = validateSerializedData(json)

                                                        if (isValid) {
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
                                                        } else {
                                                            console.error(
                                                                "Invalid serialized data - not saving changes"
                                                            )
                                                        }
                                                    } catch (error) {
                                                        console.error("Error serializing editor state:", error)
                                                    }
                                                }
                                            }}
                                        >
                                            <Box sx={{ display: "flex", gap: 2 }}>
                                                <Box
                                                    sx={{
                                                        width: "75%",
                                                        border: "1px solid #e0e0e0",
                                                        borderRadius: "4px",
                                                        minHeight: "600px",
                                                        position: "relative",
                                                        overflow: "auto",
                                                        maxHeight: "70vh",
                                                        bgcolor: "#ffffff",
                                                        boxShadow: "inset 0 0 5px rgba(0,0,0,0.05)",
                                                    }}
                                                >
                                                    {(() => {
                                                        try {
                                                            // Get the current page data
                                                            const pageData = bookPages[selectedBook]?.pages[currentPage]

                                                            // Deep validation before rendering
                                                            if (
                                                                pageData &&
                                                                typeof pageData === "object" &&
                                                                pageData.nodes
                                                            ) {
                                                                // Check for any undefined component types
                                                                let hasUndefined = false
                                                                for (const nodeId in pageData.nodes) {
                                                                    const node = pageData.nodes[nodeId]
                                                                    if (!node?.type?.resolvedName) {
                                                                        hasUndefined = true
                                                                        console.error(
                                                                            `Node ${nodeId} has undefined type:`,
                                                                            node
                                                                        )
                                                                        break
                                                                    }
                                                                }

                                                                if (hasUndefined) {
                                                                    console.error(
                                                                        "Found undefined component types - using default frame"
                                                                    )
                                                                    return renderDefaultFrame()
                                                                }

                                                                // Validate that all component types exist in our resolver
                                                                const isValid = validateNodeTypes(pageData.nodes)

                                                                if (isValid) {
                                                                    return (
                                                                        <Frame data={pageData.nodes}>
                                                                            {/* Content will be loaded from the data prop */}
                                                                        </Frame>
                                                                    )
                                                                } else {
                                                                    console.error(
                                                                        "Invalid component types in page data - using default frame"
                                                                    )
                                                                    return renderDefaultFrame()
                                                                }
                                                            } else {
                                                                // No data or invalid data format - use default frame
                                                                return renderDefaultFrame()
                                                            }
                                                        } catch (error) {
                                                            console.error("Error rendering Frame:", error)
                                                            return renderDefaultFrame()
                                                        }
                                                    })()}
                                                </Box>
                                                <Box
                                                    sx={{
                                                        width: "25%",
                                                        display: "flex",
                                                        flexDirection: "column",
                                                        gap: 2,
                                                    }}
                                                >
                                                    <Toolbox />
                                                    <SettingsPanel />
                                                </Box>
                                            </Box>

                                            <Box
                                                sx={{
                                                    mt: 2,
                                                    pt: 2,
                                                    display: "flex",
                                                    justifyContent: "space-between",
                                                    borderTop: "1px solid #eee",
                                                }}
                                            >
                                                <Box>
                                                    <Button
                                                        variant="outlined"
                                                        onClick={addNewPage}
                                                        color="primary"
                                                        size="small"
                                                    >
                                                        Add Page
                                                    </Button>
                                                </Box>
                                                <Box>
                                                    <Box sx={{ mr: 1, display: "inline-flex", alignItems: "center" }}>
                                                        <Button
                                                            variant="outlined"
                                                            size="small"
                                                            color="primary"
                                                            endIcon={<span>▼</span>}
                                                            onClick={(e) => {
                                                                const target = e.currentTarget
                                                                setAnchorEl ? setAnchorEl(target) : null
                                                            }}
                                                            disabled={!translations || translations.length === 0}
                                                        >
                                                            {isLoading ? "Loading..." : "Language"}
                                                        </Button>
                                                        <Menu
                                                            anchorEl={anchorEl}
                                                            open={Boolean(anchorEl)}
                                                            onClose={() => setAnchorEl && setAnchorEl(null)}
                                                        >
                                                            <MenuItem
                                                                onClick={() => {
                                                                    // Original language
                                                                    fetchBookPage(selectedBook || "", currentPage)
                                                                    setAnchorEl && setAnchorEl(null)
                                                                }}
                                                            >
                                                                (Original)
                                                            </MenuItem>
                                                            {translations &&
                                                                translations.map((lang, index) => (
                                                                    <MenuItem
                                                                        key={index}
                                                                        onClick={() => {
                                                                            fetchBookPage(
                                                                                selectedBook || "",
                                                                                currentPage,
                                                                                lang
                                                                            )
                                                                            // Switch to translation
                                                                            // Fetch translated content
                                                                            // Implementation depends on your translation data structure
                                                                            setAnchorEl && setAnchorEl(null)
                                                                        }}
                                                                    >
                                                                        {lang}
                                                                    </MenuItem>
                                                                ))}
                                                        </Menu>
                                                    </Box>
                                                    <Button
                                                        variant="contained"
                                                        color="primary"
                                                        size="small"
                                                        onClick={handleExportHtml}
                                                    >
                                                        Export HTML
                                                    </Button>
                                                </Box>
                                            </Box>
                                        </Editor>
                                    </ErrorBoundary>
                                )}
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
            {/* Context Menu */}
            <Menu
                open={contextMenu !== null}
                onClose={handleContextMenuClose}
                anchorReference="anchorPosition"
                anchorPosition={
                    contextMenu !== null ? { top: contextMenu.mouseY, left: contextMenu.mouseX } : undefined
                }
            >
                <MenuItem onClick={() => handleTranslateBook("de")}>Translate to German</MenuItem>
                <MenuItem onClick={() => handleTranslateBook("fr")}>Translate to French</MenuItem>
                <MenuItem onClick={() => handleTranslateBook("es")}>Translate to Spanish</MenuItem>
                <MenuItem onClick={() => handleTranslateBook("it")}>Translate to Italian</MenuItem>
                <MenuItem onClick={() => handleTranslateBook("pt")}>Translate to Portuguese</MenuItem>
                <MenuItem onClick={() => handleTranslateBook("ja")}>Translate to Japanese</MenuItem>
                <MenuItem onClick={() => handleTranslateBook("zh")}>Translate to Chinese</MenuItem>
                <MenuItem onClick={() => handleTranslateBook("ru")}>Translate to Russian</MenuItem>
                <Divider />
                <MenuItem onClick={handleDeleteBook} sx={{ color: "error.main" }}>
                    Delete Book
                </MenuItem>
            </Menu>
        </>
    )
}
