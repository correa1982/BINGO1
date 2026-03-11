# app.py
import random
from uuid import uuid4
from flask import Flask, render_template, jsonify, session, request

app = Flask(__name__)
app.secret_key = "cambia-esta-clave"  # cámbiala en producción

# Estado por sesión de navegador
GAME_STORE = {}

def get_sid():
    if "sid" not in session:
        session["sid"] = str(uuid4())
    return session["sid"]

def letra_de_bola(num: int) -> str:
    if 1 <= num <= 15:  return "B"
    if 16 <= num <= 30: return "I"
    if 31 <= num <= 45: return "N"
    if 46 <= num <= 60: return "G"
    return "O"

def estado_inicial():
    return {
        "remaining": list(range(1, 76)),  # 1..75
        "history": [],
        "last": None
    }

def estado_publico(state):
    return {
        "remaining_count": len(state["remaining"]),
        "history": [int(n) for n in state["history"]],
        "last": state["last"],
        "last_label": (f"{letra_de_bola(state['last'])}-{state['last']}" if state["last"] else None)
    }

@app.before_request
def preparar_sesion():
    get_sid()
    sid = session["sid"]
    if sid not in GAME_STORE:
        GAME_STORE[sid] = estado_inicial()

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/state", methods=["GET"])
def state():
    sid = session["sid"]
    return jsonify(estado_publico(GAME_STORE[sid]))

@app.route("/draw", methods=["POST"])
def draw():
    sid = session["sid"]
    st = GAME_STORE[sid]
    if not st["remaining"]:
        return jsonify({"error": "No quedan bolas por extraer."}), 400

    bola = random.choice(st["remaining"])
    st["remaining"].remove(bola)
    st["history"].append(bola)
    st["last"] = bola

    return jsonify({
        "ball": {"number": bola, "letter": letra_de_bola(bola), "label": f"{letra_de_bola(bola)}-{bola}"},
        "state": estado_publico(st)
    })

@app.route("/reset", methods=["POST"])
def reset():
    sid = session["sid"]
    GAME_STORE[sid] = estado_inicial()
    return jsonify({"ok": True, "state": estado_publico(GAME_STORE[sid])})

# (Opcional) Fijar semilla para repetir el orden de bolas
@app.route("/seed", methods=["POST"])
def seed():
    data = request.get_json(force=True, silent=True) or {}
    val = str(data.get("seed", "")).strip()
    if not val:
        return jsonify({"error": "Falta 'seed'."}), 400
    random.seed(val)
    return jsonify({"ok": True})

if __name__ == "__main__":
    # Ejecuta: python app.py
    app.run(host="0.0.0.0", port=5003, debug=True)