import os
from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from app.models.post import MessagePost
from app.extensions import messages_db as db

post_bp = Blueprint("post_bp", __name__)
UPLOAD_FOLDER = "static/uploads"
DEFAULT_IMAGE = "/static/default.jpg"

@post_bp.route("/posts", methods=["GET", "POST"])
def posts_page():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        body = request.form.get("body", "").strip()
        author = request.form.get("author", "").strip() or "Anonymous"

        file = request.files.get("image")
        if file and file.filename:
            filename = secure_filename(file.filename)
            path = os.path.join(UPLOAD_FOLDER, filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            file.save(path)
            image_path = "/" + path
        else:
            image_path = DEFAULT_IMAGE

        if body:
            post = MessagePost(title=title, body=body, author=author, image_path=image_path)
            db.session.add(post)
            db.session.commit()

        return redirect(url_for("post_bp.posts_page"))

    posts = MessagePost.query.order_by(MessagePost.timestamp.desc()).all()
    return render_template("posts.html", posts=posts)

@post_bp.route("/posts/delete/<int:post_id>")
@admin_required
def delete_post(post_id):
    post = MessagePost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("post_bp.posts_page"))
