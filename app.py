from flask import Flask, render_template, jsonify, request
import json
import os

app = Flask(__name__)
DATA_FILE = "data/companies.json"


def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/companies")
def api_companies():
    companies = load_data()
    q = request.args.get("q", "").lower()
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))

    if q:
        companies = [
            c for c in companies
            if q in c["name"].lower()
            or q in c["description"].lower()
            or q in c["address"].lower()
        ]

    total = len(companies)
    start = (page - 1) * per_page
    end = start + per_page

    return jsonify({
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
        "companies": companies[start:end],
    })


@app.route("/api/stats")
def api_stats():
    companies = load_data()
    return jsonify({
        "total": len(companies),
        "with_website": sum(1 for c in companies if c["website"]),
        "with_address": sum(1 for c in companies if c["address"]),
        "with_logo": sum(1 for c in companies if c["logo"]),
    })


if __name__ == "__main__":
    app.run(debug=True, port=5001)
