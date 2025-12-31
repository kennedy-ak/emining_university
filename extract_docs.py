"""
Script to extract text from Word documents in the e-mining folder
"""
import os
import docx2txt
from pathlib import Path

def extract_doc_text(file_path):
    """Extract text from .doc or .docx file"""
    try:
        # Try with docx2txt first
        text = docx2txt.process(str(file_path))
        return text
    except Exception as e:
        print(f"Error with docx2txt for {file_path}: {e}")
        # Try with python-docx for .docx files
        try:
            from docx import Document
            doc = Document(str(file_path))
            text = '\n'.join([para.text for para in doc.paragraphs])
            return text
        except Exception as e2:
            print(f"Error with python-docx for {file_path}: {e2}")
            return None

def main():
    # Path to the e-mining documents
    docs_path = Path("e-mining (1)/e-mining")

    # First, extract instructor profiles
    profile_file = docs_path / "Profile of Training Team.doc"
    if profile_file.exists():
        print("=" * 80)
        print("INSTRUCTOR PROFILES")
        print("=" * 80)
        text = extract_doc_text(profile_file)
        if text:
            print(text[:2000])  # Print first 2000 characters
            print("\n... (truncated for preview)")

    # Extract a sample course document (the .docx file)
    sample_course = docs_path / "Advanced Professional Certificatein Mining usd(1).docx"
    if sample_course.exists():
        print("\n" + "=" * 80)
        print("SAMPLE COURSE: Advanced Professional Certificate")
        print("=" * 80)
        text = extract_doc_text(sample_course)
        if text:
            print(text[:2000])  # Print first 2000 characters
            print("\n... (truncated for preview)")

    # List all course documents
    print("\n" + "=" * 80)
    print("ALL COURSE DOCUMENTS")
    print("=" * 80)
    if docs_path.exists():
        for file in sorted(docs_path.glob("*.doc*")):
            if file.name != "Profile of Training Team.doc":
                print(f"- {file.name}")

if __name__ == "__main__":
    main()
