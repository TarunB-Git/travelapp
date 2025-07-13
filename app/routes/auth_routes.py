from flask import Blueprint, render_template, request, redirect, url_for, session
from app.models.credentials import AdminCredentials
from app.extensions import db

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        entered = request.form.get("password", "")
        creds = AdminCredentials.get()
        if creds and creds.check_access_password(entered):
            session["access_granted"] = True
            return redirect(url_for("views_bp.home"))
        return render_template("login.html", error="Invalid access password")
    return render_template("login.html")

@auth_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        entered = request.form.get("admin_password", "")
        creds = AdminCredentials.get()
        if creds and creds.check_admin_password(entered):
            session["admin"] = True
            return redirect(url_for("views_bp.home"))
        return render_template("admin_login.html", error="Invalid admin password")
    return render_template("admin_login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth_bp.login"))

@auth_bp.route("/admin/reset", methods=["GET", "POST"])
def reset_passwords():
    if not session.get("admin"):
        return redirect(url_for("auth_bp.admin_login"))

    creds = AdminCredentials.get()
    if request.method == "POST":
        if "new_access_password" in request.form:
            creds.set_access_password(request.form["new_access_password"])
        if "new_admin_password" in request.form:
            creds.set_admin_password(request.form["new_admin_password"])
        db.session.commit()
        return redirect(url_for("views_bp.home"))
    return render_template("reset_passwords.html")
