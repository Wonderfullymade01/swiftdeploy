import os, time, random, threading
from flask import Flask, request, jsonify, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)
START_TIME = time.time()

MODE = os.environ.get("MODE", "stable")
VERSION = os.environ.get("APP_VERSION", "1.0.0")
PORT = int(os.environ.get("APP_PORT", 3000))

# Chaos state
chaos_state = {"mode": None, "duration": 0, "rate": 0.0}
chaos_lock = threading.Lock()

# Prometheus metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"]
)
http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)
app_uptime_seconds = Gauge("app_uptime_seconds", "App uptime in seconds")
app_mode_gauge = Gauge("app_mode", "App mode: 0=stable, 1=canary")
chaos_active_gauge = Gauge("chaos_active", "Chaos state: 0=none, 1=slow, 2=error")

def update_gauges():
    app_uptime_seconds.set(time.time() - START_TIME)
    app_mode_gauge.set(1 if MODE == "canary" else 0)
    with chaos_lock:
        m = chaos_state["mode"]
        if m == "slow":
            chaos_active_gauge.set(1)
        elif m == "error":
            chaos_active_gauge.set(2)
        else:
            chaos_active_gauge.set(0)

def apply_chaos():
    with chaos_lock:
        m = chaos_state["mode"]
        if m == "slow":
            time.sleep(chaos_state["duration"])
        elif m == "error":
            if random.random() < chaos_state["rate"]:
                return jsonify({"error": "chaos error"}), 500
    return None

@app.before_request
def start_timer():
    request._start_time = time.time()

@app.after_request
def record_metrics(response):
    duration = time.time() - getattr(request, "_start_time", time.time())
    path = request.path
    method = request.method
    status = str(response.status_code)

    http_requests_total.labels(method=method, path=path, status_code=status).inc()
    http_request_duration_seconds.labels(method=method, path=path).observe(duration)

    response.headers["X-Deployed-By"] = "swiftdeploy"
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

@app.route("/metrics")
def metrics():
    update_gauges()
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

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