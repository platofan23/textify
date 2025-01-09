import { data } from "react-router-dom"

async function streamText(appendText: (text: string) => void, texts: [string]) {
    const upload_id = crypto.randomUUID()

    for (let text of texts) {
        if (text === "") {
            continue
        }
        await fetch("http://localhost:5555/translate/text", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                data: {
                    text: text,
                    sourcelanguage: "de",
                    targetlanguage: "en",
                    upload_id: upload_id,
                    model: "Helsinki-NLP/opus-mt",
                },
            }),
        })
            .then((response) => response.json())
            .then((data) => {
                console.log(data)
                appendText(data.translation)
            })
    }
}

export default streamText
