from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Dict, List

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DATA_FILE = Path("cases.json")


def load_cases() -> List[Dict]:
    if DATA_FILE.exists():
        with DATA_FILE.open() as f:
            return json.load(f)
    return []


def save_cases(cases: List[Dict]) -> None:
    with DATA_FILE.open("w") as f:
        json.dump(cases, f, indent=2)


@app.route("/")
def index():
    cases = load_cases()
    return render_template("index.html", cases=cases)


@app.route("/open/<int:case_id>", methods=["POST"])
def open_case(case_id: int):
    cases = load_cases()
    case = cases[case_id]
    skins = case["skins"]
    rnd = random.random()
    cumulative = 0.0
    result = None
    for skin in skins:
        cumulative += skin["chance"]
        if rnd <= cumulative:
            result = skin
            break
    return render_template("result.html", case=case, skin=result)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    cases = load_cases()
    if request.method == "POST":
        name = request.form.get("name", "Untitled Case")
        price = float(request.form.get("price", 0))
        skins: List[Dict] = []
        skins_raw = request.form.get("skins", "")
        for line in skins_raw.splitlines():
            if not line.strip():
                continue
            try:
                skin_name, chance = line.split(":")
                skins.append({"name": skin_name.strip(), "chance": float(chance)})
            except ValueError:
                continue
        cases.append({"name": name, "price": price, "skins": skins})
        save_cases(cases)
        return redirect(url_for("admin"))
    return render_template("admin.html", cases=cases)


if __name__ == "__main__":
    app.run(debug=True)
