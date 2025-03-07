import { useState, useEffect } from "react"

export function useBookTranslations(user: string, title: string) {
    const [translations, setTranslations] = useState<string[]>([])
    const [isLoading, setIsLoading] = useState<boolean>(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        const fetchTranslations = async () => {
            setIsLoading(true)
            setError(null)

            try {
                const response = await fetch("http://localhost:5558/get_book_translations", {
                    method: "GET",
                    headers: {
                        user: user,
                        title: title,
                    },
                })

                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`)
                }

                const data = await response.json()
                setTranslations(data.languages || [])
            } catch (err) {
                setError(err instanceof Error ? err.message : "Unknown error occurred")
                setTranslations([])
            } finally {
                setIsLoading(false)
            }
        }

        fetchTranslations()
    }, [user, title])

    return { translations, isLoading, error }
}

export async function getTranslationLanguages(user: string, title: string, targetLanguage: string) {
    const response = await fetch("http://localhost:5558/get_book_language", {
        method: "GET",
        headers: {
            user: user,
            title: title,
        },
    })

    return "Helsinki-NLP/opus-mt-" + (await response.json()) + "-" + targetLanguage
}
