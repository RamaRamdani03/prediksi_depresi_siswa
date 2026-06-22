from flask import Blueprint, render_template
import mysql.connector
import pandas as pd
from datetime import datetime
import pickle

prediksi_bp = Blueprint('prediksi', __name__)

# =========================
# KONEKSI DATABASE
# =========================
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="prediksi_depresi",
    autocommit=True
)

# =========================
# LOAD MODEL
# =========================
with open("model/model_simple.pkl", "rb") as f:
    model = pickle.load(f)

with open("model/threshold_simple.pkl", "rb") as f:
    threshold = pickle.load(f)

with open("model/encoder_maps.pkl", "rb") as f:
    encoder_maps = pickle.load(f)

# =========================
# CLEAN FUNCTION
# =========================
def clean(val):
    if isinstance(val, str):
        return val.strip()
    return val

# =========================
# ENCODING FUNCTION
# =========================
def encode_row(row):

    return {

        'Gender':
        encoder_maps['Gender']
        .get(clean(row['gender']), 0),

        'Age':
        row['age'],

        'Academic Pressure':
        int(row['academic_pressure']),

        'Sleep Duration':
        encoder_maps['Sleep Duration']
        .get(clean(row['sleep_duration']), 0),

        'Financial Stress':
        int(row['financial_stress']),

        'Family History of Mental Illness':
        encoder_maps['Family History of Mental Illness']
        .get(clean(row['family_history']), 0),

        'Have you ever had suicidal thoughts ?':
        encoder_maps['Have you ever had suicidal thoughts ?']
        .get(clean(row['suicidal_thoughts']), 0),

        'Dietary Habits':
        encoder_maps['Dietary Habits']
        .get(clean(row['dietary_habits']), 0),

        'Study Satisfaction':
        int(row['study_satisfaction']),

        'Work/Study Hours':
        int(row['work_study_hours'])
    }

# =========================
# ROUTE PREDIKSI
# =========================
@prediksi_bp.route('/prediksi')
def halaman_prediksi():

    cursor = db.cursor()

    # =========================
    # AMBIL DATA
    # =========================
    cursor.execute("""
    SELECT
        s.id_siswa,
        s.nama,
        s.gender,
        s.umur,

        k.academic_pressure,
        k.sleep_duration,
        k.financial_stress,
        k.family_history,
        k.suicidal_thoughts,
        k.dietary_habits,
        k.study_satisfaction,
        k.work_study_hours

    FROM kuesioner k
    JOIN siswa s
    ON k.id_siswa = s.id_siswa

    ORDER BY k.id_kuesioner DESC
    """)

    data = cursor.fetchall()

    columns = [

        'id',
        'nama',
        'gender',
        'age',

        'academic_pressure',
        'sleep_duration',
        'financial_stress',
        'family_history',
        'suicidal_thoughts',
        'dietary_habits',
        'study_satisfaction',
        'work_study_hours'
    ]

    df = pd.DataFrame(data, columns=columns)

    # =========================
    # JIKA KOSONG
    # =========================
    if df.empty:
        return render_template(
            "prediksi/index.html",
            data=[],
            threshold=round(threshold, 2)
        )

    hasil = []

    # =========================
    # HAPUS HASIL LAMA
    # =========================
    cursor.execute("DELETE FROM hasil_prediksi")

    # =========================
    # LOOP PREDIKSI
    # =========================
    for _, row in df.iterrows():

        fitur = pd.DataFrame([encode_row(row)])

        fitur = fitur[[

            'Gender',
            'Age',
            'Academic Pressure',
            'Sleep Duration',
            'Financial Stress',
            'Family History of Mental Illness',
            'Have you ever had suicidal thoughts ?',
            'Dietary Habits',
            'Study Satisfaction',
            'Work/Study Hours'
        ]]

        # =========================
        # PREDIKSI
        # =========================
        proba = model.predict_proba(fitur)[0][1]

        pred = 1 if proba >= threshold else 0

        probabilitas = round(proba * 100, 2)

        label = "Depresi" if pred == 1 else "Tidak Depresi"

        tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # =========================
        # SIMPAN DATABASE
        # =========================
        cursor.execute("""
        INSERT INTO hasil_prediksi
        (id_siswa, hasil, probabilitas, tanggal)
        VALUES (%s,%s,%s,%s)
        """, (
            row['id'],
            label,
            probabilitas,
            tanggal
        ))

        hasil.append((
            row['nama'],
            label,
            probabilitas,
            tanggal
        ))

    cursor.close()

    return render_template(
        "prediksi/index.html",
        data=hasil,
        threshold=round(threshold, 2)
    )