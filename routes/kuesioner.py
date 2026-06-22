from flask import Blueprint, render_template, request, redirect
import mysql.connector

kuesioner_bp = Blueprint('kuesioner', __name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="prediksi_depresi",
    autocommit=True
)
    
# =========================
# CLEAN FUNCTION
# =========================
def clean(val):
    if isinstance(val, str):
        return val.strip()
    return val

# =========================
# READ DATA
# =========================
@kuesioner_bp.route('/kuesioner')
def index():
    cursor = db.cursor()

    cursor.execute("""
    SELECT
        k.id_kuesioner,
        s.nama,
        k.academic_pressure,
        k.sleep_duration,
        k.financial_stress,
        k.family_history,
        k.suicidal_thoughts,
        k.dietary_habits,
        k.study_satisfaction,
        k.work_study_hours
    FROM kuesioner k
    JOIN siswa s ON k.id_siswa = s.id_siswa
    ORDER BY k.id_kuesioner DESC
    """)

    data = cursor.fetchall()
    cursor.close()

    return render_template("kuesioner/index.html", data=data)

# =========================
# TAMBAH
# =========================
@kuesioner_bp.route('/kuesioner/tambah', methods=['GET', 'POST'])
def tambah():
    cursor = db.cursor()

    cursor.execute("""
    SELECT id_siswa, nama
    FROM siswa
    WHERE id_siswa NOT IN (
        SELECT id_siswa FROM kuesioner
    )
    """)    
    siswa = cursor.fetchall()

    id_siswa_param = request.args.get('id_siswa')

    if request.method == 'POST':
        id_siswa = request.form.get('id_siswa')

        # =========================
        # VALIDASI
        # =========================
        errors = {}

        if not id_siswa:
            errors['id_siswa'] = "Nama siswa harus dipilih"

        if not request.form.get('academic_pressure'):
            errors['academic_pressure'] = "Pilih tekanan akademik"

        if not request.form.get('sleep_duration'):
            errors['sleep_duration'] = "Pilih durasi tidur"

        if not request.form.get('financial_stress'):
            errors['financial_stress'] = "Pilih tekanan finansial"

        if not request.form.get('family_history'):
            errors['family_history'] = "Pilih jawaban"

        if not request.form.get('suicidal_thoughts'):
            errors['suicidal_thoughts'] = "Pilih jawaban"

        if not request.form.get('dietary_habits'):
            errors['dietary_habits'] = "Pilih pola makan"

        if not request.form.get('study_satisfaction'):
            errors['study_satisfaction'] = "Pilih kepuasan belajar"

        if not request.form.get('work_study_hours'):
            errors['work_study_hours'] = "Pilih jam belajar"

        # 🔴 kalau ada error → kembali ke form
        if errors:
            return render_template(
                "kuesioner/tambah.html",
                siswa=siswa,
                id_siswa_param=id_siswa_param,
                errors=errors
            )

        cursor.execute(
            "SELECT COUNT(*) FROM kuesioner WHERE id_siswa=%s",
            (id_siswa,)
        )
        sudah_ada = cursor.fetchone()[0]

        if sudah_ada > 0:
            errors['id_siswa'] = "Siswa sudah pernah mengisi kuesioner"
            return render_template(
                "kuesioner/tambah.html",
                siswa=siswa,
                id_siswa_param=id_siswa_param,
                errors=errors
            )

        academic_pressure = int(request.form.get('academic_pressure'))
        sleep_duration = clean(request.form.get('sleep_duration'))
        financial_stress = int(request.form.get('financial_stress'))
        family_history = clean(request.form.get('family_history'))
        suicidal_thoughts = request.form.get('suicidal_thoughts')
        dietary_habits = clean(request.form.get('dietary_habits'))
        study_satisfaction = int(request.form.get('study_satisfaction'))
        work_study_hours = int(request.form.get('work_study_hours'))



        cursor.execute("""
        INSERT INTO kuesioner (
            id_siswa,
            academic_pressure,
            sleep_duration,
            financial_stress,
            family_history,
            suicidal_thoughts,
            dietary_habits,
            study_satisfaction,
            work_study_hours
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            id_siswa,
            academic_pressure,
            sleep_duration,
            financial_stress,
            family_history,
            suicidal_thoughts,
            dietary_habits,
            study_satisfaction,
            work_study_hours
        ))

        return redirect('/prediksi')

    cursor.close()

    return render_template(
        "kuesioner/tambah.html",
        siswa=siswa,
        id_siswa_param=id_siswa_param,
        errors={}
    )

# =========================
# EDIT
# =========================
@kuesioner_bp.route('/kuesioner/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    cursor = db.cursor()

    if request.method == 'POST':
        academic_pressure = int(request.form.get('academic_pressure'))
        sleep_duration = clean(request.form.get('sleep_duration'))
        financial_stress = int(request.form.get('financial_stress'))
        family_history = clean(request.form.get('family_history'))
        suicidal_thoughts = request.form.get('suicidal_thoughts')
        dietary_habits = clean(request.form.get('dietary_habits'))
        study_satisfaction = int(request.form.get('study_satisfaction'))
        work_study_hours = int(request.form.get('work_study_hours'))

        cursor.execute("""
        UPDATE kuesioner
        SET academic_pressure=%s,
            sleep_duration=%s,
            financial_stress=%s,
            family_history=%s,
            suicidal_thoughts=%s,
            dietary_habits=%s,
            study_satisfaction=%s,
            work_study_hours=%s
        WHERE id_kuesioner=%s
        """, (
            academic_pressure,
            sleep_duration,
            financial_stress,
            family_history,
            suicidal_thoughts,
            dietary_habits,
            study_satisfaction,
            work_study_hours,
            id
        ))

        return redirect('/kuesioner')

    cursor.execute("SELECT * FROM kuesioner WHERE id_kuesioner=%s", (id,))
    data = cursor.fetchone()

    cursor.close()

    return render_template("kuesioner/edit.html", k=data)

# =========================
# DELETE
# =========================
@kuesioner_bp.route('/kuesioner/delete/<int:id>')
def delete(id):
    cursor = db.cursor()

    cursor.execute("DELETE FROM kuesioner WHERE id_kuesioner=%s", (id,))

    cursor.close()

    return redirect('/kuesioner')