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
# READ DATA KUESIONER
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
# FORM TAMBAH KUESIONER
# =========================
@kuesioner_bp.route('/kuesioner/tambah', methods=['GET','POST'])
def tambah():

    cursor = db.cursor()

    cursor.execute("SELECT id_siswa,nama FROM siswa")
    siswa = cursor.fetchall()

    if request.method == 'POST':

        id_siswa = request.form.get('id_siswa')
        academic_pressure = request.form.get('academic_pressure')
        sleep_duration = request.form.get('sleep_duration')
        financial_stress = request.form.get('financial_stress')
        family_history = request.form.get('family_history')
        suicidal_thoughts = request.form.get('suicidal_thoughts')
        dietary_habits = request.form.get('dietary_habits')
        study_satisfaction = request.form.get('study_satisfaction')
        work_study_hours = request.form.get('work_study_hours')

        cursor.execute("""
        INSERT INTO kuesioner
        (
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
        """,
        (
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

        return redirect('/kuesioner')

    cursor.close()

    return render_template("kuesioner/tambah.html", siswa=siswa)


# =========================
# EDIT KUESIONER
# =========================
@kuesioner_bp.route('/kuesioner/edit/<int:id>', methods=['GET','POST'])
def edit(id):

    cursor = db.cursor()

    if request.method == 'POST':

        academic_pressure = request.form.get('academic_pressure')
        sleep_duration = request.form.get('sleep_duration')
        financial_stress = request.form.get('financial_stress')
        family_history = request.form.get('family_history')
        suicidal_thoughts = request.form.get('suicidal_thoughts')
        dietary_habits = request.form.get('dietary_habits')
        study_satisfaction = request.form.get('study_satisfaction')
        work_study_hours = request.form.get('work_study_hours')

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
        """,
        (
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

    cursor.execute("SELECT * FROM kuesioner WHERE id_kuesioner=%s",(id,))
    data = cursor.fetchone()

    cursor.close()

    return render_template("kuesioner/edit.html", k=data)


# =========================
# DELETE
# =========================
@kuesioner_bp.route('/kuesioner/delete/<int:id>')
def delete(id):

    cursor = db.cursor()

    cursor.execute("DELETE FROM kuesioner WHERE id_kuesioner=%s",(id,))

    cursor.close()

    return redirect('/kuesioner')