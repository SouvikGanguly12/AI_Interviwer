# AI Interview Streamlit App

A Streamlit-based AI interview preparation application that generates interview questions from a resume, evaluates answers, and produces a PDF report. The app supports resume uploads in PDF, TXT, MD, and RTF formats.

## Features

- Resume upload via drag-and-drop or file selection
- Resume text extraction from PDF and text-based files
- Automatic question generation from resume contents, project mentions, and certifications
- Answer scoring and feedback using pre-defined rubrics
- Interview timer and progress tracking
- Session state management for browser sessions
- PDF report generation of interview questions and results

## Project Structure

- `streamlit_app.py` - Main Streamlit frontend application
- `Interview/`
  - `question_generator.py` - Creates interview questions from resume text
  - `answer_evaluator.py` - Scores and provides feedback on answers
  - `interview.py` - Interview control utilities and question flow
- `resume_parser/`
  - `skill_extractor.py` - Extracts text from uploaded resume files
  - `project_extractor.py` - Placeholder for project extraction logic
  - `certificate_extractor.py` - Placeholder for certification extraction logic
- `pdf/`
  - `pdf_generator.py` - Builds downloadable interview reports
- `requirement.txt` - Required Python dependencies with pinned versions

## Requirements

The project requires Python 3.10 and these dependencies:

- `streamlit==1.55.0`
- `reportlab==4.4.10`
- `pdfminer.six==20260107`

## Installation

1. Open a terminal in `streamlit/`.
2. Create and activate a virtual environment (recommended):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirement.txt
   ```

## Run the app

From the `streamlit/` folder run:

```powershell
streamlit run streamlit_app.py
```

Then open the local URL shown in the terminal.

## Usage

1. Use the slider to choose the maximum number of interview questions.
2. Upload a resume in PDF, TXT, MD, or RTF format.
3. Wait for the app to extract resume text and generate interview questions.
4. Start the interview and answer questions in the app.
5. View the score, feedback, and download a PDF report if available.

## Notes

- The app uses SHA256 hashing to detect repeated uploads and avoid regenerating questions unnecessarily.
- `project_extractor.py` and `certificate_extractor.py` are included as extension points for more advanced resume parsing.
- `Interview/question_generator.py` uses resume content heuristics to determine relevant question categories.

## Troubleshooting

- If the app fails to start, verify the virtual environment is active and dependencies are installed.
- Ensure the `streamlit` folder is the current working directory when running the app.
- For import issues, confirm that local modules are imported using relative or package-local names and not as `streamlit.*`.

## License

This repository does not include a license file by default. Add a `LICENSE` if you want to publish or share the project with license terms.
