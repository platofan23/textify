import { Modal } from "@mui/material"
import { data } from "react-router-dom"

async function streamText(
    appendText: (text: string | undefined) => void,
    texts: [string],
    sourcelanguage: string,
    targetlanguage: string
) {
    const upload_id = crypto.randomUUID()
    let modalOpen = false

    for (let text of texts) {
        if (text === "") {
            continue
        }

        await fetch("https://localhost:5555/translate/text", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                data: {
                    text: text,
                    sourcelanguage: sourcelanguage,
                    targetlanguage: targetlanguage,
                    upload_id: upload_id,
                    model: "Helsinki-NLP/opus-mt",
                },
            }),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`)
                }
                return response.json()
            })
            .then((data) => {
                if (data.translation === undefined) {
                    appendText(undefined)
                    return
                }

                appendText(data.translation)
            })
            .catch((error) => {
                console.error("Error:", error)
                appendText(undefined)
            })
    }
}

export default streamText
