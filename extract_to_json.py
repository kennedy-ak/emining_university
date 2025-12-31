"""
Script to help extract data from Word documents and prepare JSON files for import
"""
import json
from pathlib import Path
from docx import Document
import docx2txt

def extract_all_docx_files():
    """Extract text from all .docx files and create initial JSON structure"""
    docs_path = Path("e-mining (1)/e-mining")
    courses = []

    # Process all .docx files
    for doc_file in docs_path.glob("*.docx"):
        print(f"\nProcessing: {doc_file.name}")
        print("=" * 80)

        try:
            # Extract text
            doc = Document(str(doc_file))
            full_text = '\n'.join([para.text for para in doc.paragraphs])

            # Try to extract course title (usually in first few lines)
            lines = [line.strip() for line in full_text.split('\n') if line.strip()]
            title = lines[0] if lines else doc_file.stem

            # Create course structure
            course = {
                "title": title,
                "description": full_text[:500] + "...",  # First 500 chars as description
                "instructor": "To Be Assigned",
                "category": "Mining",
                "level": "intermediate",
                "price": 1500.00,
                "currency": "₵",
                "is_featured": False,
                "_source_file": doc_file.name,
                "_full_text_preview": full_text[:1000]
            }

            courses.append(course)

            # Print preview
            print(f"Title: {title}")
            print(f"Preview: {full_text[:200]}...")
            print()

        except Exception as e:
            print(f"Error processing {doc_file.name}: {e}")

    # Save to JSON file
    output_file = "data_templates/courses_extracted.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(courses, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Extracted {len(courses)} courses to {output_file}")
    print("\nNext steps:")
    print("1. Review and edit data_templates/courses_extracted.json")
    print("2. Extract instructor information from 'Profile of Training Team.doc'")
    print("3. Create data_templates/instructors.json with instructor data")
    print("4. Run: python manage.py import_courses --instructors data_templates/instructors.json --courses data_templates/courses_extracted.json")

def create_course_list_from_filenames():
    """Create a simple course list from all .doc files"""
    docs_path = Path("e-mining (1)/e-mining")
    courses = []

    print("\nAll course documents found:")
    print("=" * 80)

    for doc_file in sorted(docs_path.glob("*.doc*")):
        if "Profile" not in doc_file.name and "AAI" not in doc_file.name:
            # Clean up filename to create title
            title = doc_file.stem
            title = title.replace("_", " ").replace("-", " ")

            course = {
                "title": title,
                "description": f"Professional training course in {title}",
                "instructor": "To Be Assigned",
                "category": "Mining",
                "level": "intermediate",
                "price": 1500.00,
                "currency": "₵",
                "is_featured": False,
                "_source_file": doc_file.name
            }

            courses.append(course)
            print(f"- {title}")

    # Save to JSON
    output_file = "data_templates/courses_from_filenames.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(courses, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Created {len(courses)} course entries in {output_file}")
    print("\nYou can now:")
    print("1. Edit this file to add proper descriptions and assign instructors")
    print("2. Create data_templates/instructors.json")
    print("3. Import using: python manage.py import_courses --instructors data_templates/instructors.json --courses data_templates/courses_from_filenames.json")

if __name__ == "__main__":
    print("E-Mining Course Data Extraction")
    print("=" * 80)

    # Create data_templates directory if it doesn't exist
    Path("data_templates").mkdir(exist_ok=True)

    # Try to extract from .docx files first
    extract_all_docx_files()

    # Also create a list from all filenames as a backup
    create_course_list_from_filenames()
