import zipfile, json, os, shutil, re, sqlite3

apkg = r"C:\Users\jyoth\PycharmProjects\rohan_flashcards\data\JAnki_STEP_2_internal_MedicinePART_I.apkg"            # path to your .apkg
extract_dir = "extracted_apkg"    # temp folder
out = "images_out"                # where you’ll dump named images

# 1) Unzip if you haven’t already
os.makedirs(extract_dir, exist_ok=True)
with zipfile.ZipFile(apkg, 'r') as z:
    z.extractall(extract_dir)

# 2) Read media map
media_map = json.load(open(os.path.join(extract_dir, "media"), "r"))

# 3) Copy raw files to a sane folder+filename
os.makedirs(out, exist_ok=True)
for key, fname in media_map.items():
    src = os.path.join(extract_dir, key)
    dst = os.path.join(out, fname)
    if os.path.exists(src):
        shutil.copy(src, dst)

print(f"Pulled out {len(media_map)} files into '{out}/'")