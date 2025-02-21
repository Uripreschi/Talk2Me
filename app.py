import os
import openai
import whisper
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, template_folder="templates")
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ensure Uploads Directory Exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
db = SQLAlchemy(app)

# Load OpenAI Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load Whisper model **only once** (Optimization)
model = whisper.load_model("base")

# Database Model
class StudentResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    correct_answer = db.Column(db.String(1000), nullable=False)
    student_response = db.Column(db.String(1000), nullable=True)
    score = db.Column(db.Float, nullable=True)
    grading_strictness = db.Column(db.String(50), nullable=False, default="normal")

# Homepage for teachers to input questions
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        question = request.form.get("question")
        correct_answer = request.form.get("correct_answer")
        grading_strictness = request.form.get("grading_strictness", "normal")

        if not question or not correct_answer:
            return jsonify({"error": "Both fields are required"}), 400

        entry = StudentResponse(question=question, correct_answer=correct_answer, grading_strictness=grading_strictness)
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

    # Define grading strictness in the AI prompt
    grading_levels = {
        "lenient": "Be very forgiving in grading.",
        "normal": "Grade fairly and logically.",
        "strict": "Be very harsh in grading."
    }
    strictness_level = grading_levels.get(latest_question.grading_strictness, "normal")

    # Grade response using GPT-4
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"You are an AI grader. {strictness_level}"},
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

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure the database is initialized
    app.run(debug=True)
