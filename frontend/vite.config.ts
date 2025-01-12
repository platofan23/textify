import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs';

// https://vite.dev/config/
export default defineConfig({
    root: './src',
    plugins: [react() ],
    server: {
        https: {
            key: fs.readFileSync("./resources/certs/server.key"),
            cert: fs.readFileSync("./resources/certs/server.crt"),
        },
        host: '0.0.0.0', // Optional: Make the server accessible externally
        port: 5173,       // Optional: Use the standard HTTPS port
        proxy: {
            "/translate": {
                target: "https://localhost:5555", // Backend container name
                changeOrigin: true,
                secure: false, // For self-signed certificates
            },
        },
    },
})

