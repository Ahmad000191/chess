pip install -r requirements.txt

curl -L https://stockfishchess.org/files/stockfish_16.1_linux_x64_avx2.zip -o stockfish.zip

unzip stockfish.zip
mkdir -p stockfish
mv stockfish*/stockfish* stockfish/stockfish

chmod +x stockfish/stockfish