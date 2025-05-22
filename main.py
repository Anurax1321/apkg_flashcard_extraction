import zipfile
import sqlite3
import os
import re
import html

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

def read_apkg_to_txt(apkg_path, output_txt):
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
    #
    # with open(output_txt, 'w', encoding='utf-8') as f:
    #     # for idx, (flds,) in enumerate(rows, start=1):
    #     #     parts = flds.split('\x1f')
    #     #     if idx in (1, 2):
    #     #         print(parts)
    #     #     question = clean_text(parts[0]) if len(parts) >= 1 else ''
    #     #     answer   = clean_text(parts[1]) if len(parts) >= 2 else ''
    #     #     f.write(f"Flashcard {idx}\n")
    #     #     f.write(f"Question: {question}\n")
    #     #     f.write(f"Answer: {answer}\n\n")

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

if __name__ == '__main__':
    apkg_file = r"C:\Users\jyoth\PycharmProjects\apkg_flashcard_extraction\data\JAnki_STEP_2_internal_MedicinePART_I.apkg"
    output_txt = r'C:\Users\jyoth\PycharmProjects\apkg_flashcard_extraction\final\flashcards_extracted.txt'
    read_apkg_to_txt(apkg_file, output_txt)

    # with open(r"C:\Users\jyoth\PycharmProjects\rohan_flashcards\final\flashcards_extracted.txt", 'r', encoding='utf-8') as f:
    #     content = f.read()  # read the entire file into one string
    #     # or, to read line by line:
    #     # lines = f.readlines()   # returns a list of lines
    # flash = content.split("Flashcard")
    # # print(content)
    # # print(flash[0])
    # print(flash[1])
    # print(flash[2])
    # # print(flash[3])
    # question = flash[1].split("Question: ")[1].split("?")[0] + "?"
    # ans = flash[1].split("Question: ")[1].split("?")[1]
    # print(f"question: {question}")
    # print(f"ans: {ans}")
    #
    # flashcards = []
    # current = {}

    # with open(r"C:\Users\jyoth\PycharmProjects\apkg_flashcard_extraction\final\flashcards_extracted.txt",
    #           'r', encoding='utf-8') as f:
    #     for raw in f:
    #         line = raw.strip()
    #         if not line:
    #             # skip empty lines
    #             continue
    #
    #         # start of a new card
    #         if line.startswith("Flashcard "):
    #             # push the last card, if any
    #             if current:
    #                 flashcards.append(current)
    #             num = line.split()[1]
    #             current = {
    #                 "number": num,
    #                 "question": "N/A",
    #                 "answer": "Dumb—you don't get to know the answer for this, study better!"
    #             }
    #
    #         # question line
    #         elif line.startswith("Question:"):
    #             q = line[len("Question:"):].strip()
    #             if q:
    #                 current["question"] = q
    #
    #         # answer line
    #         elif line.startswith("Answer:"):
    #             a = line[len("Answer:"):].strip()
    #             if a:
    #                 current["answer"] = a
    #
    #     # don’t forget the very last one
    #     if current:
    #         flashcards.append(current)

    # Now flashcards is a list of dicts—let’s print the first two to verify:
    # for card in flashcards[:2]:
    #     print(f"Flashcard {card['number']}")
    #     print("  Q:", card["question"])
    #     print("  A:", card["answer"])
    #     print()
