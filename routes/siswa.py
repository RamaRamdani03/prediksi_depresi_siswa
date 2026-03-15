from flask import Blueprint, render_template, request, redirect
import mysql.connector

siswa_bp = Blueprint('siswa', __name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="prediksi_depresi",
    autocommit=True
)

# =========================
# READ
# =========================
@siswa_bp.route('/siswa')
def lihat_siswa():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM siswa")
    data = cursor.fetchall()
    cursor.close()
    return render_template("siswa/index.html", data=data)


# =========================
# CREATE
# =========================
@siswa_bp.route('/siswa/tambah', methods=['GET', 'POST'])
def form_tambah():

    if request.method == 'POST':
        nama = request.form['nama']
        gender = request.form['gender']
        umur = request.form['umur']
        kelas = request.form['kelas']

        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO siswa (nama, gender, umur, kelas)
            VALUES (%s, %s, %s, %s)
        """, (nama, gender, umur, kelas))
        cursor.close()

        return redirect('/siswa')

    return render_template("siswa/tambah.html")


# =========================
# EDIT
# =========================
@siswa_bp.route('/siswa/edit/<int:id_siswa>', methods=['GET', 'POST'])
def edit_siswa(id_siswa):
    cursor = db.cursor()

    if request.method == 'POST':
        nama = request.form['nama']
        gender = request.form['gender']
        umur = request.form['umur']
        kelas = request.form['kelas']

        cursor.execute("""
            UPDATE siswa
            SET nama=%s, gender=%s, umur=%s, kelas=%s
            WHERE id_siswa=%s
        """, (nama, gender, umur, kelas, id_siswa))

        cursor.close()
        return redirect('/siswa')

    cursor.execute("SELECT * FROM siswa WHERE id_siswa=%s", (id_siswa,))
    siswa = cursor.fetchone()
    cursor.close()

    return render_template("siswa/edit.html", siswa=siswa)


# =========================
# DELETE
# =========================
@siswa_bp.route('/siswa/delete/<int:id_siswa>')
def delete_siswa(id_siswa):
    cursor = db.cursor()
    cursor.execute("DELETE FROM siswa WHERE id_siswa=%s", (id_siswa,))
    cursor.close()

    return redirect('/siswa')