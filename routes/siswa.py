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

# CLEAN FUNCTION
def clean(val):
    if isinstance(val, str):
        return val.strip()
    return val


# READ
@siswa_bp.route('/siswa')
def lihat_siswa():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM siswa")
    data = cursor.fetchall()
    cursor.close()
    return render_template("siswa/index.html", data=data)


# CREATE
@siswa_bp.route('/siswa/tambah', methods=['GET', 'POST'])
def form_tambah():

    if request.method == 'POST':
        nisn = clean(request.form['nisn'])
        nama = clean(request.form['nama'])
        gender = clean(request.form['gender'])
        umur = request.form['umur']
        kelas = clean(request.form['kelas'])

        # VALIDASI
        if not nisn.isdigit() or len(nisn) != 10:
            return redirect('/siswa/tambah?error=nisn_format')

        try:
            umur = int(umur)
        except:
            return redirect('/siswa/tambah?error=umur')

        if gender not in ['L', 'P']:
            return redirect('/siswa/tambah?error=gender')

        cursor = db.cursor()

        # CEK DUPLIKAT
        cursor.execute("SELECT id_siswa FROM siswa WHERE nisn=%s", (nisn,))
        cek = cursor.fetchone()

        if cek:
            cursor.close()
            return redirect('/siswa/tambah?error=nisn')

        cursor.execute("""
            INSERT INTO siswa (nisn, nama, gender, umur, kelas)
            VALUES (%s, %s, %s, %s, %s)
        """, (nisn, nama, gender, umur, kelas))

        cursor.execute("SELECT LAST_INSERT_ID()")
        id_siswa = cursor.fetchone()[0]

        cursor.close()

        return redirect(f'/kuesioner/tambah?id_siswa={id_siswa}')

    return render_template("siswa/tambah.html")


# EDIT
@siswa_bp.route('/siswa/edit/<int:id_siswa>', methods=['GET', 'POST'])
def edit_siswa(id_siswa):
    cursor = db.cursor()

    if request.method == 'POST':
        nisn = clean(request.form['nisn'])
        nama = clean(request.form['nama'])
        gender = clean(request.form['gender'])
        umur = request.form['umur']
        kelas = clean(request.form['kelas'])

        if not nisn.isdigit() or len(nisn) != 10:
            return redirect(f'/siswa/edit/{id_siswa}?error=nisn_format')

        try:
            umur = int(umur)
        except:
            return redirect(f'/siswa/edit/{id_siswa}?error=umur')

        if gender not in ['L', 'P']:
            return redirect(f'/siswa/edit/{id_siswa}?error=gender')

        # CEK DUPLIKAT (KECUALI DIRI SENDIRI)
        cursor.execute("""
            SELECT id_siswa FROM siswa 
            WHERE nisn=%s AND id_siswa != %s
        """, (nisn, id_siswa))

        cek = cursor.fetchone()

        if cek:
            cursor.close()
            return redirect(f'/siswa/edit/{id_siswa}?error=nisn')

        cursor.execute("""
            UPDATE siswa
            SET nisn=%s, nama=%s, gender=%s, umur=%s, kelas=%s
            WHERE id_siswa=%s
        """, (nisn, nama, gender, umur, kelas, id_siswa))

        cursor.close()
        return redirect('/siswa')

    cursor.execute("SELECT * FROM siswa WHERE id_siswa=%s", (id_siswa,))
    siswa = cursor.fetchone()
    cursor.close()

    return render_template("siswa/edit.html", siswa=siswa)


# DELETE
@siswa_bp.route('/siswa/delete/<int:id_siswa>')
def delete_siswa(id_siswa):
    cursor = db.cursor()
    cursor.execute("DELETE FROM siswa WHERE id_siswa=%s", (id_siswa,))
    cursor.close()
    return redirect('/siswa')

# Ajax cek NISNS
@siswa_bp.route('/cek_nisn')
def cek_nisn():
    nisn = request.args.get('nisn')

    cursor = db.cursor()
    cursor.execute("SELECT id_siswa FROM siswa WHERE nisn=%s", (nisn,))
    data = cursor.fetchone()
    cursor.close()

    return jsonify({"exists": bool(data)})


# Ajax cek NISNS
@siswa_bp.route('/cek_nisn_edit')
def cek_nisn_edit():
    nisn = request.args.get('nisn')
    id_siswa = request.args.get('id_siswa')

    cursor = db.cursor()
    cursor.execute("""
        SELECT id_siswa FROM siswa 
        WHERE nisn=%s AND id_siswa != %s
    """, (nisn, id_siswa))

    data = cursor.fetchone()
    cursor.close()

    return jsonify({"exists": bool(data)})