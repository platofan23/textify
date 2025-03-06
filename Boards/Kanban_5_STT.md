<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
</head>
<body>
<h1>Kanban Board</h1>
<h2>Epic 5: Speech-to-Text (STT)</h2>
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
      <td>Research Available STT Models</td>
      <td>Evaluate STT models based on accuracy, noise handling, and speed.</td>
      <td>A detailed comparison of available models is documented.</td>
      <td>Done</td>
      <td>JK</td>
      <td>1</td>
    </tr>
    <tr>
      <td>Select Optimal STT Model</td>
      <td>Choose the best STT model for Textify, focusing on accuracy in noisy environments.</td>
      <td>The selected model is documented with rationale.</td>
      <td>Done</td>
      <td></td>
      <td>1</td>
    </tr>
    <tr>
      <td>Integrate Chosen STT API</td>
      <td>Connect the application to the chosen STT API for transcribing speech to text.</td>
      <td>Audio inputs are successfully transcribed to text.</td>
      <td>Done</td>
      <td></td>
      <td>1</td>
    </tr>
    <tr>
      <td>Implement Preprocessing for Noise Reduction</td>
      <td>Add preprocessing steps to improve transcription accuracy in noisy environments.</td>
      <td>Transcription accuracy meets the target of 90%.</td>
      <td>To Do</td>
      <td></td>
      <td>1</td>
    </tr>
    <tr>
      <td>Create Audio Upload Feature</td>
      <td>Allow users to upload audio files for transcription.</td>
      <td>Files in MP3, WAV, and other standard formats are accepted.</td>
      <td>Dpme</td>
      <td></td>
      <td>1</td>
    </tr>
    <tr>
      <td>Add Error Messaging for Invalid Audio</td>
      <td>Notify users of unsupported formats or poor audio quality.</td>
      <td>Clear error messages are displayed when needed.</td>
      <td>To Do</td>
      <td></td>
      <td>1</td>
    </tr>
    <tr>
      <td>Write Unit Tests for STT Features</td>
      <td>Create tests for preprocessing, API integration, and transcription accuracy.</td>
      <td>All tests pass and meet accuracy targets.</td>
      <td>Done</td>
      <td></td>
      <td>1</td>
    </tr>
    <tr>
      <td>Conduct User Acceptance Testing (UAT)</td>
      <td>Collect feedback on transcription accuracy and usability.</td>
      <td>Feedback is reviewed and used to make improvements.</td>
      <td>Done</td>
      <td></td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</body>
</html>
