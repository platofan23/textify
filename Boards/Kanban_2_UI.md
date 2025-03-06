<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
</head>
<body>

<h1>Kanban Board</h1>
<h2>Epic 2: UI</h2>
<table border="1" cellpadding="6" cellspacing="0">
  <thead>
    <tr>
      <th>Task</th>
      <th>Description</th>
      <th>Acceptance Criteria</th>
      <th>Status</th>
      <th>Assigned to</th>
      <th>Importance 1(very low) .. 5(very hight)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Set up project structure</td>
      <td>Establish the basic project structure for the Web-UI.</td>
      <td>Folder structure created, build tools (e.g., Webpack/Vite) set up.</td>
      <td>Done</td>
      <td>CJ</td>
      <td>5</td>
    </tr>
    <tr>
      <td>Select UI framework</td>
      <td>Choose a framework (e.g., React, Vue, Angular) for the Web-UI.</td>
      <td>Framework selected, sample components created.</td>
      <td>Done</td>
      <td>CJ</td>
      <td>5</td>
    </tr>
    <tr>
      <td>Create design system</td>
      <td>Develop a basic design</td>
      <td>Unified color palette, fonts, and basic components available.</td>
      <td>Done</td>
      <td>CJ</td>
      <td>3</td>
    </tr>
    <tr>
      <td>Integrate Translation API</td>
      <td>Implement the connection to the translation API.</td>
      <td>API responses are displayed correctly in the frontend.</td>
      <td>Done</td>
      <td>CJ</td>
      <td>5</td>
    </tr>
    <tr>
      <td>Develop text translation input form</td>
      <td>Create a form for users to input text for translation.</td>
      <td>Input and target languages selectable, translations displayed.</td>
      <td>Done</td>
      <td>CJ</td>
      <td>4</td>
    </tr>
    <tr>
      <td>Implement real-time translation feedback</td>
      <td>Add a loading indicator for translations.</td>
      <td>Progress indicator appears during API queries.</td>
      <td>Done</td>
      <td>CJ</td>
      <td>3</td>
    </tr>
    <tr>
      <td>Implement audio recording functionality</td>
      <td>Add functionality to allow audio recording in the browser.</td>
      <td>Recordings are captured and played back correctly in the frontend.</td>
      <td>Done/td>
      <td>CJ</td>
      <td>1</td>
    </tr>
    <tr>
      <td>Integrate STT API</td>
      <td>Connect the recording functionality to the Speech-to-Text API.</td>
      <td>Text output based on audio input works correctly.</td>
      <td>Done</td>
      <td>CJ</td>
      <td>2</td>
    </tr>
    <tr>
      <td>Add error handling for audio files</td>
      <td>Develop robust error handling for invalid or missing audio inputs.</td>
      <td>Clear error messages are displayed.</td>
      <td>Done</td>
      <td>CJ</td>
      <td>2</td>
    </tr>
    <tr>
      <td>Integrate text-to-audio conversion</td>
      <td>Create functionality to convert text to audio.</td>
      <td>Input text is correctly converted into audio files and played back.</td>
      <td>Done</td>
      <td>CJ</td>
      <td>3</td>
    </tr>
    <tr>
      <td>Implement audio player</td>
      <td>Create an audio player with fuctions like changing playback speed.</td>
      <td>Working audio player</td>
      <td>Done</td>
      <td>CJ</td>
      <td>1</td>
    </tr>
    <tr>
      <td>Implement image upload functionality</td>
      <td>Add functionality to allow image uploads.</td>
      <td>Uploaded images are displayed and ready for analysis.</td>
      <td>Done</td>
      <td>CJ</td>
      <td>5</td>
    </tr>
    <tr>
      <td>Integrate OCR API</td>
      <td>Implement the connection to the OCR API.</td>
      <td>Text is extracted from images and displayed in the UI.</td>
      <td>Done</td>
      <td>CJ</td>
      <td>5</td>
    </tr>
    <tr>
      <td>Add OCR result review and editing</td>
      <td>Provide an option to edit detected text.</td>
      <td>Users can manually adjust detected text.</td>
      <td>Done</td>
      <td>CJ</td>
      <td>4</td>
    </tr>
    <tr>
      <td>Integrate Export translations</td>
      <td>Develop functionality to download translations as files.</td>
      <td>Translations are exportable as TXT or CSV.</td>
      <td>ToDo</td>
      <td>CJ</td>
      <td>4(PDF)/2(DOCX)</td>
    </tr>
    <tr>
      <td>Integrate Export audio</td>
      <td>Add the ability to download generated audio files.</td>
      <td>Audio files are exportable as MP3 or WAV.</td>
      <td>ToDo</td>
      <td>CJ</td>
      <td>3</td>
    </tr>
    <tr>
      <td>Conduct usability tests</td>
      <td>Test the UI’s usability with various users.</td>
      <td>Feedback collected and analyzed.</td>
      <td>Done</td>
      <td>ALL</td>
      <td>4</td>
    </tr>
    <tr>
      <td>Optimize performance</td>
      <td>Improve loading times and responsiveness of the Web-UI.</td>
      <td>All functions load within 1 second (if API responds).</td>
      <td>Done</td>
      <td>CJ</td>
      <td>5</td>
    </tr>
    <tr>
      <td>Test cross-browser compatibility</td>
      <td>Ensure the UI works across different browsers.</td>
      <td>Works in Chrome, Firefox, and Edge.</td>
      <td>Done</td>
      <td>CJ</td>
      <td>2</td>
    </tr>
  </tbody>
</table>
</body>
</html>
