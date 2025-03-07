import { useState, useRef, useEffect } from "react"

export function get_book_translations() {

    const [bookTranslations, setBookTranslations] = useState<string[]>([])

    useEffect(() => {
        fetch("http://localhost/get_book_translations")

}
