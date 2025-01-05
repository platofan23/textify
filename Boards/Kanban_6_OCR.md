<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
</head>
<body>

<h1>Kanban Board</h1>
<h2>Epic 6: Optical Character Recognition (OCR)</h2>
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
      <td>Research OCR Models</td>
      <td>Compare OCR models based on text accuracy, font support, and processing speed.</td>
      <td>A report of recommended models is completed.</td>
      <td>In progress</td>
      <td>AS</td>
      <td>5</td>
    </tr>
    <tr>
      <td>Select Optimal OCR Model</td>
      <td>Choose the OCR model with the best performance for various image formats.</td>
      <td>The selected model and rationale are documented.</td>
      <td>To Do</td>
      <td></td>
      <td>5</td>
    </tr>
    <tr>
      <td>Integrate OCR API</td>
      <td>Connect the backend to the chosen OCR API for extracting text from images.</td>
      <td>Uploaded images are successfully processed.</td>
      <td>To Do</td>
      <td></td>
      <td>5</td>
    </tr>
    <tr>
      <td>Add Preprocessing for Image Optimization</td>
      <td>Implement preprocessing (e.g., de-skewing, noise reduction) to improve OCR accuracy.</td>
      <td>Preprocessed images yield improved results.</td>
      <td>To Do</td>
      <td></td>
      <td>4</td>
    </tr>
    <tr>
      <td>Create Image Upload Feature</td>
      <td>Allow users to upload images for text recognition.</td>
      <td>Images in PNG, JPEG, and other common formats are accepted.</td>
      <td>To Do</td>
      <td></td>
      <td>5</td>
    </tr>
    <tr>
      <td>Write Unit Tests for OCR Features</td>
      <td>Create tests for image processing, OCR accuracy, and text extraction.</td>
      <td>Tests pass and ensure high accuracy.</td>
      <td>To Do</td>
      <td></td>
      <td>5</td>
    </tr>
    <tr>
      <td>Conduct User Acceptance Testing (UAT)</td>
      <td>Gather feedback on OCR performance and accuracy.</td>
      <td>Feedback is reviewed and used to make improvements.</td>
      <td>To Do</td>
      <td></td>
      <td>4</td>
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
      <th>Importance 1(very low) .. 5(very hight)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Research Export Formats</td>
      <td>Evaluate different export formats (PDF, Word, TXT) based on compatibility, quality, and ease of use.</td>
      <td>A report on the most suitable formats for export is created.</td>
      <td>Done</td>
      <td>ALL</td>
      <td>5</td>
    </tr>
    <tr>
      <td>Implement Export to PDF</td>
      <td>Develop functionality to export translated text to PDF format.</td>
      <td>Users can export translations into PDF successfully.</td>
      <td>To Do</td>
      <td></td>
      <td>5</td>
    </tr>
    <tr>
      <td>Implement Export to Word</td>
      <td>Develop functionality to export translated text to Word format.</td>
      <td>Users can export translations into Word documents.</td>
      <td>To Do</td>
      <td></td>
      <td>2</td>
    </tr>
    <tr>
      <td>Implement Export to TXT</td>
      <td>Develop functionality to export translated text to plain text (TXT) format.</td>
      <td>Users can export translations as TXT files.</td>
      <td>To Do</td>
      <td></td>
      <td>5</td>
    </tr>
    <tr>
      <td>Test Export Functionality</td>
      <td>Test the export functions for all formats (PDF, Word, TXT) to ensure they work correctly.</td>
      <td>All export formats work correctly and meet quality standards.</td>
      <td>To Do</td>
      <td></td>
      <td>4</td>
    </tr>
    <tr>
      <td>Add Error Handling for Export Failures</td>
      <td>Implement error messages when an export fails (e.g., invalid file format, file size too large).</td>
      <td>Users receive clear error messages if an export fails.</td>
      <td>To Do</td>
      <td></td>
      <td>4</td>
    </tr>
    <tr>
      <td>Write Unit Tests for Export Features</td>
      <td>Develop tests for export API calls and UI components.</td>
      <td>All tests pass for export functionality.</td>
      <td>To Do</td>
      <td></td>
      <td>4</td>
    </tr>
    <tr>
      <td>Conduct User Acceptance Testing (UAT)</td>
      <td>Gather feedback from users on the export functionality.</td>
      <td>Adjustments are made based on feedback from UAT.</td>
      <td>To Do</td>
      <td></td>
      <td>54</td>
    </tr>
  </tbody>
</table>
</body>
</html>
