### Project Overview
This is a fiction visualization project based on UV management, aiming to automate the process of generating videos from novels, allowing creators to focus on just a few key points to complete video generation.

### Workflow Version 0.01
The current workflow assumes that character portraits in the novel won't change significantly. Here are the detailed workflow steps:

#### 1. Text Preprocessing
- **Task 1.1**: Segment the novel by chapters and store them.
  - **Requirement**: Implement a text segmentation module that can divide novel text by chapters and save to database/files.
- **Task 1.2**: Use large language models to analyze each chapter, extract important characters and related information, store them in a structured way, analyze main and secondary characters along the timeline, and determine which characters need portrait generation for better viewing experience.
  - **Requirement**: Integrate LLM API for text analysis and character information extraction.
- **Task 1.3**: Based on the extracted information, summarize character portrait features and organize them into prompts for image generation models.
  - **Requirement**: Implement prompt generation module to convert character information into image generation model inputs.

#### 2. Portrait Generation and Character Feature Database
- **Task 2.1**: Use image generation models to create portraits, manually review them, and build a portrait library containing different expressions of characters, using IP Adapter to generate prompts and store them with corresponding images.
  - **Requirement**: Integrate image generation model API and implement manual review process.
- **Task 2.2**: Build a character feature database based on the above data for maintaining character consistency.
  - **Requirement**: Design and implement character feature database.

#### 3. Audio Processing
- **Task 3.1**: Use text-to-speech models to generate corresponding audio based on image slices, using simplest voice settings.
  - **Requirement**: Integrate TTS model API.

#### 4. Video Composition
- **Task 4.1**: Combine images and audio along the timeline to generate videos.
  - **Requirement**: Implement video composition module.
- **Task 4.2**: Apply simplest animations (e.g., up-down movement) to images.
  - **Requirement**: Implement basic animation effects.

### Module Analysis
#### Systematic Character Management Strategy
1. **New Scene Requirement**: Check if character exists when new scene is needed.
2. **Character Exists?**: If yes, extract feature vectors and reference images; if no, create new character profile.
3. **Parameter Constraints**: Apply parameter constraints to extracted features.
4. **Generation Quality Check**: Verify portrait quality.
5. **CLIP-I > 0.85?**: Output if similarity > 0.85; otherwise adjust reference image weights.

### Tools and Models
- **Theoretical Tools**:
  - CLIP multimodal model
  - Midjourney character consistency
  - DALL-E 3 grid layout
  - IP Adapter for character consistency
  - ControlNet IP-Adapter
  - StoryMaker
- **Model Providers**:
  - Kling AI
