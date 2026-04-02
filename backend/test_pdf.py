from app.services.pdf_service import generate_pdf_from_text
import os

content = """
# Sample BRD
## Introduction
This is a sample document for testing the PDF generation service.

### Features
* Feature 1: Login
* Feature 2: Dashboard

| Column 1 | Column 2 |
|---|---|
| Value 1 | Value 2 |

End of document.
"""

output_path = generate_pdf_from_text(content, "test.pdf")
print(f"Generated PDF at: {output_path}")
if os.path.exists(output_path):
    print("Success: PDF file created.")
else:
    print("Failure: PDF file not found.")
