from flask import Blueprint, render_template
import mysql.connector
import joblib
import pandas as pd
from datetime import datetime

prediksi_bp = Blueprint('prediksi', __name__)

# koneksi database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="prediksi_depresi",
    autocommit=True
)

# load model
model = joblib.load("model/model_depresi.pkl")


@prediksi_bp.route('/prediksi')
def halaman_prediksi():

    cursor = db.cursor()

    # ambil data siswa + kuesioner
    cursor.execute("""
    SELECT
        s.id_siswa,
        s.nama,
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

    hasil = []

    # hapus hasil lama agar tidak duplicate
    cursor.execute("DELETE FROM hasil_prediksi")

    for d in data:

        fitur = pd.DataFrame([{
            'Have you ever had suicidal thoughts ?': d[6],
            'Academic Pressure': d[3],
            'Financial Stress': d[5],
            'Age': d[2],
            'Work/Study Hours': d[9],
            'Dietary Habits': d[7],
            'Study Satisfaction': d[8],
            'Sleep Duration': d[4]
        }])

        # prediksi model
        pred = model.predict(fitur)[0]
        prob = model.predict_proba(fitur)[0]

        probabilitas = round(max(prob) * 100, 2)

        if pred == 1:
            label = "Depresi"
        else:
            label = "Tidak Depresi"

        tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # simpan ke database
        cursor.execute("""
        INSERT INTO hasil_prediksi
        (id_siswa, hasil, probabilitas, tanggal)
        VALUES (%s,%s,%s,%s)
        """,(d[0], label, probabilitas, tanggal))

        # simpan untuk ditampilkan
        hasil.append((d[1], label, probabilitas, tanggal))

    cursor.close()

    return render_template("prediksi/index.html", data=hasil)