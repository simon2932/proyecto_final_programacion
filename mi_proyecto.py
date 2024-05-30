from flask import Flask, render_template, request, redirect, url_for
import random
import string
import csv

app = Flask(__name__)

datos_usuarios = {}
datos_aplicaciones = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        contrasena = request.form['contrasena']
        if correo in datos_usuarios and datos_usuarios[correo]["contrasena"] == contrasena:
            return redirect(url_for('dashboard', correo=correo))
        else:
            return "Usuario o contraseña incorrectos"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        correo = request.form['correo']
        contrasena = request.form['contrasena']
        confirmar_contrasena = request.form['confirmar_contrasena']
        if contrasena != confirmar_contrasena:
            return "Las contraseñas no coinciden"
        else:
            usuario = {"nombre": nombre, "apellido": apellido, "correo": correo, "contrasena": contrasena}
            datos_usuarios[correo] = usuario
            datos_aplicaciones[correo] = {"aplicaciones": []}
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard/<correo>')
def dashboard(correo):
    return render_template('dashboard.html', usuario=datos_usuarios[correo], aplicaciones=datos_aplicaciones[correo]["aplicaciones"])

@app.route('/add_application/<correo>', methods=['GET', 'POST'])
def add_application(correo):
    if request.method == 'POST':
        imagen = "imagen"  # Esto se puede cambiar para subir imágenes reales
        nombre_aplicacion = request.form['nombre_aplicacion']
        nombre_usuario = request.form['nombre_usuario']
        contrasena = request.form['contrasena']
        correo_aplicacion = request.form['correo_aplicacion']
        aplicacion = {"imagen": imagen, "nombre_aplicacion": nombre_aplicacion, "nombre_usuario": nombre_usuario, "contrasena": contrasena, "correo": correo_aplicacion}
        datos_aplicaciones[correo]["aplicaciones"].append(aplicacion)
        return redirect(url_for('dashboard', correo=correo))
    return render_template('add_application.html', correo=correo)

@app.route('/edit_application/<correo>/<int:app_index>', methods=['GET', 'POST'])
def edit_application(correo, app_index):
    if request.method == 'POST':
        nombre_aplicacion = request.form['nombre_aplicacion']
        nombre_usuario = request.form['nombre_usuario']
        contrasena = request.form['contrasena']
        correo_aplicacion = request.form['correo_aplicacion']
        aplicacion = datos_aplicaciones[correo]["aplicaciones"][app_index]
        aplicacion['nombre_aplicacion'] = nombre_aplicacion
        aplicacion['nombre_usuario'] = nombre_usuario
        aplicacion['contrasena'] = contrasena
        aplicacion['correo'] = correo_aplicacion
        return redirect(url_for('dashboard', correo=correo))
    aplicacion = datos_aplicaciones[correo]["aplicaciones"][app_index]
    return render_template('edit_application.html', correo=correo, app_index=app_index, aplicacion=aplicacion)

@app.route('/delete_application/<correo>/<int:app_index>')
def delete_application(correo, app_index):
    del datos_aplicaciones[correo]["aplicaciones"][app_index]
    return redirect(url_for('dashboard', correo=correo))

@app.route('/generate_password/<correo>', methods=['POST'])
def generate_password(correo):
    longitud = int(request.form['longitud'])
    contrasena = "".join(random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(longitud))
    return contrasena

@app.route('/export/<correo>')
def export(correo):
    aplicaciones = datos_aplicaciones[correo]["aplicaciones"]
    with open(f'{correo}_passwords.csv', 'w', newline='') as csvfile:
        fieldnames = ['nombre_aplicacion', 'nombre_usuario', 'contrasena', 'correo']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for app in aplicaciones:
            writer.writerow(app)
    return f'{correo}_passwords.csv exportado correctamente'

@app.route('/import/<correo>', methods=['GET', 'POST'])
def import_csv(correo):
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            file_content = file.stream.read().decode('utf-8')
            csv_reader = csv.DictReader(file_content.splitlines())
            for row in csv_reader:
                datos_aplicaciones[correo]["aplicaciones"].append(row)
            return redirect(url_for('dashboard', correo=correo))
    return render_template('import.html', correo=correo)

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
