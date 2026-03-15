from flask import Flask, render_template
from routes.siswa import siswa_bp
from routes.kuesioner import kuesioner_bp
from routes.prediksi import prediksi_bp
import mysql.connector

app = Flask(__name__)

# =============================
# KONEKSI DATABASE
# =============================
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="prediksi_depresi",
    autocommit=True
)

# =============================
# REGISTER BLUEPRINT
# =============================
app.register_blueprint(siswa_bp)
app.register_blueprint(kuesioner_bp)
app.register_blueprint(prediksi_bp)

# =============================
# DASHBOARD
# =============================
@app.route("/")
def dashboard():

    cursor = db.cursor()

    # total siswa
    cursor.execute("SELECT COUNT(*) FROM siswa")
    total_siswa = cursor.fetchone()[0] or 0

    # total kuesioner
    cursor.execute("SELECT COUNT(*) FROM kuesioner")
    total_kuesioner = cursor.fetchone()[0] or 0

    # total depresi
    cursor.execute("SELECT COUNT(*) FROM hasil_prediksi WHERE hasil='Depresi'")
    total_depresi = cursor.fetchone()[0] or 0

    # total tidak depresi
    cursor.execute("SELECT COUNT(*) FROM hasil_prediksi WHERE hasil='Tidak Depresi'")
    total_tidak = cursor.fetchone()[0] or 0

    cursor.close()

    return render_template(
        "dashboard.html",
        total_siswa=int(total_siswa),
        total_kuesioner=int(total_kuesioner),
        total_depresi=int(total_depresi),
        total_tidak=int(total_tidak)
    )


# =============================
# RUN APP
# =============================
if __name__ == "__main__":
    app.run(debug=True)