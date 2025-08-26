from __future__ import annotations

import random
import sqlite3
from pathlib import Path
from typing import Dict, List

from flask import Flask, render_template, request, redirect, url_for, g

app = Flask(__name__)

DATABASE = Path("cases.db")


def get_db() -> sqlite3.Connection:
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
    return db


@app.teardown_appcontext
def close_connection(exception) -> None:
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db() -> None:
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS skins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            chance REAL NOT NULL,
            FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
        );
        """
    )
    db.commit()


def fetch_cases() -> List[Dict]:
    db = get_db()
    cases = []
    for case in db.execute("SELECT id, name, price FROM cases").fetchall():
        skins = db.execute(
            "SELECT id, name, chance FROM skins WHERE case_id = ?", (case["id"],)
        ).fetchall()
        cases.append(
            {
                "id": case["id"],
                "name": case["name"],
                "price": case["price"],
                "skins": [dict(s) for s in skins],
            }
        )
    return cases


def get_case(case_id: int) -> Dict | None:
    db = get_db()
    case = db.execute(
        "SELECT id, name, price FROM cases WHERE id = ?", (case_id,)
    ).fetchone()
    if case is None:
        return None
    skins = db.execute(
        "SELECT id, name, chance FROM skins WHERE case_id = ?", (case_id,)
    ).fetchall()
    return {
        "id": case["id"],
        "name": case["name"],
        "price": case["price"],
        "skins": [dict(s) for s in skins],
    }


def create_case(name: str, price: float, skins: List[Dict]) -> None:
    db = get_db()
    cur = db.execute("INSERT INTO cases (name, price) VALUES (?, ?)", (name, price))
    case_id = cur.lastrowid
    for skin in skins:
        db.execute(
            "INSERT INTO skins (case_id, name, chance) VALUES (?, ?, ?)",
            (case_id, skin["name"], skin["chance"]),
        )
    db.commit()


def update_case(case_id: int, name: str, price: float, skins: List[Dict]) -> None:
    db = get_db()
    db.execute("UPDATE cases SET name = ?, price = ? WHERE id = ?", (name, price, case_id))
    db.execute("DELETE FROM skins WHERE case_id = ?", (case_id,))
    for skin in skins:
        db.execute(
            "INSERT INTO skins (case_id, name, chance) VALUES (?, ?, ?)",
            (case_id, skin["name"], skin["chance"]),
        )
    db.commit()


def remove_case(case_id: int) -> None:
    db = get_db()
    db.execute("DELETE FROM cases WHERE id = ?", (case_id,))
    db.commit()


@app.before_first_request
def initialize() -> None:
    init_db()


@app.route("/")
def index():
    cases = fetch_cases()
    return render_template("index.html", cases=cases)


@app.route("/open/<int:case_id>", methods=["POST"])
def open_case(case_id: int):
    case = get_case(case_id)
    if case is None:
        return redirect(url_for("index"))
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


@app.route("/admin")
def admin():
    cases = fetch_cases()
    return render_template("admin.html", cases=cases)


def parse_skins(skins_raw: str) -> List[Dict]:
    skins: List[Dict] = []
    for line in skins_raw.splitlines():
        if not line.strip():
            continue
        try:
            skin_name, chance = line.split(":")
            skins.append({"name": skin_name.strip(), "chance": float(chance)})
        except ValueError:
            continue
    return skins


@app.route("/admin/new", methods=["GET", "POST"])
def new_case():
    if request.method == "POST":
        name = request.form.get("name", "Untitled Case")
        price = float(request.form.get("price", 0))
        skins = parse_skins(request.form.get("skins", ""))
        create_case(name, price, skins)
        return redirect(url_for("admin"))
    return render_template("case_form.html", case=None)


@app.route("/admin/<int:case_id>/edit", methods=["GET", "POST"])
def edit_case(case_id: int):
    case = get_case(case_id)
    if case is None:
        return redirect(url_for("admin"))
    if request.method == "POST":
        name = request.form.get("name", case["name"])
        price = float(request.form.get("price", case["price"]))
        skins = parse_skins(request.form.get("skins", ""))
        update_case(case_id, name, price, skins)
        return redirect(url_for("admin"))
    return render_template("case_form.html", case=case)


@app.route("/admin/<int:case_id>/delete", methods=["POST"])
def delete_case(case_id: int):
    remove_case(case_id)
    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(debug=True)
