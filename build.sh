pip install -r requirements.txt

# make folder
mkdir -p stockfish

# download raw binary (NOT zip)
curl -L https://github.com/official-stockfish/Stockfish/releases/download/sf_16/stockfish-ubuntu-x86-64-avx2 -o stockfish/stockfish

# make executable
chmod +x stockfish/stockfish