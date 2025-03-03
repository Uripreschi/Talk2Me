import os
import openai
import whisper
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Ensure OpenAI API Key is available
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("🚨 ERROR: Missing OPENAI_API_KEY. Add it to your environment variables.")

openai.api_key = OPENAI_API_KEY

# Initialize Flask app
app = Flask(__name__, template_folder="templates")
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ensure Uploads Directory Exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
db = SQLAlchemy(app)

# Ensure database tables are created
with app.app_context():
    db.create_all()

# Load Whisper Model (only once for performance)
model = whisper.load_model("base")

# Database Model
class StudentResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    correct_answer = db.Column(db.String(1000), nullable=False)
    student_response = db.Column(db.String(1000), nullable=True)
    score = db.Column(db.Float, nullable=True)

# Homepage - Display input form
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        question = request.form.get("question")
        correct_answer = request.form.get("correct_answer")

        if not question or not correct_answer:
            return jsonify({"error": "Both fields are required"}), 400

        entry = StudentResponse(question=question, correct_answer=correct_answer)
        db.session.add(entry)
        db.session.commit()

    return render_template("index.html", questions=StudentResponse.query.all())

# Upload & Transcribe Student's Audio
@app.route("/submit", methods=["POST"])
def submit():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    file = request.files["audio"]
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Transcribe audio
    result = model.transcribe(filepath)
    transcript = result["text"]

    # Retrieve latest question
    latest_question = StudentResponse.query.order_by(StudentResponse.id.desc()).first()
    if not latest_question:
        return jsonify({"error": "No questions available"}), 400

    # Grade response using GPT-4
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a strict but fair oral assessment grader."},
                {"role": "user", "content": f"Question: {latest_question.question}\nCorrect Answer: {latest_question.correct_answer}\nStudent Response: {transcript}\n\nGive a score from 0 to 100 and a short feedback note."}
            ]
        )
        score_feedback = response["choices"][0]["message"]["content"]
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Save response and score
    latest_question.student_response = transcript
    latest_question.score = float(score_feedback.split()[0])  # Extract score
    db.session.commit()

    return jsonify({"transcript": transcript, "score_feedback": score_feedback})

# Run App
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensures the database tables are created
    app.run(host="0.0.0.0", port=5000, debug=True)
