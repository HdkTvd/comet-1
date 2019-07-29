import os
from flask import Flask, flash, url_for, render_template, request
from werkzeug.utils import secure_filename, redirect

Upload_folder = "C:\\Users\\Shlok\\Desktop"
allowed_extensions = {'pdf', 'jpeg', 'jpg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = Upload_folder
app.config['SECRET_KEY'] = 'any secret string'


def allowed_file(file_name):
    if file_name.rsplit('.', 1)[1] in allowed_extensions:
        return True


@app.route("/admin/home/notes", methods=['POST'])
def file_uploader():  # uploads doc when clicked Submit button
    if request.method == 'POST':
        f = request.files["file"]
        if allowed_file(f.filename):
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            flash("File Uploaded!")
            return render_template("notes_uploader.html", title='Notes', status='admin', login=True)


@app.route("/admin/home/notes")
def admin_notes():
    return render_template("notes_up.html", title='Notes', status='admin', login=True)


@app.route("/")
def landing():
    return render_template("landing.html", title='Home', status='student', login=False)


@app.route("/admin")
def admin_login():
    return render_template("admin_login.html", title='Admin', status='admin', login=False)


@app.route("/admin/home", methods=["POST"])
def admin_home():
    username = request.form.get("username")
    password = request.form.get("password")
    if username == "admin" and password == "admin":
        return render_template("admin_home.html", title='Admin', status='admin', login=True)
    else:
        return "Invalid credentials"


@app.route("/logout", methods=["POST"])
def logout():
    token = request.form.get()
    # tokenizer.revoke_token(token)
    return redirect("/")


@app.route("/home")
def home():
    return render_template("home.html", title="Home", status='student', login=True)


if __name__ == '__main__':
    app.run()
