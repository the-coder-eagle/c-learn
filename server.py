"""
Flask API server for C Learn. All endpoints call services.py functions.
"""
import os
import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, request, jsonify, send_from_directory
from services import (
    load_modules, load_exercises, load_progress, save_progress,
    compile_and_run, judge,
)
from simulator import CSimulator, EXAMPLES

# Global simulator instance (one per session)
_simulator: CSimulator = None

app = Flask(__name__, static_folder="web", static_url_path="")


# ── Static files ───────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory("web", "index.html")


@app.route("/<path:path>")
def static_files(path):
    if os.path.exists(os.path.join("web", path)):
        return send_from_directory("web", path)
    return send_from_directory("web", "index.html")


# ── Content API ────────────────────────────────────────────
@app.route("/api/modules")
def api_modules():
    mods = load_modules()
    return jsonify([{
        "slug": m.slug, "title": m.title, "level": m.level,
        "order": m.order, "description": m.description,
        "content_md": m.content_md, "tags": m.tags,
    } for m in mods])


@app.route("/api/exercises")
def api_exercises():
    exs = load_exercises()
    progress = load_progress()
    return jsonify([{
        "id": e.id, "title": e.title, "difficulty": e.difficulty,
        "tags": e.tags, "description_md": e.description_md,
        "test_case_count": len(e.test_cases),
        "status": progress.get(e.id, {}).get("status", ""),
    } for e in exs])


@app.route("/api/exercise/<ex_id>")
def api_exercise(ex_id):
    exs = load_exercises()
    ex = next((e for e in exs if e.id == ex_id), None)
    if not ex:
        return jsonify({"error": "not found"}), 404
    progress = load_progress()
    p = progress.get(ex_id, {})
    return jsonify({
        "id": ex.id, "title": ex.title, "difficulty": ex.difficulty,
        "tags": ex.tags, "description_md": ex.description_md,
        "template_code": p.get("last_code", "") or ex.template_code,
        "hints": ex.hints,
        "test_case_count": len(ex.test_cases),
        "status": p.get("status", ""),
    })


# ── Progress API ───────────────────────────────────────────
@app.route("/api/progress")
def api_progress():
    progress = load_progress()
    exercises = load_exercises()
    solved = sum(1 for v in progress.values() if v.get("status") == "passed")
    return jsonify({
        "solved": solved,
        "total": len(exercises),
        "details": progress,
    })


# ── Compile & Run ──────────────────────────────────────────
@app.route("/api/run", methods=["POST"])
def api_run():
    data = request.get_json() or {}
    code = data.get("code", "")
    stdin = data.get("stdin", "")
    if not code.strip():
        return jsonify({"error": "No code provided"}), 400
    r = compile_and_run(code, stdin=stdin)
    return jsonify({
        "success": r.success,
        "stdout": r.stdout,
        "stderr": r.stderr,
        "compile_error": r.compile_error,
        "exit_code": r.exit_code,
        "wall_time_ms": r.wall_time_ms,
        "error_lines": r.error_lines,
    })


# ── Judge / Submit ─────────────────────────────────────────
@app.route("/api/submit", methods=["POST"])
def api_submit():
    data = request.get_json() or {}
    code = data.get("code", "")
    ex_id = data.get("exercise_id", "")
    if not code.strip():
        return jsonify({"error": "No code provided"}), 400

    exs = load_exercises()
    ex = next((e for e in exs if e.id == ex_id), None)
    if not ex:
        return jsonify({"error": "Exercise not found"}), 404

    r = judge(code, ex.test_cases)
    save_progress(ex_id, r.status, code)

    return jsonify({
        "status": r.status,
        "passed_count": r.passed_count,
        "total_count": r.total_count,
        "test_results": r.test_results,
        "compile_error": r.compile_error,
        "wall_time_ms": r.wall_time_ms,
    })


# ── Simulator API ──────────────────────────────────────────
@app.route("/api/sim/load", methods=["POST"])
def api_sim_load():
    """Load code into the simulator."""
    global _simulator
    data = request.get_json() or {}
    code = data.get("code", "")
    if not code.strip():
        return jsonify({"error": "No code"}), 400
    _simulator = CSimulator(code)
    return jsonify(_simulator._get_state())


@app.route("/api/sim/example/<name>")
def api_sim_example(name):
    """Load a built-in example."""
    global _simulator
    if name not in EXAMPLES:
        return jsonify({"error": "Example not found"}), 404
    ex = EXAMPLES[name]
    _simulator = CSimulator(ex["code"])
    return jsonify({**_simulator._get_state(), "title": ex["title"]})


@app.route("/api/sim/examples")
def api_sim_examples():
    """List available examples."""
    return jsonify([
        {"id": k, "title": v["title"],
         "code_preview": v["code"][:80] + "..."}
        for k, v in EXAMPLES.items()
    ])


@app.route("/api/sim/step", methods=["POST"])
def api_sim_step():
    """Execute one step forward."""
    global _simulator
    if not _simulator:
        return jsonify({"error": "No code loaded"}), 400
    return jsonify(_simulator.step())


@app.route("/api/sim/back", methods=["POST"])
def api_sim_back():
    """Step back one step."""
    global _simulator
    if not _simulator:
        return jsonify({"error": "No code loaded"}), 400
    return jsonify(_simulator.step_back())


@app.route("/api/sim/reset", methods=["POST"])
def api_sim_reset():
    """Reset the simulator."""
    global _simulator
    if not _simulator:
        return jsonify({"error": "No code loaded"}), 400
    _simulator.reset()
    return jsonify(_simulator._get_state())


@app.route("/api/sim/run", methods=["POST"])
def api_sim_run_all():
    """Run to completion."""
    global _simulator
    if not _simulator:
        return jsonify({"error": "No code loaded"}), 400
    state = _simulator.run_all()
    return jsonify(state)


@app.route("/api/sim/state")
def api_sim_state():
    """Get current simulator state."""
    global _simulator
    if not _simulator:
        return jsonify({"error": "No code loaded"}), 400
    return jsonify(_simulator._get_state())


# ── Health ─────────────────────────────────────────────────
@app.route("/api/health")
def api_health():
    return jsonify({"status": "ok"})


def start_server(port=8765):
    """Start Flask in a daemon thread. Returns the URL."""
    import threading
    t = threading.Thread(
        target=lambda: app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False),
        daemon=True)
    t.start()
    return f"http://127.0.0.1:{port}"
