"""Downloads Stockfish for Windows and places it in the stockfish/ folder."""
import urllib.request
import zipfile
import os
import shutil

STOCKFISH_URL = "https://github.com/official-stockfish/Stockfish/releases/download/sf_16.1/stockfish-windows-x86-64-avx2.zip"
DEST_DIR = os.path.join(os.path.dirname(__file__), "stockfish")
DEST_EXE = os.path.join(DEST_DIR, "stockfish.exe")

def download():
    if os.path.exists(DEST_EXE):
        print(f"Stockfish already present: {DEST_EXE}")
        return

    os.makedirs(DEST_DIR, exist_ok=True)
    zip_path = os.path.join(DEST_DIR, "stockfish.zip")

    print("Downloading Stockfish 16.1 for Windows...")
    print(f"URL: {STOCKFISH_URL}")

    def progress(block_num, block_size, total_size):
        pct = block_num * block_size / total_size * 100
        print(f"\r  {min(pct, 100):.1f}%", end='', flush=True)

    urllib.request.urlretrieve(STOCKFISH_URL, zip_path, reporthook=progress)
    print("\nExtracting...")

    with zipfile.ZipFile(zip_path, 'r') as z:
        for name in z.namelist():
            if name.endswith('.exe'):
                z.extract(name, DEST_DIR)
                extracted = os.path.join(DEST_DIR, name)
                shutil.move(extracted, DEST_EXE)
                # Clean up empty dirs
                for part in name.split('/')[:-1]:
                    try:
                        os.rmdir(os.path.join(DEST_DIR, part))
                    except Exception:
                        pass
                print(f"Stockfish extracted to: {DEST_EXE}")
                break

    os.remove(zip_path)
    print("Done! You can now run: python app.py")

if __name__ == "__main__":
    download()
