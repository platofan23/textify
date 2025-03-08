import { useState, useRef, useEffect } from "react"
import Quill from "quill"

interface UseRecorderProps {
    quillRefInput: React.MutableRefObject<Quill | null>
    sourcelanguage: string
}

export function useRecorder({ quillRefInput, sourcelanguage }: UseRecorderProps) {
    const [isRecording, setIsRecording] = useState<boolean>(false)
    const [recordedAudio, setRecordedAudio] = useState<Blob | null>(null)
    const [recordingTime, setRecordingTime] = useState<number>(0)
    const mediaRecorderRef = useRef<MediaRecorder | null>(null)
    const recordingIntervalRef = useRef<number | null>(null)
    const audioChunksRef = useRef<BlobPart[]>([])

    function startRecording() {
        audioChunksRef.current = []
        setRecordingTime(0)

        if (!navigator.mediaDevices || !window.MediaRecorder) {
            alert("Recording is not supported in this browser")
            return
        }

        navigator.mediaDevices
            .getUserMedia({ audio: true })
            .then((stream) => {
                // Define MIME types with fallbacks for better browser support
                const mimeTypes = [
                    "audio/webm;codecs=opus",
                    "audio/webm",
                    "audio/ogg;codecs=opus",
                    "audio/wav",
                    "", // Empty string lets browser use default
                ]

                // Find first supported MIME type
                let mimeType =
                    mimeTypes.find((type) => {
                        try {
                            return type === "" || MediaRecorder.isTypeSupported(type)
                        } catch {
                            return false
                        }
                    }) || ""

                // Create MediaRecorder with proper options
                const mediaRecorder = new MediaRecorder(stream, {
                    mimeType: mimeType || undefined,
                    audioBitsPerSecond: 128000,
                })
                mediaRecorderRef.current = mediaRecorder

                // Important: Register event listener BEFORE starting recording
                mediaRecorder.addEventListener("dataavailable", (event) => {
                    if (event.data.size > 0) {
                        audioChunksRef.current.push(event.data)
                    }
                })

                mediaRecorder.addEventListener("stop", () => {
                    const finalMimeType = mediaRecorder.mimeType || "audio/webm"
                    const audioBlob = new Blob(audioChunksRef.current, { type: finalMimeType })
                    setRecordedAudio(audioBlob)

                    console.log(
                        `Recording completed: ${audioChunksRef.current.length} chunks, size ${audioBlob.size} bytes`
                    )

                    // Convert recorded audio to text and place in input editor
                    processRecordedAudio(audioBlob)

                    // Stop all tracks in the stream to release the microphone
                    stream.getTracks().forEach((track) => track.stop())
                })

                // Start the recording timer
                const interval = window.setInterval(() => {
                    setRecordingTime((prevTime) => {
                        const newTime = prevTime + 1

                        // Auto-stop at 2 minutes (120 seconds)
                        if (newTime >= 120) {
                            stopRecording()
                        }
                        return newTime
                    })
                }, 1000)
                recordingIntervalRef.current = interval

                // Request data every 1 second (1000ms) instead of 200ms for more reliable chunks
                mediaRecorder.start(1000)
                setIsRecording(true)
                console.log("Recording started")
            })
            .catch((error) => {
                console.error("Error accessing microphone:", error)
                alert("Could not access microphone. Please check permissions.")
            })
    }

    function stopRecording() {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop()
            setIsRecording(false)

            // Clear the interval timer
            if (recordingIntervalRef.current) {
                clearInterval(recordingIntervalRef.current)
                recordingIntervalRef.current = null
            }
        }
    }

    function handleRecordButtonClick() {
        if (isRecording) {
            stopRecording()
        } else {
            startRecording()
        }
    }

    async function processRecordedAudio(audioBlob: Blob) {
        // Create a FormData object to send the audio file
        const formData = new FormData()
        formData.append("audio_file", audioBlob, "recording.wav")
        formData.append("language", sourcelanguage)

        try {
            const response = await fetch("https://localhost:5558/stt", {
                method: "POST",
                body: formData,
            })

            if (!response.ok) throw new Error("Speech to text conversion failed")

            const data = await response.json()
            if (data.text && quillRefInput.current) {
                quillRefInput.current.setText(data.text)
            }
        } catch (error) {
            console.error("Speech to text failed:", error)
        }
    }

    // Clean up recording resources when component unmounts
    useEffect(() => {
        return () => {
            if (mediaRecorderRef.current && isRecording) {
                mediaRecorderRef.current.stop()
            }
            if (recordingIntervalRef.current) {
                clearInterval(recordingIntervalRef.current)
            }
        }
    }, [isRecording])

    return {
        isRecording,
        recordingTime,
        recordedAudio,
        handleRecordButtonClick,
    }
}
