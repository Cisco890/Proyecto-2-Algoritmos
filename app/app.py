from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'super_secret_key'  

# Ruta de la página de introducción
@app.route('/')
def home():
    return render_template('introduccion.html')

# Ruta de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        return redirect(url_for('home'))  # Redirige a la página principal tras el inicio de sesión
    return render_template('login.html')

# Ruta de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
      
        return redirect(url_for('home'))  
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
