# app.py
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import datetime

app = Flask(__name__)

# Use DATABASE_URL (Railway) if present; otherwise use local sqlite for testing
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
else:
    # Local fallback (makes it easy to develop without a remote DB)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///homework.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# --- Models ---
class Homework(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200), nullable=False, unique=True)
    due_date = db.Column(db.Date, nullable=True)   # store as Date
    details = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "subject": self.subject,
            "due_date": self.due_date.isoformat() if self.due_date else "",
            "details": self.details or ""
        }

# Create tables automatically on startup (simple approach)
with app.app_context():
    db.create_all()

# --- Helpers to parse date inputs ---
def parse_date_input(value):
    """
    Accept either YYYY-MM-DD or DD/MM/YYYY (in case the frontend sometimes provides that).
    Returns a datetime.date or None.
    """
    if not value:
        return None
    value = value.strip()
    # try ISO first
    try:
        return datetime.date.fromisoformat(value)
    except Exception:
        pass
    # try DD/MM/YYYY
    try:
        parts = value.split('/')
        if len(parts) == 3:
            d, m, y = parts
            return datetime.date(int(y), int(m), int(d))
    except Exception:
        pass
    return None

def format_date_for_input(date_obj):
    """Return YYYY-MM-DD for input[type=date] value (or empty)."""
    if not date_obj:
        return ""
    return date_obj.isoformat()

# --- Routes ---
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        subject = (request.form.get("subject") or "").strip()
        due_in = (request.form.get("due_date") or "").strip()
        details = (request.form.get("details") or "").strip()

        # if adding/updating
        if "add" in request.form and subject:
            due_date = parse_date_input(due_in)
            hw = Homework.query.filter_by(subject=subject).first()
            if hw:
                # update
                hw.due_date = due_date
                hw.details = details
            else:
                hw = Homework(subject=subject, due_date=due_date, details=details)
                db.session.add(hw)
            db.session.commit()
            return redirect(url_for("index", subject=subject))

        # delete
        if "delete" in request.form and subject:
            Homework.query.filter_by(subject=subject).delete()
            db.session.commit()
            return redirect(url_for("index"))

    # GET: read selected subject query param
    selected = (request.args.get("subject") or "").strip()
    # list all subjects (alphabetical)
    subjects = [h.subject for h in Homework.query.order_by(Homework.subject).all()]
    selected_due = ""
    selected_details = ""
    if selected:
        hw = Homework.query.filter_by(subject=selected).first()
        if hw:
            selected_due = format_date_for_input(hw.due_date)  # YYYY-MM-DD -> safe for input[type=date]
            selected_details = hw.details or ""
    return render_template("index.html",
                           subjects=subjects,
                           selected=selected,
                           due_date=selected_due,
                           details=selected_details)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
