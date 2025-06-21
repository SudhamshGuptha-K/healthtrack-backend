from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from healthtrack_core import analyze_report, export_to_pdf

import os





app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def home():
    return "✅ HealthTrack AI Flask backend is running!"

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        report_text = data.get("report", "")
        print("🔍 Report received:\n", report_text)

        results = analyze_report(report_text)
        export_to_pdf(results)

        print("✅ Analysis complete. Returning results.")
        return jsonify(results)
    except Exception as e:
        print("❌ Error occurred:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/download", methods=["GET"])
def download():
    try:
        return send_file("healthtrack_report.pdf", as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "PDF not found. Run /analyze first."}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

