from flask import Flask, render_template, request, send_file
from weasyprint import HTML
import io
import unicodedata
import re

app = Flask(__name__)

def limpiar_nombre(nombre):
    nombre = str(nombre)
    nombre = unicodedata.normalize('NFKD', nombre).encode('ascii', 'ignore').decode('ascii')
    nombre = re.sub(r'[^\w]+', '_', nombre)
    return nombre.strip('_').lower()

@app.route('/', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        datos = {
            "nombre": request.form["nombre"],
            "dni": request.form["dni"],
            "residencia": request.form["residencia"],
            "trastero": request.form["trastero"],
            "superficie": request.form["superficie"],
            "fechainicio": request.form["fechainicio"],
            "fechafinal": request.form["fechafinal"],
            "preciooriginal": request.form["preciooriginal"],
            "iva": request.form["iva"],
            "preciototal": request.form["preciototal"],
            "fechafirma": request.form["fechafirma"]
        }

        html = render_template("contrato.html", **datos)
        pdf = HTML(string=html, base_url=".").write_pdf()

        nombre_archivo = limpiar_nombre(datos["nombre"]) + ".pdf"
        return send_file(
            io.BytesIO(pdf),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"contrato_{nombre_archivo}"
        )

    return render_template("formulario.html")

if __name__ == '__main__':
    app.run(debug=True)
