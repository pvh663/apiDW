from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os

app = Flask(__name__)

# MySQL Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:phamvanha@localhost:3306/thanglong88'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the Database
db = SQLAlchemy(app)

# Define the StudentScores model
class StudentScore(db.Model):
    __tablename__ = 'student_course_scores'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    studentID = db.Column(db.String(20), nullable=False)
    student_name= db.Column(db.String(50), nullable=False)
    courseID = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    classID = db.Column(db.String(20), nullable=False)
    course_name= db.Column(db.String(80), nullable=False)
    score = db.Column(db.Float, nullable=False)
    coefficient =db.Column(db.Integer,nullable=True)
    ex_location= db.Column(db.String(20),nullable=True)
    semester =db.Column(db.String(20), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/upload', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        df = pd.read_csv(file)

        for _, row in df.iterrows():
            new_score = StudentScore(

                studentID = row['studentID'],
                student_name = row['student_name'],
                courseID = row['courseID'],
                status=  row['status'],
                classID = row['classID'],
                course_name = row['course_name'],
                score = row['score'],
                coefficient =row['coefficient'],
                ex_location= row['ex_location'],
                semester = row['semester']
            )
            db.session.add(new_score)

        db.session.commit()

        return jsonify({"message": "File uploaded and data stored successfully!"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/check-db', methods=['GET'])
def check_db_connection():
    try:
        # Use text() for raw SQL queries (SQLAlchemy 2.x requirement)
        db.session.execute(text('SELECT 1'))
        return jsonify({"status": "success", "message": "Connected to MySQL on port 3307 successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route('/get-all', methods=['GET'])
def get_all_data():
    try:
        records = StudentScore.query.all()
        result = [
            {
                "status":record.status,
                "classID":record.classID,
                "course_name":record.course_name,
                "id": record.id,
                "studentID": record.studentID,
                "courseID": record.courseID,
                "score": record.score,
                "coefficient":record.coefficient,
                "ex_location":record.ex_location,
                "semester":record.semester,
            }
            for record in records
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/score/<semester>', methods=['GET'])
def get_scores_by_semester(semester):
    try:
        records = StudentScore.query.filter_by(semester=semester).all()
        result = [
            {
                "status": record.status,
                "classID": record.classID,
                "course_name": record.course_name,
                "id": record.id,
                "studentID": record.studentID,
                "courseID": record.courseID,
                "score": record.score,
                "coefficient": record.coefficient,
                "ex_location": record.ex_location,
                "semester": record.semester
            }
            for record in records
        ]
        return jsonify({"semester": semester, "data": {"student_course_score": result}})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
