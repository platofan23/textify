## :ledger: Index

- [About](#beginner-about)
- [Usage](#zap-usage)
  - [Commands](#package-commands)
- [Development](#wrench-development)
  - [Pre-Requisites](#notebook-pre-requisites)
  - [File Structure](#file_folder-file-structure)
- [Contribution](#fire-contribution)
  - [Branches](#cactus-branches)
- [Resources](#page_facing_up-resources)
- [Gallery](#camera-gallery)
- [Credit/Acknowledgment](#star2-creditacknowledgment)
- [License](#lock-license)

##  :beginner: About
We develop innovative software solutions that solve real-world problems and improve people's lives. With a focus on applications in the areas of optical character recognition (OCR), book and image translation, text-to-speech (TSS) and speech-to-text (STT), we aim to break down barriers and facilitate access to knowledge. In doing so, we promote a culture of collaboration, creative growth and continuous improvement.

## :zap: Usage
The project has following use-cases:
- OCR for books, papers or a blackboard via picture
- Translation of texts
- Summerization of texts
- TTS
- STT
- Export in human-readable or machine-readable file-format


### :package: Commands

- Start the project:
  ```
  docker-compose up -d
  ```

- Stop the project:
  ```
  docker-compose down
  ```
  
## :wrench: Development

### :notebook: Pre-Requisites
List of pre-requisites:

- **Docker** and **Docker Compose** installed on your system.
- A code editor (e.g., **Visual Studio Code**, **PyCharm**).
- For backend development: **Python 3.11** and a virtual environment.
- For frontend development: **Node.js** and **npm** or **yarn**.

### :nut_and_bolt: Development Environment

#### Clone the repository:
```
git clone https://github.com/your-repository/textify.git
cd textify
```
### Backend Development:

1. Navigate to the backend directory:
   ```
   cd backend
   ```
2. Set up the virtual environment and install dependencies:
   ```
   python3.11 -m venv venv
   source venv/bin/activate 
   pip install -r ressources/resources.txt
   ```
3. Ensure the config.ini file is configured correctly in the config folder.
4. Start the main.py in /back/app folder

### Frontend Development:

1. Navigate to the frontend directory:
  ```
  cd ../frontend
  ```
2. Install dependencies:
  ```
  npm install
  ```
3. Start the development server:
  ```
  npm run dev
  ```
### Run the Application Locally:

1. Ensure both backend and frontend are running.
2. Access the frontend at: http://localhost:5173.
3. Access the backend API at: http://localhost:5555

###  :file_folder: File Structure
```
.
textify/                                  # Root directory of the project
├── backend/                              # Backend folder for the Flask application
│   ├── app/                              # Core backend application
│   │   ├── routes/                       # API endpoint definitions
│   │   │   ├── __init__.py               # Initializes the routes module
│   │   │   ├── route_file_manager.py     # Endpoints for file management
│   │   │   ├── route_ocr.py              # Endpoints for Optical Character Recognition (OCR)
│   │   │   ├── route_stt.py              # Endpoints for Speech-to-Text functionality
│   │   │   ├── route_tts.py              # Endpoints for Text-to-Speech functionality
│   │   │   ├── route_translation_file.py # Endpoints for file translation
│   │   │   └── route_translation_text.py # Endpoints for text translation
│   │   ├── services/                     # Service logic and core functionality
│   │   │   ├── __init__.py               # Initializes the services module
│   │   │   ├── service_ocr.py            # OCR processing logic
│   │   │   ├── service_stt.py            # Speech-to-Text processing logic
│   │   │   ├── service_translation.py    # Translation processing logic
│   │   │   └── service_tts.py            # Text-to-Speech processing logic
│   │   ├── start/                        # Application startup processes
│   │   │   ├── __init__.py               # Initializes the startup module
│   │   │   ├── start_configure.py        # Configures application settings
│   │   │   ├── start_execute_unit_test.py# Executes unit tests during startup
│   │   │   ├── start_preload.py          # Preloads models like translation models
│   │   │   └── start_register_routes.py  # Registers API routes with Flask
│   │   ├── translators/                  # Translation logic and API integrations
│   │   │   ├── __init__.py               # Initializes the translators module
│   │   │   ├── translator_opus.py        # Translation logic using OpusMT
│   │   │   └── translator_libre.py       # Translation logic using LibreTranslate API
│   │   ├── utils/                        # Utility functions and helpers
│   │   │   ├── __init__.py               # Initializes the utils module
│   │   │   ├── util_config_manager.py    # Manages and validates configuration settings
│   │   │   ├── util_mongo_manager.py     # Database class
│   │   │   ├── util_cache_manager.py     # Caching for translations and API responses
│   │   │   ├── util_logger.py            # Logger class
│   │   │   ├── util_pdf_processor.py     # Extracts and processes text from PDF files
│   │   │   └── util_text_processing.py   # Text preprocessing and chunking utilities
│   │   ├── main.py                       # Entry point for the Flask application
│   ├── config/                           # Configuration files for the backend
│   │   ├── config.ini                    # Main configuration file
│   │   └── docker.ini                    # Docker-specific configuration
│   ├── ressources/                       # Static resources and certificates
│   │   ├── cert/                         # SSL/TLS certificates
│   │   │   ├── Generate Certs.txt        # Instructions for generating certificates
│   │   │   ├── mongo.pem                 # Combined certificate and key for MongoDB
│   │   │   ├── mongo-cert.pem            # Certificate file for MongoDB
│   │   │   ├── mongo-key.pem             # Key file for MongoDB
│   │   │   ├── san.conf                  # OpenSSL config for generating SAN certificates
│   │   │   ├── server.crt                # Certificate file for HTTPS (Flask in Docker)
│   │   │   ├── server.key                # Key file for HTTPS (Flask in Docker)
│   │   ├── nginx/                        # NGINX configuration files
│   │   │   ├── nginx.conf                # Configuration for NGINX in Docker
│   │   ├── resources.txt                 # Python dependencies for the backend
│   │   └── ressources_generate_txt.py    # Script to generate `resources.txt`
│   ├── tests/                            # Unit and integration tests
│   │   ├── test_upload_files/            # Folder for uploaded files during tests
│   │   ├── test_rest_api.py              # Tests for REST API endpoints
│   │   └── test_user_management.py       # Tests for user management logic
│   ├── __ini__.py                        # Initializes the backend module
│   ├── Dockerfile_Backend_arm_or_CPU     # Dockerfile for backend ARM64 or CPU only 
│   ├── Dockerfile_Backend_x86_or_GPU_Big # Dockerfile for backend x86 or GPU big Version
│   └── Dockerfile_Backend_x86_or_GPU_Smal# Dockerfile for backend x86 or GPU small Version
│
├── frontend/                             # ReactJS frontend application
│   ├── public/                           # Publicly accessible files
│   │   ├── vite.svg                      # Static SVG asset
│   │   └── index.html                    # Main HTML file
│   ├── ressources/                       # Static resources and certificates
│   │   ├── cert/                         # SSL/TLS certificates
│   │   │   ├── server.crt                # Certificate file for HTTPS (Vitein Docker)
│   │   │   └── server.key                # Key file for HTTPS (Vite in Docker)
│   ├── src/                              # Source files for the frontend
│   │   ├── assets/                       # Static assets like images and fonts
│   │   │   ├── asset_menu_background.webp# Background image for the menu
│   │   │   └── asset_react_logo.svg      # React logo asset
│   │   ├── components/                   # Reusable React components
│   │   │   ├── component_home.tsx        # Component for the home page
│   │   │   ├── Editor.tsx                # Editor component for text editing
│   │   │   ├── Editor_style.css          # CSS styles for the editor
│   │   │   └── translate.tsx             # Component for translations
│   │   ├── menu/                         # Components for menus
│   │   │   ├── menu_base.tsx             # Base menu component
│   │   │   └── menu_sign_in.tsx          # Sign-in menu component
│   │   ├── main.tsx                      # Main entry point for the frontend
│   │   └── vite-env.d.ts                 # TypeScript type definitions for Vite
│   ├── node_modules/                     # Installed Node.js dependencies
│   ├── Dockerfile                        # Dockerfile for frontend
│   ├── package.json                      # JavaScript dependencies and scripts
│   ├── package-lock.json                 # Lock file for npm dependencies
│   ├── eslint.config.js                  # ESLint configuration for code linting
│   ├── tsconfig.json                     # Global TypeScript configuration
│   ├── tsconfig.app.json                 # TypeScript configuration for the app
│   ├── tsconfig.node.json                # TypeScript configuration for Node.js
│   └── vite.config.ts                    # Vite build and development configuration
│
├── uploads/                              # Directory for uploaded files
├── .gitignore                            # Files and directories to be ignored by Git
├── README.md                             # Project description and documentation
└── docker-compose.yml                    # Docker Compose configuration

```
 ###  :fire: Contribution

 1. **Create a pull request** <br>
 It can't get better then this, your pull request will be appreciated by the community. You can get started by picking up any open issues from [here](https://www.notion.so/145ded0028a281848e1aea96339b7e7d?v=145ded0028a281059c53000cd49c37dd) and make a pull request.

 ### :cactus: Branches
 
1. **`Test`** is the development branch.

2. **`master`** is the production branch.

3. Other Branches shall be named after the feature being worked on

**Steps to work with feature branch**

1. To start working on a new feature, create a new branch prefixed with `feature/` and followed by feature name. (ie. `featute/-FEATURE-NAME`)
2. Once you are done with your changes, you can raise PR.

**Steps to create a pull request**

1. Make a PR to `test` branch.
2. Comply with the best practices and guidelines e.g. where the PR concerns visual elements it should have an image showing the effect.
3. It must pass all continuous integration checks and get positive reviews.

After this, changes will be merged.


##  :page_facing_up: Resources
- AI-Models: https://huggingface.co/
- Discord Server: https://discord.gg/XzERCkFV
- Docker: https://www.docker.com/
- EasyOCR: https://github.com/JaidedAI/EasyOCR
- LibreTranslate: https://de.libretranslate.com/
- MarianMT: https://marian-nmt.github.io/
- Material UI: https://mui.com/material-ui/
- MongoDB: https://www.mongodb.com/de-de
- OPUS-MT: https://github.com/Helsinki-NLP/Opus-MT
- Python: https://www.python.org/
- QuillJS: https://quilljs.com/
- React JS: https://react.dev/
- Vite: https://vite.dev/
- YOLOv11: https://docs.ultralytics.com/de/models/yolo11/

##  :camera: Gallery
Pictures of your project.

## :star2: Credit/Acknowledgment
- https://github.com/Hein0002
- https://github.com/Komiplex
- https://github.com/platofan23


##  :lock: License

This project is licensed under the MIT License. You are free to use, modify, and distribute this software in compliance with the license terms.
  ```
  MIT License
  
  Copyright (c) [2025] [Team Textify]
  
  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:
  
  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.
  
  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
  ```
