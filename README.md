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
- A datebase: **MongoDB**
- Dependencies depending on the operating system

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
   python3.12 -m venv venv
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
2. Access the frontend at: http://localhost:5173 in docker with https
3. Access the backend API at: http://localhost:5555 in docker with https

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
