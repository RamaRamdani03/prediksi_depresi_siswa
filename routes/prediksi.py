from flask import Blueprint, render_template
import mysql.connector
import joblib
import pandas as pd
from datetime import datetime

prediksi_bp = Blueprint('prediksi', __name__)

# KONEKSI DATABASE
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="prediksi_depresi",
    autocommit=True
)

# LOAD MODEL
model = joblib.load("model/model_prediksi_depresi.pkl")


@prediksi_bp.route('/prediksi')
def halaman_prediksi():

    cursor = db.cursor()

    # AMBIL DATA
    cursor.execute("""
    SELECT
        s.id_siswa,
        s.nama,
        s.gender,
        s.umur,
        k.academic_pressure,
        k.sleep_duration,
        k.financial_stress,
        k.suicidal_thoughts,
        k.dietary_habits,
        k.study_satisfaction,
        k.work_study_hours
    FROM kuesioner k
    JOIN siswa s ON k.id_siswa = s.id_siswa
    """)

    data = cursor.fetchall()

    columns = [
        'id', 'nama', 'gender', 'age',
        'academic_pressure', 'sleep_duration',
        'financial_stress', 'suicidal_thoughts',
        'dietary_habits', 'study_satisfaction',
        'work_study_hours'
    ]

    df = pd.DataFrame(data, columns=columns)

    hasil = []

    # HAPUS DATA LAMA
    cursor.execute("DELETE FROM hasil_prediksi")

    # FIX: ENCODING GENDER
    gender_map = {
        'L': 0,
        'P': 1
    }

    # LOOP PREDIKSI
    for _, row in df.iterrows():

        fitur = pd.DataFrame([{
            'id': row['id'],
            'Gender': gender_map.get(row['gender'], 0),  # 🔥 FIX DI SINI
            'Age': row['age'],
            'Academic Pressure': row['academic_pressure'],
            'Sleep Duration': row['sleep_duration'],
            'Financial Stress': row['financial_stress'],
            'Have you ever had suicidal thoughts ?': row['suicidal_thoughts'],
            'Dietary Habits': row['dietary_habits'],
            'Study Satisfaction': row['study_satisfaction'],
            'Work/Study Hours': row['work_study_hours']
        }])

        # URUTAN HARUS SAMA DENGAN MODEL
        fitur = fitur[[
            'id',
            'Gender',
            'Age',
            'Academic Pressure',
            'Sleep Duration',
            'Financial Stress',
            'Have you ever had suicidal thoughts ?',
            'Dietary Habits',
            'Study Satisfaction',
            'Work/Study Hours'
        ]]

        # PREDIKSI
        pred = model.predict(fitur)[0]
        prob = model.predict_proba(fitur)[0]

        probabilitas = round(max(prob) * 100, 2)
        label = "Depresi" if pred == 1 else "Tidak Depresi"

        tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # SIMPAN KE DATABASE
        cursor.execute("""
        INSERT INTO hasil_prediksi
        (id_siswa, hasil, probabilitas, tanggal)
        VALUES (%s,%s,%s,%s)
        """, (row['id'], label, probabilitas, tanggal))

        hasil.append((row['nama'], label, probabilitas, tanggal))

    cursor.close()

    return render_template("prediksi/index.html", data=hasil)