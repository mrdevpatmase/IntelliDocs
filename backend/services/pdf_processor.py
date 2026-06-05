import fitz


def extract_text_from_pdf(pdf_path):

    pages = []

    doc = fitz.open(pdf_path)

    for page_num, page in enumerate(doc):

        pages.append({
            "page": page_num + 1,
            "text": page.get_text()
        })

    doc.close()

    return pages