from pathlib import Path
from pdfminer.high_level import extract_text

def skill_extractor(resume_path):
    path = Path(resume_path)
    text = ""

    def read_text_file(file_path):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as fh:
            return fh.read()

    if path.is_dir():
        resume_files = sorted(path.glob('*'))
        for resume_file in resume_files:
            if resume_file.suffix.lower() == '.pdf':
                text += extract_text(str(resume_file)) + "\n"
            elif resume_file.suffix.lower() in ['.txt', '.md', '.rtf']:
                text += read_text_file(resume_file) + "\n"
    elif path.is_file():
        if path.suffix.lower() == '.pdf':
            text = extract_text(str(path))
        else:
            text = read_text_file(path)
    else:
        raise FileNotFoundError(f"Resume path not found: {resume_path}")

    return text
