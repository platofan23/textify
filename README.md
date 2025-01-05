## :ledger: Index

- [About](#beginner-about)
- [Usage](#zap-usage)
  - [Installation](#electric_plug-installation)
  - [Commands](#package-commands)
- [Development](#wrench-development)
  - [Pre-Requisites](#notebook-pre-requisites)
  - [Developmen Environment](#nut_and_bolt-development-environment)
  - [File Structure](#file_folder-file-structure)
  - [Build](#hammer-build)  
  - [Deployment](#rocket-deployment)  
- [Contribution](#fire-contribution)
  - [Branches](#cactus-branches)
  - [Guideline](#exclamation-guideline)  
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
###  :electric_plug: Installation
- Steps on how to install this project, to use it.
- Be very detailed here, For example, if you have tools which run on different operating systems, write installation steps for all of them.

```
$ add installations steps if you have to.
```

###  :package: Commands
- Commands to start the project.

##  :wrench: Development
If you want other people to contribute to this project, this is the section, make sure you always add this.

### :notebook: Pre-Requisites
List all the pre-requisites the system needs to develop this project.
- A tool
- B tool

###  :nut_and_bolt: Development Environment
Write about setting up the working environment for your project.
- How to download the project...
- How to install dependencies...


###  :file_folder: File Structure
```
.
textify/                                  # Directory for the project
├── backend/                              # Flask Backend
│   ├── app/                              # Directory App
│   │   ├── routes/                       # Directory for the Endpoints
│   │   │   ├── __init__.py               # Init File for Importing whole directory
│   │   │   ├── route_file_manager.py     # Endpoints for File-Manager
│   │   │   ├── route_ocr.py              # Endpoints for OCR
│   │   │   ├── route_stt.py              # Endpoints for Speech-to-Text
│   │   │   ├── route_tts.py              # Endpoints for Text-to-Speech
│   │   │   ├── route_translation.py      # Endpoints for Translation
│   │   ├── services/                     # Directory for the services
│   │   │   ├── __inti__.py               # Init File for Importing whole directory
│   │   │   ├── service_ocr.py            # Logic for OCR
│   │   │   ├── service_stt_.py           # Logic for Speech-to-Text
│   │   │   ├── service_translation.py    # Logic for Translation
│   │   │   ├── service_tts.py            # Logic for Text-to-Speech
│   │   ├── utils/                        # Directory for resuseable code
│   │   ├── main.py                       # Entry point for the Flask app
│   ├── config/                           # Config Directory for the backend
│   │   ├── config.ini                    # Configs for the backend
│   ├── ressources/                       # Resource files for the backend
│   │   ├── resources.txt                 # File for easy install with pip
│   │   ├── ressources_generate_txt.py    # Script to generate resources.txt
│   ├── tests/                            # Directory Tests
│   │   ├── test_upload_files/            # Test Folder for uploades files
│   │   ├── test_rest_api.py.py           # Tests for the endpoints
│   │   ├── test_user_management.py       # Tests for the logic
│
├── frontend/                             # React Frontend
│   ├── public/                           # Static files
│   │   ├── vite.svg                      # Static SVG asset
│   │   ├── index.html                    # HTML entry point
│   ├── src/
│   │   ├── assets/                       # Resource files for the frontend
│   │   │   ├── asset_menu_background.webp# Menu background image
│   │   │   ├── asset_react_logo.svg      # React logo
│   │   ├── components/                   # Reusable UI components
│   │   │   ├── component_home.tsx        # Home component
│   │   │   ├── Editor.tsx                # Editor component
│   │   │   ├── Editor_style.css          # CSS for the editor
│   │   │   ├── translate.tsx             # Translation component
│   │   ├── menu/                         # Menu components
│   │   │   ├── menu_base.tsx             # Base menu
│   │   │   ├── menu_sign_in.tsx          # Sign-in menu
│   │   ├── main.tsx                      # Main application entry
│   │   ├── vite-env.d.ts                 # Vite environment types
│   ├── node_modules/                     # Node dependencies
│   ├── package.json                      # JavaScript dependencies
│   ├── package-lock.json                 # Lock file for npm dependencies
│   ├── eslint.config.js                  # ESLint configuration
│   ├── tsconfig.json                     # TypeScript configuration
│   ├── tsconfig.app.json                 # App-specific TypeScript config
│   ├── tsconfig.node.json                # Node-specific TypeScript config
│   ├── vite.config.ts                    # Vite configuration
│
├── uploads/                              # Upload folder
├── .gitignore                            # Git ignore files
├── README.md                             # Project description
├── docker-compose.yml                    # Optional: Docker configuration
└── Dockerfile                            # Optional: Dockerfile for backend
```

| No | File Name | Details 
|----|------------|-------|
| 1  | index | Entry point

###  :hammer: Build
Write the build Instruction here.

### :rocket: Deployment
Write the deployment instruction here.

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


### :exclamation: Guideline


##  :page_facing_up: Resources
- AI-Models: https://huggingface.co/
- Discord Server: https://discord.gg/XzERCkFV
- Docker: https://www.docker.com/
- EasyOCR: https://github.com/JaidedAI/EasyOCR
- https://de.libretranslate.com/
- https://marian-nmt.github.io/
- Material UI: https://mui.com/material-ui/
- https://github.com/Helsinki-NLP/Opus-MT
- Python: https://www.python.org/
- https://quilljs.com/
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
Add a license here, or a link to it.
