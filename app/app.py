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
            return redirect(url_for('home'))
        else:
            flash('Nombre de usuario o contraseña incorrectos.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Aquí deberías registrar el nuevo usuario


        
        flash('Registro exitoso.')
        return redirect(url_for('home'))
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)

