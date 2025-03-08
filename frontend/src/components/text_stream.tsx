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

        await fetch("https://localhost:5558/translate/text", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                data: {
                    text: text,
                    upload_id: upload_id,
                    model: "Helsinki-NLP/opus-mt-" + sourcelanguage + "-" + targetlanguage,
                },
            }),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.text}`)
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
    }
}

export default streamText
