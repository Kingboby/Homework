from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# Homework folder in Dropbox
homework_folder = os.path.expanduser("~/Dropbox/Homework")
os.makedirs(homework_folder, exist_ok=True)

def get_homework_list():
    """List all homework subjects"""
    return [f[:-4] for f in os.listdir(homework_folder) if f.endswith(".txt")]

def read_homework(subject):
    """Read homework file"""
    file_path = os.path.join(homework_folder, f"{subject}.txt")
    if not os.path.exists(file_path):
        return "", ""
    with open(file_path, "r") as f:
        lines = f.readlines()
    due = lines[0].replace("Due Date: ", "").strip() if len(lines) > 0 else ""
    details = lines[1].replace("Details: ", "").strip() if len(lines) > 1 else ""
    return due, details

def save_homework(subject, due, details):
    """Save homework"""
    with open(os.path.join(homework_folder, f"{subject}.txt"), "w") as f:
        f.write(f"Due Date: {due}\nDetails: {details}")

def delete_homework(subject):
    """Delete homework"""
    file_path = os.path.join(homework_folder, f"{subject}.txt")
    if os.path.exists(file_path):
        os.remove(file_path)

@app.route("/", methods=["GET", "POST"])
def index():
    subjects = ["-- New Subject --"] + get_homework_list()  # visible empty option

    selected = request.args.get("subject", "").strip()
    due_date = ""
    details = ""

    if request.method == "POST":
        subject = request.form.get("subject", "").strip()
        due = request.form.get("due_date", "").strip()
        details_text = request.form.get("details", "").strip()

        # Add or update homework
        if "add" in request.form and subject:
            save_homework(subject, due, details_text)
            return redirect(url_for("index", subject=subject))

        # Delete homework
        elif "delete" in request.form and subject:
            delete_homework(subject)
            return redirect(url_for("index"))

    # Load selected subject if exists
    if selected:
        due_date, details = read_homework(selected)

    return render_template(
        "index.html",
        subjects=subjects,
        selected=selected,
        due_date=due_date,
        details=details
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
