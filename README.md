<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Kanban Board</title>

</head>
<body>

<h1>Kanban Board</h1>

<h2>Epic 1: Backend and REST-API</h2>
<table border="1" cellpadding="6" cellspacing="0">
  <thead>
    <tr>
      <th>Task</th>
      <th>Description</th>
      <th>Acceptance Criteria</th>
      <th>Status</th>
      <th>Assigned to</th>
      <th>Importance 1(very low) ->5(very hight)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Select and configure web server for frontend</td>
      <td>Choose and configure a web server for serving the frontend application.</td>
      <td>Web server (e.g., Nginx, Apache) selected, configured, and tested for deployment.</td>
      <td>Done</td>
      <td>CJ</td>
      <td>5</td>
    </tr>
    <tr>
      <td>Set up project structure</td>
      <td>Establish the basic project structure for the REST API and backend.</td>
      <td>Folder structure created, build tools (e.g., Node.js, Django, Flask) set up.</td>
      <td>In progress</td>
      <td>ALL</td>
    </tr>
    <tr>
      <td>Design API endpoints</td>
      <td>Define the structure and endpoints of the REST API.</td>
      <td>API documentation created with endpoint specifications.</td>
      <td>In progress</td>
      <td>CJ</td>
    </tr>
    <tr>
      <td>Implement user authentication</td>
      <td>Develop authentication mechanisms (e.g., JWT, OAuth).</td>
      <td>Users can log in, register, and manage sessions securely.</td>
      <td>In Progress</td>
      <td>CJ</td>
    </tr>
    <tr>
      <td>Integrate Translation API</td>
      <td>Connect backend with the Translation API for processing requests.</td>
      <td>API calls handled, results returned accurately.</td>
      <td>In Progress</td>
      <td>JK</td>
    </tr>
    <tr>
      <td>Implement Speech-to-Text (STT) support</td>
      <td>Integrate backend functionality with the STT API.</td>
      <td>Audio files processed and transcriptions returned.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Add Text-to-Speech (TTS) support</td>
      <td>Integrate TTS API for converting text to speech.</td>
      <td>Text input converted to audio output.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Implement OCR support</td>
      <td>Integrate OCR API for image text extraction.</td>
      <td>Uploaded images processed and text extracted successfully.</td>
      <td>In progress</td>
      <td>CJ</td>
    </tr>
    <tr>
      <td>Develop error handling</td>
      <td>Implement global error handling for API failures and edge cases.</td>
      <td>Errors logged, and descriptive error messages returned.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Add logging</td>
      <td>Set up logging for the backend.</td>
      <td>Logs available.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Set up automated testing</td>
      <td>Implement unit and integration tests for backend components.</td>
      <td>Tests written, executed, and passed successfully.</td>
      <td>Progess</td>
      <td>ALL</td>
    </tr>
    <tr>
      <td>Implement rate limiting</td>
      <td>Protect the API from abuse by implementing rate limiting.</td>
      <td>API rate limits enforced, and violations logged.</td>
      <td>In progress</td>
      <td></td>
    </tr>
    <tr>
      <td>Secure API</td>
      <td>Implement security measures like HTTPS, input validation, and encryption.</td>
      <td>Security tests passed, and vulnerabilities resolved.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Conduct performance testing</td>
      <td>Test the backend for performance under various loads.</td>
      <td>API responds within acceptable time limits under load.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Document API usage</td>
      <td>Create comprehensive documentation for API consumers.</td>
      <td>API documentation available and easy to understand.</td>
      <td>To Do</td>
      <td></td>
    </tr>
  </tbody>
</table>

<h2>Epic 2: UI</h2>
<table border="1" cellpadding="6" cellspacing="0">
  <thead>
    <tr>
      <th>Task</th>
      <th>Description</th>
      <th>Acceptance Criteria</th>
      <th>Status</th>
      <th>Assigned to</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Set up project structure</td>
      <td>Establish the basic project structure for the Web-UI.</td>
      <td>Folder structure created, build tools (e.g., Webpack/Vite) set up.</td>
      <td>In progress</td>
      <td>CJ</td>
    </tr>
    <tr>
      <td>Select UI framework</td>
      <td>Choose a framework (e.g., React, Vue, Angular) for the Web-UI.</td>
      <td>Framework selected, sample components created.</td>
      <td>Done</td>
      <td>CJ</td>
    </tr>
    <tr>
      <td>Create design system</td>
      <td>Develop a basic design</td>
      <td>Unified color palette, fonts, and basic components available.</td>
      <td>In progress</td>
      <td>CJ</td>
    </tr>
    <tr>
      <td>Integrate Translation API</td>
      <td>Implement the connection to the translation API.</td>
      <td>API responses are displayed correctly in the frontend.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Develop text translation input form</td>
      <td>Create a form for users to input text for translation.</td>
      <td>Input and target languages selectable, translations displayed.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Implement real-time translation feedback</td>
      <td>Add a loading indicator for translations.</td>
      <td>Progress indicator appears during API queries.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Implement audio recording functionality</td>
      <td>Add functionality to allow audio recording in the browser.</td>
      <td>Recordings are captured and played back correctly in the frontend.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Integrate STT API</td>
      <td>Connect the recording functionality to the Speech-to-Text API.</td>
      <td>Text output based on audio input works correctly.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Add error handling for audio files</td>
      <td>Develop robust error handling for invalid or missing audio inputs.</td>
      <td>Clear error messages are displayed.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Integrate text-to-audio conversion</td>
      <td>Create functionality to convert text to audio.</td>
      <td>Input text is correctly converted into audio files and played back.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Implement audio player</td>
      <td>Create an audio player with fuctions like changing playback speed.</td>
      <td>Working audio player</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Implement image upload functionality</td>
      <td>Add functionality to allow image uploads.</td>
      <td>Uploaded images are displayed and ready for analysis.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Integrate OCR API</td>
      <td>Implement the connection to the OCR API.</td>
      <td>Text is extracted from images and displayed in the UI.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Add OCR result review and editing</td>
      <td>Provide an option to edit detected text.</td>
      <td>Users can manually adjust detected text.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Integrate Export translations</td>
      <td>Develop functionality to download translations as files.</td>
      <td>Translations are exportable as TXT or CSV.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Integrate Export audio</td>
      <td>Add the ability to download generated audio files.</td>
      <td>Audio files are exportable as MP3 or WAV.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Integrate Export OCR text</td>
      <td>Develop functionality to export detected OCR text.</td>
      <td>Detected text is exportable as a file.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Conduct usability tests</td>
      <td>Test the UI’s usability with various users.</td>
      <td>Feedback collected and analyzed.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Optimize performance</td>
      <td>Improve loading times and responsiveness of the Web-UI.</td>
      <td>All functions load within 1 second (if API responds).</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Test cross-browser compatibility</td>
      <td>Ensure the UI works across different browsers.</td>
      <td>Works in Chrome, Firefox, and Edge.</td>
      <td>To Do</td>
      <td></td>
    </tr>
  </tbody>
</table>

<h2>Epic 3: Text Translation</h2>
<table border="1" cellpadding="6" cellspacing="0">
  <thead>
    <tr>
      <th>Task</th>
      <th>Description</th>
      <th>Acceptance Criteria</th>
      <th>Status</th>
      <th>Assigned to</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Research Available Translation Models</td>
      <td>Evaluate and compare multiple AI translation models based on accuracy, speed, and cost.</td>
      <td>A report is created summarizing the strengths, weaknesses, and use cases of each model.</td>
      <td>Done</td>
      <td>JK</td>
    </tr>
    <tr>
      <td>Select Optimal Translation Model</td>
      <td>Choose the most suitable translation model for Textify based on the evaluation.</td>
      <td>The selected model is documented with justification for its choice.</td>
      <td>Done</td>
      <td>JK</td>
    </tr>
    <tr>
      <td>Integrate Chosen Translation Model API</td>
      <td>Connect the application backend to the selected translation model’s API.</td>
      <td>Translation requests are sent and responses are received successfully.</td>
      <td>In Progress</td>
      <td></td>
    </tr>
    <tr>
      <td>Test and Validate Translation Accuracy</td>
      <td>Conduct extensive testing of the integrated model to ensure translations are accurate and meet user requirements.</td>
      <td>Accuracy is validated for multiple language pairs with real-world test cases.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Optimize API Performance</td>
      <td>Implement caching, batching, or other optimization techniques to reduce API latency and improve throughput.</td>
      <td>Translation responses are consistently delivered within 2 seconds for texts under 500 words.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Document the Integration Process</td>
      <td>Create developer documentation explaining how the translation model is integrated, including API details and fallback handling.</td>
      <td>Documentation is complete and accessible to team members.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Write Unit Tests for Translation Features</td>
      <td>Develop tests for input validation, API calls, and UI components to ensure consistent behavior.</td>
      <td>All tests pass for a variety of scenarios, including edge cases.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Conduct User Acceptance Testing (UAT)</td>
      <td>Gather feedback from test users to verify the usability and reliability of the translation feature.</td>
      <td>Feedback is reviewed and necessary adjustments are implemented.</td>
      <td>To Do</td>
      <td></td>
    </tr>
  </tbody>
</table>

<h2>Epic 4: Text-to-Speech (TTS)</h2>
<table border="1" cellpadding="6" cellspacing="0">
  <thead>
    <tr>
      <th>Task</th>
      <th>Description</th>
      <th>Acceptance Criteria</th>
      <th>Status</th>
      <th>Assigned to</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Research Available TTS Models</td>
      <td>Evaluate TTS models based on voice naturalness, speed, and language support.</td>
      <td>A comparison report highlighting the best models for implementation is created.</td>
      <td>In progress</td>
      <td></td>
    </tr>
    <tr>
      <td>Select Optimal TTS Model</td>
      <td>Choose the most suitable TTS model for Textify.</td>
      <td>Documentation of the selected model and justification for its use.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Integrate Chosen TTS API</td>
      <td>Connect the application to the selected TTS model’s API for generating audio output.</td>
      <td>Text inputs are successfully converted into audio.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Optimize TTS Performance</td>
      <td>Ensure audio is generated within 2 seconds for text under 500 words.</td>
      <td>Performance benchmarks are achieved.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Enable Audio File Download</td>
      <td>Allow users to download generated audio files in MP3 or WAV formats.</td>
      <td>Files are correctly downloaded in the chosen format.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Write Unit Tests for TTS Features</td>
      <td>Develop tests for TTS API calls and UI components.</td>
      <td>All tests pass with no failures.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Conduct User Acceptance Testing (UAT)</td>
      <td>Collect feedback on TTS quality and UI functionality.</td>
      <td>Issues identified during testing are resolved.</td>
      <td>To Do</td>
      <td></td>
    </tr>
  </tbody>
</table>

<h2>Epic 5: Speech-to-Text (STT)</h2>
<table border="1" cellpadding="6" cellspacing="0">
  <thead>
    <tr>
      <th>Task</th>
      <th>Description</th>
      <th>Acceptance Criteria</th>
      <th>Status</th>
      <th>Assigned to</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Research Available STT Models</td>
      <td>Evaluate STT models based on accuracy, noise handling, and speed.</td>
      <td>A detailed comparison of available models is documented.</td>
      <td>In Progress</td>
      <td>JK</td>
    </tr>
    <tr>
      <td>Select Optimal STT Model</td>
      <td>Choose the best STT model for Textify, focusing on accuracy in noisy environments.</td>
      <td>The selected model is documented with rationale.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Integrate Chosen STT API</td>
      <td>Connect the application to the chosen STT API for transcribing speech to text.</td>
      <td>Audio inputs are successfully transcribed to text.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Implement Preprocessing for Noise Reduction</td>
      <td>Add preprocessing steps to improve transcription accuracy in noisy environments.</td>
      <td>Transcription accuracy meets the target of 90%.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Create Audio Upload Feature</td>
      <td>Allow users to upload audio files for transcription.</td>
      <td>Files in MP3, WAV, and other standard formats are accepted.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Add Error Messaging for Invalid Audio</td>
      <td>Notify users of unsupported formats or poor audio quality.</td>
      <td>Clear error messages are displayed when needed.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Write Unit Tests for STT Features</td>
      <td>Create tests for preprocessing, API integration, and transcription accuracy.</td>
      <td>All tests pass and meet accuracy targets.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Conduct User Acceptance Testing (UAT)</td>
      <td>Collect feedback on transcription accuracy and usability.</td>
      <td>Feedback is reviewed and used to make improvements.</td>
      <td>To Do</td>
      <td></td>
    </tr>
  </tbody>
</table>

<h2>Epic 6: Optical Character Recognition (OCR)</h2>
<table border="1" cellpadding="6" cellspacing="0">
  <thead>
    <tr>
      <th>Task</th>
      <th>Description</th>
      <th>Acceptance Criteria</th>
      <th>Status</th>
      <th>Assigned to</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Research OCR Models</td>
      <td>Compare OCR models based on text accuracy, font support, and processing speed.</td>
      <td>A report of recommended models is completed.</td>
      <td>In progress</td>
      <td>AS</td>
    </tr>
    <tr>
      <td>Select Optimal OCR Model</td>
      <td>Choose the OCR model with the best performance for various image formats.</td>
      <td>The selected model and rationale are documented.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Integrate OCR API</td>
      <td>Connect the backend to the chosen OCR API for extracting text from images.</td>
      <td>Uploaded images are successfully processed.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Add Preprocessing for Image Optimization</td>
      <td>Implement preprocessing (e.g., de-skewing, noise reduction) to improve OCR accuracy.</td>
      <td>Preprocessed images yield improved results.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Create Image Upload Feature</td>
      <td>Allow users to upload images for text recognition.</td>
      <td>Images in PNG, JPEG, and other common formats are accepted.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Write Unit Tests for OCR Features</td>
      <td>Create tests for image processing, OCR accuracy, and text extraction.</td>
      <td>Tests pass and ensure high accuracy.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Conduct User Acceptance Testing (UAT)</td>
      <td>Gather feedback on OCR performance and accuracy.</td>
      <td>Feedback is reviewed and used to make improvements.</td>
      <td>To Do</td>
      <td></td>
    </tr>
  </tbody>
</table>

<h2>Epic 7: Exports</h2>
<table border="1" cellpadding="6" cellspacing="0">
  <thead>
    <tr>
      <th>Task</th>
      <th>Description</th>
      <th>Acceptance Criteria</th>
      <th>Status</th>
      <th>Assigned to</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Research Export Formats</td>
      <td>Evaluate different export formats (PDF, Word, TXT) based on compatibility, quality, and ease of use.</td>
      <td>A report on the most suitable formats for export is created.</td>
      <td>Done</td>
      <td>ALL</td>
    </tr>
    <tr>
      <td>Implement Export to PDF</td>
      <td>Develop functionality to export translated text to PDF format.</td>
      <td>Users can export translations into PDF successfully.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Implement Export to Word</td>
      <td>Develop functionality to export translated text to Word format.</td>
      <td>Users can export translations into Word documents.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Implement Export to TXT</td>
      <td>Develop functionality to export translated text to plain text (TXT) format.</td>
      <td>Users can export translations as TXT files.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Test Export Functionality</td>
      <td>Test the export functions for all formats (PDF, Word, TXT) to ensure they work correctly.</td>
      <td>All export formats work correctly and meet quality standards.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Add Error Handling for Export Failures</td>
      <td>Implement error messages when an export fails (e.g., invalid file format, file size too large).</td>
      <td>Users receive clear error messages if an export fails.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Write Unit Tests for Export Features</td>
      <td>Develop tests for export API calls and UI components.</td>
      <td>All tests pass for export functionality.</td>
      <td>To Do</td>
      <td></td>
    </tr>
    <tr>
      <td>Conduct User Acceptance Testing (UAT)</td>
      <td>Gather feedback from users on the export functionality.</td>
      <td>Adjustments are made based on feedback from UAT.</td>
      <td>To Do</td>
      <td></td>
    </tr>
  </tbody>
</table>

</body>
</html>
