import csv
from flask import Flask, request, jsonify, send_file
from engine import analyze, clean
from explain import highlight

app = Flask(__name__)


@app.get("/")
def home():
    return send_file("index.html")


@app.post("/check")
def check():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    if not text.strip():
        return jsonify({"error": "Send JSON like {\"text\": \"message\"}"}), 400
    result = analyze(text)
    result["highlight"] = highlight(clean(text))
    return jsonify(result)


@app.post("/report")
def report():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()
    if text:
        with open("reported.csv", "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([text, 1])
    return jsonify({"saved": bool(text)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)