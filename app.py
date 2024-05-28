from flask import Flask, render_template, request, redirect, url_for, flash, session
from neo4jconnection import Neo4jConnection

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# Configuración de la conexión a Neo4j
neo4j_conn = Neo4jConnection("bolt://localhost:7687", "neo4j", "password")

@app.route('/')
def home():
    return render_template('introduccion.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Validar usuario y contraseña con Neo4j
        query = "MATCH (u:User {username: $username, password: $password}) RETURN u"
        parameters = {"username": username, "password": password}
        result = neo4j_conn.query(query, parameters)
        user = result[0] if result else None
        if user:
            session['username'] = username  # Almacena el nombre de usuario en la sesión
            flash('Inicio de sesión exitoso.')
            return redirect(url_for('web'))  # Redirige a la tienda
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
        # Registrar el nuevo usuario en Neo4j
        if password == confirm_password:
            neo4j_conn.query("CREATE (u:User {username: $username, email: $email, password: $password})", 
                            username=username, email=email, password=password)
            session['username'] = username  # Almacena el nombre de usuario en la sesión después del registro
            flash('Registro exitoso.')
            return redirect(url_for('survey'))  # Redirige a la encuesta
        else:
            flash('Las contraseñas no coinciden.')
    return render_template('register.html')

@app.route('/survey', methods=['GET', 'POST'])
def survey():
    if request.method == 'POST':
        # Procesar respuestas de la encuesta
        return redirect(url_for('web'))  
    return render_template('Encuesta.html')  

@app.route('/store')
def store():
    username = session.get('username')  # Recupera el nombre de usuario de la sesión
    if not username:
        return redirect(url_for('login'))  # Redirige al usuario a la página de inicio de sesión si no hay nombre de usuario en la sesión
    return render_template('web.html', username=username)

@app.route('/web')
def web():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    return render_template('web.html', username=username)

if __name__ == '__main__':
    app.run(debug=True)

# Cierre de la conexión al salir de la aplicación
@app.teardown_appcontext
def close_driver(exception):
    neo4j_conn.close()
