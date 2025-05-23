from flask import Flask, render_template, request, send_file, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from weasyprint import HTML
import io
import unicodedata
import re
import os

# Inicialización
basedir = os.path.abspath(os.path.dirname(__file__))

# ✅ Asegura que la carpeta "data" exista antes de configurar la DB
data_dir = os.path.join(basedir, "data")
os.makedirs(data_dir, exist_ok=True)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(data_dir, 'contratos.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de datos
class Contrato(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    dni = db.Column(db.String(20))
    residencia = db.Column(db.String(200))
    trastero = db.Column(db.String(10))
    superficie = db.Column(db.String(10))
    fechainicio = db.Column(db.String(50))
    fechafinal = db.Column(db.String(50))
    preciooriginal = db.Column(db.Float)
    iva = db.Column(db.Float)
    preciototal = db.Column(db.Float)
    fechafirma = db.Column(db.String(50))

# Limpieza del nombre de archivo
def limpiar_nombre(nombre):
    nombre = str(nombre)
    nombre = unicodedata.normalize('NFKD', nombre).encode('ascii', 'ignore').decode('ascii')
    nombre = re.sub(r'[^\w]+', '_', nombre)
    return nombre.strip('_').lower()

# Ruta para crear la BD manualmente en Render
@app.route('/initdb')
def initdb():
    db.create_all()
    return "✅ Base de datos creada correctamente."

# Formulario principal y edición
@app.route('/', methods=['GET', 'POST'])
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def formulario(id=None):
    contrato = Contrato.query.get(id) if id else None

    if request.method == 'POST':
        datos = {
            "nombre": request.form["nombre"],
            "dni": request.form["dni"],
            "residencia": request.form["residencia"],
            "trastero": request.form["trastero"],
            "superficie": request.form["superficie"],
            "fechainicio": request.form["fechainicio"],
            "fechafinal": request.form["fechafinal"],
            "preciooriginal": float(request.form["preciooriginal"].replace(',', '.')),
            "iva": float(request.form["iva"].replace(',', '.')),
            "preciototal": float(request.form["preciototal"].replace(',', '.')),
            "fechafirma": request.form["fechafirma"]
        }

        if contrato:
            for key, value in datos.items():
                setattr(contrato, key, value)
        else:
            contrato = Contrato(**datos)
            db.session.add(contrato)

        db.session.commit()

        # Generar PDF
        html = render_template("contrato.html", **datos)
        pdf = HTML(string=html, base_url=".").write_pdf()
        nombre_archivo = limpiar_nombre(datos["nombre"]) + ".pdf"

        return send_file(
            io.BytesIO(pdf),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"contrato_{nombre_archivo}"
        )

    return render_template("formulario.html", contrato=contrato)

# Historial
@app.route('/historial')
def historial():
    contratos = Contrato.query.order_by(Contrato.id.desc()).all()
    return render_template("historial.html", contratos=contratos)

# Ejecución local
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
