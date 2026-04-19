from flask import Flask, render_template, request, jsonify
import chess
import chess.engine
import chess.pgn
import os
import io

app = Flask(__name__)

STOCKFISH_PATH = os.path.join(os.path.dirname(__file__), "stockfish", "stockfish.exe")

OPENINGS = [
    # --- OPEN GAMES (1.e4 e5) ---
    {"name": "Italian Game", "eco": "C50", "moves": "e2e4 e7e5 g1f3 b8c6 f1c4", "category": "Open Games"},
    {"name": "Italian - Giuoco Piano", "eco": "C53", "moves": "e2e4 e7e5 g1f3 b8c6 f1c4 f8c5 c2c3", "category": "Open Games"},
    {"name": "Italian - Evans Gambit", "eco": "C51", "moves": "e2e4 e7e5 g1f3 b8c6 f1c4 f8c5 b2b4", "category": "Open Games"},
    {"name": "Italian - Two Knights Defense", "eco": "C55", "moves": "e2e4 e7e5 g1f3 b8c6 f1c4 g8f6", "category": "Open Games"},
    {"name": "Ruy Lopez (Spanish)", "eco": "C60", "moves": "e2e4 e7e5 g1f3 b8c6 f1b5", "category": "Open Games"},
    {"name": "Ruy Lopez - Berlin Defense", "eco": "C65", "moves": "e2e4 e7e5 g1f3 b8c6 f1b5 g8f6", "category": "Open Games"},
    {"name": "Ruy Lopez - Marshall Attack", "eco": "C89", "moves": "e2e4 e7e5 g1f3 b8c6 f1b5 a7a6 b5a4 g8f6 e1g1 f8e7 f1e1 b7b5 a4b3 e8g8 c2c3 d7d5", "category": "Open Games"},
    {"name": "Ruy Lopez - Morphy Defense", "eco": "C78", "moves": "e2e4 e7e5 g1f3 b8c6 f1b5 a7a6 b5a4", "category": "Open Games"},
    {"name": "King's Gambit", "eco": "C30", "moves": "e2e4 e7e5 f2f4", "category": "Open Games"},
    {"name": "King's Gambit Accepted", "eco": "C33", "moves": "e2e4 e7e5 f2f4 e5f4", "category": "Open Games"},
    {"name": "Scotch Game", "eco": "C44", "moves": "e2e4 e7e5 g1f3 b8c6 d2d4", "category": "Open Games"},
    {"name": "Scotch Gambit", "eco": "C44", "moves": "e2e4 e7e5 g1f3 b8c6 d2d4 e5d4 f1c4", "category": "Open Games"},
    {"name": "Four Knights Game", "eco": "C46", "moves": "e2e4 e7e5 g1f3 b8c6 b1c3 g8f6", "category": "Open Games"},
    {"name": "Vienna Game", "eco": "C25", "moves": "e2e4 e7e5 b1c3", "category": "Open Games"},
    {"name": "Petrov Defense", "eco": "C42", "moves": "e2e4 e7e5 g1f3 g8f6", "category": "Open Games"},
    # --- SICILIAN DEFENSE ---
    {"name": "Sicilian Defense", "eco": "B20", "moves": "e2e4 c7c5", "category": "Sicilian Defense"},
    {"name": "Sicilian - Najdorf", "eco": "B90", "moves": "e2e4 c7c5 g1f3 d7d6 d2d4 c5d4 f3d4 g8f6 b1c3 a7a6", "category": "Sicilian Defense"},
    {"name": "Sicilian - Dragon", "eco": "B70", "moves": "e2e4 c7c5 g1f3 d7d6 d2d4 c5d4 f3d4 g8f6 b1c3 g7g6", "category": "Sicilian Defense"},
    {"name": "Sicilian - Yugoslav Attack", "eco": "B76", "moves": "e2e4 c7c5 g1f3 d7d6 d2d4 c5d4 f3d4 g8f6 b1c3 g7g6 f1e2 f8g7 e1g1 e8g8 c1e3 b8c6 f2f3", "category": "Sicilian Defense"},
    {"name": "Sicilian - Scheveningen", "eco": "B80", "moves": "e2e4 c7c5 g1f3 d7d6 d2d4 c5d4 f3d4 g8f6 b1c3 e7e6", "category": "Sicilian Defense"},
    {"name": "Sicilian - Classical", "eco": "B56", "moves": "e2e4 c7c5 g1f3 b8c6 d2d4 c5d4 f3d4", "category": "Sicilian Defense"},
    {"name": "Sicilian - Kan (Taimanov)", "eco": "B41", "moves": "e2e4 c7c5 g1f3 e7e6 d2d4 c5d4 f3d4 a7a6", "category": "Sicilian Defense"},
    {"name": "Sicilian - Accelerated Dragon", "eco": "B34", "moves": "e2e4 c7c5 g1f3 b8c6 d2d4 c5d4 f3d4 g7g6", "category": "Sicilian Defense"},
    {"name": "Sicilian - Paulsen", "eco": "B46", "moves": "e2e4 c7c5 g1f3 e7e6 d2d4 c5d4 f3d4 b8c6", "category": "Sicilian Defense"},
    {"name": "Sicilian - Grand Prix Attack", "eco": "B23", "moves": "e2e4 c7c5 b1c3 b8c6 f2f4", "category": "Sicilian Defense"},
    {"name": "Sicilian - Rossolimo", "eco": "B30", "moves": "e2e4 c7c5 g1f3 b8c6 f1b5", "category": "Sicilian Defense"},
    # --- FRENCH DEFENSE ---
    {"name": "French Defense", "eco": "C00", "moves": "e2e4 e7e6", "category": "French Defense"},
    {"name": "French - Winawer", "eco": "C15", "moves": "e2e4 e7e6 d2d4 d7d5 b1c3 f8b4", "category": "French Defense"},
    {"name": "French - Classical", "eco": "C11", "moves": "e2e4 e7e6 d2d4 d7d5 b1c3 g8f6", "category": "French Defense"},
    {"name": "French - Tarrasch", "eco": "C03", "moves": "e2e4 e7e6 d2d4 d7d5 b1d2", "category": "French Defense"},
    {"name": "French - Advance", "eco": "C02", "moves": "e2e4 e7e6 d2d4 d7d5 e4e5", "category": "French Defense"},
    {"name": "French - Exchange", "eco": "C01", "moves": "e2e4 e7e6 d2d4 d7d5 e4d5", "category": "French Defense"},
    {"name": "French - Rubinstein", "eco": "C10", "moves": "e2e4 e7e6 d2d4 d7d5 b1c3 d5e4", "category": "French Defense"},
    # --- CARO-KANN ---
    {"name": "Caro-Kann Defense", "eco": "B10", "moves": "e2e4 c7c6", "category": "Caro-Kann"},
    {"name": "Caro-Kann - Classical", "eco": "B18", "moves": "e2e4 c7c6 d2d4 d7d5 b1c3 d5e4 c3e4 c8f5", "category": "Caro-Kann"},
    {"name": "Caro-Kann - Advance", "eco": "B12", "moves": "e2e4 c7c6 d2d4 d7d5 e4e5", "category": "Caro-Kann"},
    {"name": "Caro-Kann - Exchange", "eco": "B13", "moves": "e2e4 c7c6 d2d4 d7d5 e4d5 c6d5", "category": "Caro-Kann"},
    {"name": "Caro-Kann - Panov Attack", "eco": "B13", "moves": "e2e4 c7c6 d2d4 d7d5 e4d5 c6d5 c2c4", "category": "Caro-Kann"},
    {"name": "Caro-Kann - Fantasy Variation", "eco": "B12", "moves": "e2e4 c7c6 d2d4 d7d5 f2f3", "category": "Caro-Kann"},
    # --- QUEEN'S GAMBIT ---
    {"name": "Queen's Gambit", "eco": "D06", "moves": "d2d4 d7d5 c2c4", "category": "Queen's Gambit"},
    {"name": "Queen's Gambit Declined", "eco": "D30", "moves": "d2d4 d7d5 c2c4 e7e6", "category": "Queen's Gambit"},
    {"name": "Queen's Gambit Accepted", "eco": "D20", "moves": "d2d4 d7d5 c2c4 d5c4", "category": "Queen's Gambit"},
    {"name": "QGD - Orthodox", "eco": "D60", "moves": "d2d4 d7d5 c2c4 e7e6 b1c3 g8f6 c1g5 f8e7", "category": "Queen's Gambit"},
    {"name": "QGD - Cambridge Springs", "eco": "D52", "moves": "d2d4 d7d5 c2c4 e7e6 b1c3 g8f6 c1g5 b8d7 e2e3 c7c6 g1f3 d8a5", "category": "Queen's Gambit"},
    {"name": "QGD - Tartakower", "eco": "D58", "moves": "d2d4 d7d5 c2c4 e7e6 b1c3 g8f6 c1g5 f8e7 e2e3 e8g8 g1f3 h7h6 g5h4 b7b6", "category": "Queen's Gambit"},
    {"name": "Slav Defense", "eco": "D10", "moves": "d2d4 d7d5 c2c4 c7c6", "category": "Queen's Gambit"},
    {"name": "Semi-Slav Defense", "eco": "D43", "moves": "d2d4 d7d5 c2c4 c7c6 b1c3 g8f6 g1f3 e7e6", "category": "Queen's Gambit"},
    {"name": "Marshall Gambit (Slav)", "eco": "D31", "moves": "d2d4 d7d5 c2c4 c7c6 b1c3 e7e6 e2e4", "category": "Queen's Gambit"},
    # --- INDIAN DEFENSES ---
    {"name": "King's Indian Defense", "eco": "E60", "moves": "d2d4 g8f6 c2c4 g7g6 b1c3 f8g7 e2e4 d7d6", "category": "Indian Defenses"},
    {"name": "KID - Classical", "eco": "E91", "moves": "d2d4 g8f6 c2c4 g7g6 b1c3 f8g7 e2e4 d7d6 g1f3 e8g8 f1e2", "category": "Indian Defenses"},
    {"name": "KID - Samisch", "eco": "E81", "moves": "d2d4 g8f6 c2c4 g7g6 b1c3 f8g7 e2e4 d7d6 f2f3", "category": "Indian Defenses"},
    {"name": "KID - Four Pawns Attack", "eco": "E76", "moves": "d2d4 g8f6 c2c4 g7g6 b1c3 f8g7 e2e4 d7d6 f2f4", "category": "Indian Defenses"},
    {"name": "Nimzo-Indian Defense", "eco": "E20", "moves": "d2d4 g8f6 c2c4 e7e6 b1c3 f8b4", "category": "Indian Defenses"},
    {"name": "Nimzo-Indian - Rubinstein", "eco": "E46", "moves": "d2d4 g8f6 c2c4 e7e6 b1c3 f8b4 e2e3", "category": "Indian Defenses"},
    {"name": "Nimzo-Indian - Saemisch", "eco": "E26", "moves": "d2d4 g8f6 c2c4 e7e6 b1c3 f8b4 a2a3", "category": "Indian Defenses"},
    {"name": "Queen's Indian Defense", "eco": "E12", "moves": "d2d4 g8f6 c2c4 e7e6 g1f3 b7b6", "category": "Indian Defenses"},
    {"name": "Bogo-Indian Defense", "eco": "E11", "moves": "d2d4 g8f6 c2c4 e7e6 g1f3 f8b4", "category": "Indian Defenses"},
    {"name": "Grünfeld Defense", "eco": "D80", "moves": "d2d4 g8f6 c2c4 g7g6 b1c3 d7d5", "category": "Indian Defenses"},
    {"name": "Grünfeld - Exchange", "eco": "D85", "moves": "d2d4 g8f6 c2c4 g7g6 b1c3 d7d5 c4d5 f6d5 e2e4 d5c3 b2c3 f8g7", "category": "Indian Defenses"},
    {"name": "Benoni Defense", "eco": "A60", "moves": "d2d4 g8f6 c2c4 c7c5 d4d5 e7e6", "category": "Indian Defenses"},
    {"name": "Modern Benoni", "eco": "A70", "moves": "d2d4 g8f6 c2c4 c7c5 d4d5 e7e6 b1c3 e6d5 c4d5 d7d6 e2e4 g7g6", "category": "Indian Defenses"},
    # --- ENGLISH AND FLANK OPENINGS ---
    {"name": "English Opening", "eco": "A10", "moves": "c2c4", "category": "Flank Openings"},
    {"name": "English - Symmetrical", "eco": "A30", "moves": "c2c4 c7c5", "category": "Flank Openings"},
    {"name": "Reti Opening", "eco": "A09", "moves": "g1f3 d7d5 c2c4", "category": "Flank Openings"},
    {"name": "King's Indian Attack", "eco": "A07", "moves": "g1f3 d7d5 g2g3 g8f6 f1g2 e7e6 e1g1 f8e7 d2d3", "category": "Flank Openings"},
    {"name": "Bird's Opening", "eco": "A02", "moves": "f2f4", "category": "Flank Openings"},
    {"name": "Larsen's Opening", "eco": "A01", "moves": "b2b3", "category": "Flank Openings"},
    # --- DUTCH DEFENSE ---
    {"name": "Dutch Defense", "eco": "A80", "moves": "d2d4 f7f5", "category": "Dutch Defense"},
    {"name": "Dutch - Stonewall", "eco": "A92", "moves": "d2d4 f7f5 c2c4 g8f6 g1f3 e7e6 g2g3 d7d5", "category": "Dutch Defense"},
    {"name": "Dutch - Leningrad", "eco": "A89", "moves": "d2d4 f7f5 c2c4 g8f6 g1f3 g7g6 g2g3 f8g7", "category": "Dutch Defense"},
    # --- PIRC/MODERN ---
    {"name": "Pirc Defense", "eco": "B07", "moves": "e2e4 d7d6 d2d4 g8f6 b1c3 g7g6", "category": "Pirc/Modern"},
    {"name": "Modern Defense", "eco": "B06", "moves": "e2e4 g7g6", "category": "Pirc/Modern"},
    {"name": "Alekhine's Defense", "eco": "B02", "moves": "e2e4 g8f6", "category": "Pirc/Modern"},
    # --- LONDON/QUEEN PAWN ---
    {"name": "London System", "eco": "D02", "moves": "d2d4 d7d5 g1f3 g8f6 c1f4", "category": "Queen's Pawn Systems"},
    {"name": "London System (vs KID setup)", "eco": "A45", "moves": "d2d4 g8f6 g1f3 e7e6 c1f4", "category": "Queen's Pawn Systems"},
    {"name": "Colle System", "eco": "D04", "moves": "d2d4 d7d5 g1f3 g8f6 e2e3 e7e6 f1d3", "category": "Queen's Pawn Systems"},
    {"name": "Torre Attack", "eco": "A46", "moves": "d2d4 g8f6 g1f3 e7e6 c1g5", "category": "Queen's Pawn Systems"},
    {"name": "Trompowsky Attack", "eco": "A45", "moves": "d2d4 g8f6 c1g5", "category": "Queen's Pawn Systems"},
    # --- GAMBITS ---
    {"name": "Budapest Gambit", "eco": "A51", "moves": "d2d4 g8f6 c2c4 e7e5", "category": "Gambits"},
    {"name": "Benko Gambit", "eco": "A57", "moves": "d2d4 g8f6 c2c4 c7c5 d4d5 b7b5", "category": "Gambits"},
    {"name": "Volga Gambit", "eco": "A57", "moves": "d2d4 g8f6 c2c4 c7c5 d4d5 b7b5 c4b5 a7a6", "category": "Gambits"},
    {"name": "Smith-Morra Gambit", "eco": "B21", "moves": "e2e4 c7c5 d2d4 c5d4 c2c3", "category": "Gambits"},
    {"name": "Danish Gambit", "eco": "C21", "moves": "e2e4 e7e5 d2d4 e5d4 c2c3", "category": "Gambits"},
    {"name": "Latvian Gambit", "eco": "C40", "moves": "e2e4 e7e5 g1f3 f7f5", "category": "Gambits"},
]

def get_engine():
    if not os.path.exists(STOCKFISH_PATH):
        return None, f"Stockfish not found at {STOCKFISH_PATH}"
    try:
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        return engine, None
    except Exception as e:
        return None, str(e)

def score_to_str(score, turn):
    """Convert a PovScore to a display string."""
    if score.is_mate():
        mate_in = score.white().mate()
        if mate_in > 0:
            return f"+M{mate_in}"
        else:
            return f"-M{abs(mate_in)}"
    else:
        cp = score.white().score()
        return f"{'+' if cp >= 0 else ''}{cp/100:.2f}"

def score_to_cp(score):
    """Return centipawn value from white's perspective."""
    if score.is_mate():
        mate = score.white().mate()
        return 30000 if mate > 0 else -30000
    return score.white().score()

def generate_explanation(board, move, info, alt_moves):
    """Generate natural language explanation for the move."""
    parts = []
    piece = board.piece_at(move.from_square)
    piece_name = chess.piece_name(piece.piece_type).capitalize() if piece else "Piece"
    to_name = chess.square_name(move.to_square)
    from_name = chess.square_name(move.from_square)

    # Castling
    if board.is_castling(move):
        side = "kingside" if chess.square_file(move.to_square) > 4 else "queenside"
        parts.append(f"Castles {side}, securing the king and activating the rook.")
    else:
        # Capture
        if board.is_capture(move):
            captured = board.piece_at(move.to_square)
            cap_name = chess.piece_name(captured.piece_type) if captured else "piece"
            parts.append(f"Captures the {cap_name} on {to_name}, winning material.")
        else:
            parts.append(f"Moves the {piece_name} from {from_name} to {to_name}.")

    # Check after move
    board_copy = board.copy()
    board_copy.push(move)
    if board_copy.is_checkmate():
        parts.append("This delivers CHECKMATE!")
    elif board_copy.is_check():
        parts.append("This move gives check, forcing the opponent to respond.")

    # Promotion
    if move.promotion:
        prom_name = chess.piece_name(move.promotion).capitalize()
        parts.append(f"The pawn promotes to a {prom_name}.")

    # Development
    if piece and piece.piece_type in [chess.KNIGHT, chess.BISHOP]:
        rank = chess.square_rank(move.from_square)
        if (piece.color == chess.WHITE and rank == 0) or (piece.color == chess.BLACK and rank == 7):
            parts.append(f"Develops the {piece_name} from its starting square, increasing piece activity.")

    # Center control
    center = {chess.D4, chess.D5, chess.E4, chess.E5}
    if move.to_square in center:
        parts.append("Controls a key central square.")

    # Pawn push in center
    if piece and piece.piece_type == chess.PAWN and move.to_square in center:
        parts.append("This central pawn advance claims space and supports future piece activity.")

    # Score context
    score = info.get("score")
    if score:
        cp = score_to_cp(score)
        if abs(cp) >= 29000:
            pass  # Already mentioned mate
        elif cp > 200:
            parts.append(f"White has a significant advantage ({score_to_str(score, board.turn)}).")
        elif cp > 50:
            parts.append(f"White has a slight edge ({score_to_str(score, board.turn)}).")
        elif cp < -200:
            parts.append(f"Black has a significant advantage ({score_to_str(score, board.turn)}).")
        elif cp < -50:
            parts.append(f"Black has a slight edge ({score_to_str(score, board.turn)}).")
        else:
            parts.append(f"The position is roughly equal ({score_to_str(score, board.turn)}).")

    if not parts:
        parts.append("This improves piece coordination and prepares for upcoming play.")

    return " ".join(parts)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/openings")
def get_openings():
    return jsonify(OPENINGS)

@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.json
    fen = data.get("fen", chess.STARTING_FEN)
    depth = min(int(data.get("depth", 20)), 25)
    multipv = 3

    try:
        board = chess.Board(fen)
    except Exception as e:
        return jsonify({"error": f"Invalid FEN: {e}"}), 400

    if board.is_game_over():
        result = board.result()
        return jsonify({"game_over": True, "result": result})

    engine, err = get_engine()
    if not engine:
        return jsonify({"error": f"Engine not available: {err}. Please download Stockfish."}), 503

    try:
        infos = engine.analyse(board, chess.engine.Limit(depth=depth), multipv=multipv)
    except Exception as e:
        engine.quit()
        return jsonify({"error": str(e)}), 500

    engine.quit()

    moves_data = []
    for i, info in enumerate(infos):
        pv = info.get("pv", [])
        if not pv:
            continue
        best_move = pv[0]
        score = info.get("score")

        explanation = generate_explanation(board, best_move, info, [])

        # Build PV line (first 5 moves)
        pv_board = board.copy()
        pv_san = []
        for m in pv[:6]:
            try:
                pv_san.append(pv_board.san(m))
                pv_board.push(m)
            except Exception:
                break

        moves_data.append({
            "rank": i + 1,
            "uci": best_move.uci(),
            "from": chess.square_name(best_move.from_square),
            "to": chess.square_name(best_move.to_square),
            "san": board.san(best_move),
            "promotion": chess.piece_name(best_move.promotion) if best_move.promotion else None,
            "score_display": score_to_str(score, board.turn) if score else "0.00",
            "score_cp": score_to_cp(score) if score else 0,
            "is_mate": score.is_mate() if score else False,
            "mate_in": score.white().mate() if (score and score.is_mate()) else None,
            "explanation": explanation,
            "pv": pv_san,
            "depth": info.get("depth", depth),
        })

    if not moves_data:
        return jsonify({"error": "No moves found"}), 500

    return jsonify({
        "moves": moves_data,
        "fen": fen,
        "turn": "white" if board.turn == chess.WHITE else "black",
        "best_move": moves_data[0],
    })

@app.route("/api/make_move", methods=["POST"])
def make_move():
    data = request.json
    fen = data.get("fen", chess.STARTING_FEN)
    move_uci = data.get("move")

    try:
        board = chess.Board(fen)
        move = chess.Move.from_uci(move_uci)
        if move not in board.legal_moves:
            return jsonify({"error": "Illegal move"}), 400
        san = board.san(move)
        board.push(move)
        return jsonify({
            "fen": board.fen(),
            "san": san,
            "game_over": board.is_game_over(),
            "result": board.result() if board.is_game_over() else None,
            "in_check": board.is_check(),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/load_pgn", methods=["POST"])
def load_pgn():
    data = request.json
    pgn_text = data.get("pgn", "")
    try:
        game = chess.pgn.read_game(io.StringIO(pgn_text))
        if not game:
            return jsonify({"error": "Invalid PGN"}), 400
        board = game.end().board()
        moves = []
        node = game
        while node.variations:
            next_node = node.variations[0]
            moves.append(next_node.move.uci())
            node = next_node
        return jsonify({"fen": board.fen(), "moves": moves})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/validate_fen", methods=["POST"])
def validate_fen():
    data = request.json
    fen = data.get("fen", "")
    try:
        board = chess.Board(fen)
        return jsonify({"valid": True, "fen": board.fen()})
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 400

@app.route("/api/opening_from_moves", methods=["POST"])
def opening_from_moves():
    """Identify the opening from a sequence of moves."""
    data = request.json
    moves_uci = data.get("moves", [])
    moves_str = " ".join(moves_uci)

    best_match = None
    best_len = 0
    for op in OPENINGS:
        op_moves = op["moves"]
        if moves_str.startswith(op_moves) or op_moves.startswith(moves_str[:len(op_moves)]):
            if moves_str[:len(op_moves)] == op_moves:
                if len(op_moves) > best_len:
                    best_len = len(op_moves)
                    best_match = op

    return jsonify({"opening": best_match})

if __name__ == "__main__":
    print("=" * 60)
    print("Chess Beast - Advanced Chess Analysis Engine")
    print("=" * 60)
    if not os.path.exists(STOCKFISH_PATH):
        print(f"WARNING: Stockfish not found at {STOCKFISH_PATH}")
        print("Please run download_stockfish.py or place stockfish.exe in the stockfish/ folder")
    else:
        print(f"Stockfish found: {STOCKFISH_PATH}")
    print("Starting server at http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, port=5000)
