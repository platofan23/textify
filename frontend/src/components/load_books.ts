import { Book, User } from "../main"

export function loadBooks(user: User | null, setBooks: (fn: Book[]) => void) {
    fetch("https://localhost:5558/get_books", {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            User: user?.Username ?? "",
        },
    })
        .then((res) => res.json())
        .then((data) => setBooks(data))
        .catch((err) => console.error(err))
}
