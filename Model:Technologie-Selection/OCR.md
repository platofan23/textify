# ADR 002: Selection of OCR Model

## Status
On Hold

## Context
Textify requires a robust and scalable OCR model to deliver high-quality scanning of user images. After evaluating various OCR models such as Idefix, Tesseract, PaddleOCR, EasyOCR the selection was narrowed to Idefix, EasyOCR based on key factors including:
- Scanning quality
- Language Support
- Adaptability
- Integration and compatibility
- Resource requirements
- Cost
- Scalability
- Ethical and legal considerations

## Decision
Textify will adopt a combination of **Idefix**, **EasyOCR**  and **Tesseract** as the primary translation models.

## Rationale
- **Idefix**
  - **Pros**: Modern and likely optimized for speed.
    - May offer enhanced performance over older models.
   - **Cons**: Limited documentation and community support as it is a newer or less established option.
    - Requires evaluation of licensing terms to ensure it's free to use.

- **Tesseract**
  - **Pros**: Open-source and completely free (Apache License 2.0).
    - Well-documented and widely adopted, with a large community.
    - Supports multiple languages and has advanced configuration options.
  - **Cons**: Speed might not match more modern models, especially on large documents.
    - Requires fine-tuning for specific use cases to achieve high accuracy.

## Alternatives
1. **OCRmyPDF**:
   - **Consideration**: (Tesseract-based): Tailored for PDF workflows, supports text extraction and text layer addition.

2. **PaddleOCR**:
   - **Pros**: Open-source, developed by Baidu.
    - High speed and accuracy with support for multiple languages.

3. **EasyOCR**:
  - **Pros**: Open-source with user-friendly integration.
    - Good language support and reasonable speed.

## Consequences
- **Positive**:
  - Leveraging Tesseract ensures stability and ease of debugging due to its maturity and wide adoption.
  - Free cost of use aligns with the project’s budget constraints.
  
- **Negative**:
  - Might need optimization or preprocessing for speed improvements.
  - Initial setup and fine-tuning could require additional effort compared to modern models like PaddleOCR.

- **Negative**:
  - Should Tesseract fail to meet speed requirements, PaddleOCR or other alternatives will.

## Implementation
  - The OCR Service will output a uniform Text and the user or service itself can switch between Models to perform speedups or improve Quality

## Decision Owner
Engineering Lead – Textify Project

