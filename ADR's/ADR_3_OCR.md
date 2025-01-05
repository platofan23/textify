# ADR003: Decision to Use EasyOCR and docTR for OCR Functionality

## Context
We need to implement Optical Character Recognition (OCR) functionality in our project to extract text from images. The OCR functionality should support multiple languages and be efficient in terms of performance and accuracy.

## Decision
We have decided to use EasyOCR and docTR as the OCR libraries for our project.

### EasyOCR
- **Pros:**
  - Supports multiple languages.
  - Easy to use and integrate.
  - Good accuracy for various languages.
  - Actively maintained and has a large community.

- **Cons:**
  - May not be as fast as some other OCR libraries.
  - Requires additional dependencies like PyTorch.

### docTR
- **Pros:**
  - High accuracy for text detection and recognition.
  - Supports GPU acceleration, which can significantly improve performance.
  - Provides a modern and efficient approach to OCR using deep learning models.

- **Cons:**
  - Limited language support compared to EasyOCR.
  - Requires a GPU for optimal performance, which may not be available in all environments.

## Alternatives Considered
- **Tesseract OCR:**
  - Pros: Open-source, supports multiple languages, widely used.
  - Cons: Slower performance, less accurate compared to EasyOCR and docTR.

- **Google Cloud Vision OCR:**
  - Pros: High accuracy, supports multiple languages, easy to use.
  - Cons: Requires a paid subscription, dependency on external service.

## Consequences
- By using EasyOCR, we can support multiple languages and provide a good balance between ease of use and accuracy.
- By using docTR, we can leverage GPU acceleration for faster and more accurate OCR, especially for complex documents.
- We need to ensure that our deployment environment supports the necessary dependencies for both EasyOCR and docTR, including PyTorch and GPU support.

## Implementation
- Integrate EasyOCR and docTR into the `multi_reader` function in `service_ocr.py`.
- Provide options for users to choose between EasyOCR and docTR based on their requirements.
- Ensure that the necessary dependencies are included in the project requirements.

## Status
Accepted
