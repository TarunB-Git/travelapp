from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.person import Person

person_bp = Blueprint("person_bp", __name__, url_prefix="/api/people")


@person_bp.route("", methods=["GET"])
def list_people():
    people = Person.query.all()
    return jsonify([{"id": p.id, "name": p.name} for p in people]), 200

@person_bp.route("/add", methods=["POST"])
def add_person():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400
    if Person.query.filter_by(name=name).first():
        return jsonify({"error": "person already exists"}), 400

    new = Person(name=name)
    db.session.add(new)
    db.session.commit()

    return jsonify({"id": new.id, "name": new.name}), 201

