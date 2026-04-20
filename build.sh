pip install -r requirements.txt

apt-get update && apt-get install -y unzip

curl -L https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-ubuntu-x86-64-avx2.zip -o stockfish.zip

unzip stockfish.zip

mkdir -p stockfish
mv stockfish*/stockfish* stockfish/stockfish

chmod +x stockfish/stockfish