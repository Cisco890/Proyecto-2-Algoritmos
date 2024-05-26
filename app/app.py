from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'super_secret_key'

@app.route('/')
def home():
    return render_template('introduccion.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Aquí deberías validar el usuario y la contraseña
        if username == 'admin' and password == 'password':  # Ejemplo de validación
            flash('Inicio de sesión exitoso.')
            return redirect(url_for('store'))  # Redirige a la tienda
        else:
            flash('Nombre de usuario o contraseña incorrectos.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        # Aquí deberías registrar el nuevo usuario
        if password == confirm_password:
            flash('Registro exitoso.')
            return redirect(url_for('survey'))  # Redirige a la encuesta
        else:
            flash('Las contraseñas no coinciden.')
    return render_template('register.html')

@app.route('/survey', methods=['GET', 'POST'])
def survey():
    if request.method == 'POST':
        # Aquí puedes manejar las respuestas de la encuesta
        return redirect(url_for('web'))  # Redirige a la página web.html
    return render_template('Encuesta.html')  # Asegúrate de usar 'Encuesta.html'

@app.route('/store')
def store():
    return render_template('store.html')

@app.route('/web')
def web():
    return render_template('web.html')

if __name__ == '__main__':
    app.run(debug=True)


