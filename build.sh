pip install -r requirements.txt

mkdir -p stockfish

# download guaranteed working Linux binary
curl -L https://stockfishchess.org/files/stockfish_16_linux_x64.zip -o stockfish.zip

# extract using python
python -m zipfile -e stockfish.zip stockfish

# move correct binary (path inside zip)
mv stockfish/stockfish_16_linux_x64/stockfish_16_x64 stockfish/stockfish

# make executable
chmod +x stockfish/stockfish