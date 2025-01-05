# ADR 004: Selection of Translation Model

## Status
Decided

## Context
Textify requires a robust and scalable translation model to deliver high-quality translations across multiple languages. After evaluating various translation models such as OpenNMT, Joey NMT, MarianMT, OPUS-MT, and LibreTranslate, the selection was narrowed to OPUS-MT, MarianMT, and LibreTranslate based on key factors including:
- Translation quality
- Language support
- Adaptability
- Integration and compatibility
- Resource requirements
- Cost
- Scalability
- Ethical and legal considerations

## Decision
Textify will adopt a combination of **OPUS-MT**, **MarianMT** (OPUS-MT is based on MariantMT so both are named), and **LibreTranslate** as the primary translation models.

## Rationale
- **OPUS-MT**
  - **Translation Quality**: High-quality translations suitable for production.
  - **Language Support**: Supports up to 1000 languages, ensuring broad accessibility.
  - **Adaptability**: High adaptability and seamless compatibility.
  - **Scalability**: Excellent scalability to handle large translation workloads.
  - **Conclusion**: Ideal for pretrained models, enabling rapid deployment.

- **MarianMT**
  - **Translation Quality**: Very high quality, especially for models that can be fine-tuned.
  - **Language Support**: Supports 1000 languages.
  - **Resource Requirements**: Higher resource demand but justified by exceptional accuracy.
  - **Adaptability**: Highly adaptable and integrates smoothly.
  - **Conclusion**: Excellent choice for pretrained models with the potential for customization.

- **LibreTranslate**
  - **Translation Quality**: Moderate to high, sufficient for basic translation needs.
  - **Cost**: Extremely cost-effective.
  - **User-Friendliness**: Easy to use, even for teams without extensive machine learning expertise.
  - **Conclusion**: Suitable for small to medium-sized projects with budget constraints.

## Alternatives
1. **OpenNMT**:
   - **Pros**: Highly adaptable and trainable for any language.
   - **Cons**: Requires significant machine learning expertise and computational resources.

2. **Joey NMT**:
   - **Pros**: Trainable for any language.
   - **Cons**: Limited scalability and lower translation quality.

## Consequences
- **Positive**:
  - Flexibility to switch between models depending on translation complexity.
  - OPUS-MT/MarianMT provide reliable, high-quality translations.
  - LibreTranslate offers a lightweight, cost-efficient alternative.
  
- **Negative**:
  - MarianMT and OPUS-MT may have higher resource demands.
  - Managing multiple models adds integration complexity.

## Implementation
  - The translation service will allow users to manually select between OPUS-MT/MarianMT, and LibreTranslate based on their specific translation needs.
  - A unified interface will be developed, enabling users to switch between models seamlessly, providing flexibility for different translation scenarios.

## Decision Owner
Engineering Lead – Textify Project

