import zipfile, sqlite3, os, re, html
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

def extract_apkg(apkg_path, extract_dir):
    """
    Extracts the .apkg file (a zip archive) into the given directory.
    """
    with zipfile.ZipFile(apkg_path, 'r') as z:
        z.extractall(extract_dir)

def clean_text(text):
    """
    Cleans Anki field text by:
      - Removing cloze markers like {{c1::…}}
      - Stripping HTML tags
      - Unescaping HTML entities
    """
    text = re.sub(r'\{\{c\d+::|}}', '', text)   # remove cloze
    text = re.sub(r'<[^>]+>', '', text)          # strip HTML tags
    return html.unescape(text).strip()           # unescape entities

def write_flashcards_to_pdf(flashcards, output_pdf_path):
    c = canvas.Canvas(output_pdf_path, pagesize=LETTER)
    width, height = LETTER

    for card in flashcards:
        # Page 1: Question
        c.setFont("Helvetica-Bold", 14)
        c.drawString(72, height - 72, f"Flashcard {card['number']}")
        c.setFont("Helvetica", 12)
        text_obj = c.beginText(72, height - 100)
        text_obj.textLines(f"Q: {card['question']}")
        c.drawText(text_obj)
        c.showPage()  # move to next page

        # Page 2: Answer
        c.setFont("Helvetica-Bold", 14)
        c.drawString(72, height - 72, f"Flashcard {card['number']} (Answer)")
        c.setFont("Helvetica", 12)
        text_obj = c.beginText(72, height - 100)
        text_obj.textLines(f"A: {card['answer']}")
        c.drawText(text_obj)
        c.showPage()  # move to next page again

    c.save()

def read_apkg_to_txt(apkg_path):
    """
    Reads the .apkg at apkg_path and writes all Q/A pairs
    to output_txt (utf-8).
    """
    extract_dir = 'extracted_apkg'
    os.makedirs(extract_dir, exist_ok=True)
    extract_apkg(apkg_path, extract_dir)

    # Path to the SQLite DB inside the extracted folder
    db_path = os.path.join(extract_dir, 'collection.anki2')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # The `flds` column holds all fields separated by the \x1f character
    cursor.execute("SELECT flds FROM notes")
    rows = cursor.fetchall()

    flashcards =[]
    for idx, (flds,) in enumerate(rows, start=1):
        parts = flds.split('?')
        if idx in (1, 2):
            print(parts)
            # re.findall(r'<img\s+src="([^"]+)"', parts)
        question = clean_text(''.join(parts[0:-1])) if len(parts) >= 1 else ''
        answer   = clean_text(parts[-1]) if len(parts) >= 2 else ''

        current = {
            "number": idx,
            "question": question,
            "answer": answer
        }
        flashcards.append(current)

        # f.write(f"Flashcard {idx}\n")
        # f.write(f"Question: {question}?\n")
        # f.write(f"Answer: {answer}\n\n")

    conn.close()
    print(f"Extracted: {len(rows)} rows")
    print(f"Extracted: {len(flashcards)} flashcards")
    print(flashcards[0:3])
    print(flashcards[1]['question'])
    print(flashcards[1]['answer'])
    return flashcards

if __name__ == '__main__':
    apkg_file = r"C:\Users\jyoth\PycharmProjects\apkg_flashcard_extraction\data\JAnki_STEP_2_internal_MedicinePART_I.apkg"
    output_pdf = r'C:\Users\jyoth\PycharmProjects\apkg_flashcard_extraction\final\flashcards_extracted.pdf'
    flashcards = read_apkg_to_txt(apkg_file)
    write_flashcards_to_pdf(flashcards, output_pdf)