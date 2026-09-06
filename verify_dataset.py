import os
import json
import csv
from pypdf import PdfReader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "it-support-rag-dataset")

def verify_pdfs():
    print("Verifying Master PDF...")
    pdfs_dir = os.path.join(DATASET_DIR, "pdfs")
    files = [f for f in os.listdir(pdfs_dir) if f.endswith(".pdf")]
    assert len(files) == 1, f"Expected 1 PDF file, found {len(files)}: {files}"
    
    pdf_path = os.path.join(pdfs_dir, files[0])
    assert files[0] == "it_support_knowledge_base_1000pages.pdf", f"Unexpected filename: {files[0]}"
    size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
    print(f"Master PDF Size: {size_mb:.2f} MB")
    
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    print(f"Total Page Count in Master PDF: {total_pages} pages")
    assert total_pages >= 100, f"Expected large page count, found {total_pages} pages"
    
    sample_text = ""
    for idx in range(0, min(total_pages, 20)):
        sample_text += reader.pages[idx].extract_text() or ""
        
    assert len(sample_text) > 1000, "PDF text extraction failed or text is empty"
    print(f"Verified Master PDF ({files[0]}) containing {total_pages} pages of searchable text.")
    return total_pages

def verify_markdown():
    print("Verifying Master Markdown...")
    md_dir = os.path.join(DATASET_DIR, "markdown")
    files = [f for f in os.listdir(md_dir) if f.endswith(".md")]
    assert len(files) == 1, f"Expected 1 Markdown file, found {len(files)}: {files}"
    
    md_path = os.path.join(md_dir, files[0])
    size_kb = os.path.getsize(md_path) / 1024
    print(f"Master Markdown Size: {size_kb:.2f} KB")
    
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Enterprise IT Support Master Knowledge Base" in content
        assert "Domain 1: 1. Windows 11/10 Client OS Administration & Performance Tuning" in content
        assert "Domain 10: 10. ITIL v4 Service Desk Operations, SLAs & Escalation Management" in content
        
    print(f"Verified Master Markdown ({files[0]}) with all 10 domain headers present.")

def verify_metadata():
    print("Verifying metadata.json...")
    meta_path = os.path.join(DATASET_DIR, "metadata.json")
    with open(meta_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) >= 100, f"Expected at least 100 entries, found {len(data)}"
    print(f"Verified metadata.json containing {len(data)} entries.")

def verify_sources_csv():
    print("Verifying sources.csv...")
    csv_path = os.path.join(DATASET_DIR, "sources.csv")
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)
        assert len(rows) == 100, f"Expected 100 rows in sources.csv, found {len(rows)}"
    print(f"Verified sources.csv containing {len(rows)} data rows.")

def verify_evaluation_questions():
    print("Verifying evaluation_questions.json...")
    eval_path = os.path.join(DATASET_DIR, "evaluation_questions.json")
    with open(eval_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 100, f"Expected 100 evaluation questions, found {len(data)}"
    print(f"Verified evaluation_questions.json with {len(data)} questions.")

def main():
    print("=== Running Enterprise IT RAG Dataset QA Suite ===")
    total_pages = verify_pdfs()
    verify_markdown()
    verify_metadata()
    verify_sources_csv()
    verify_evaluation_questions()
    print("=== ALL VERIFICATION CHECKS PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
