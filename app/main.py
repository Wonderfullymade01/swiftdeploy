import os, time, random, threading
from flask import Flask, request, jsonify

app = Flask(__name__)
START_TIME = time.time()

MODE = os.environ.get("MODE", "stable")
VERSION = os.environ.get("APP_VERSION", "1.0.0")
PORT = int(os.environ.get("APP_PORT", 3000))

# Chaos state
chaos_state = {"mode": None, "duration": 0, "rate": 0.0}
chaos_lock = threading.Lock()

def apply_chaos():
    with chaos_lock:
        m = chaos_state["mode"]
        if m == "slow":
            time.sleep(chaos_state["duration"])
        elif m == "error":
            if random.random() < chaos_state["rate"]:
                return jsonify({"error": "chaos error"}), 500
    return None

@app.after_request
def add_headers(response):
    if MODE == "canary":
        response.headers["X-Mode"] = "canary"
    return response

@app.route("/")
def index():
    chaos = apply_chaos()
    if chaos:
        return chaos
    return jsonify({
        "message": f"Welcome! Running in {MODE} mode",
        "mode": MODE,
        "version": VERSION,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    })

@app.route("/healthz")
def healthz():
    return jsonify({
        "status": "ok",
        "uptime_seconds": round(time.time() - START_TIME, 2)
    })

@app.route("/chaos", methods=["POST"])
def chaos_endpoint():
    if MODE != "canary":
        return jsonify({"error": "chaos only available in canary mode"}), 403
    data = request.get_json()
    with chaos_lock:
        if data.get("mode") == "recover":
            chaos_state["mode"] = None
        else:
            chaos_state.update(data)
    return jsonify({"status": "chaos applied", "state": chaos_state})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)