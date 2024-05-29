from flask import Flask, render_template, request, redirect, url_for, flash, session
from neo4jconnection import Neo4jConnection
from random import sample, choice

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# Configuración de la conexión a Neo4j
neo4j_conn = Neo4jConnection("bolt://localhost:7687", "neo4j", "password")

def close_driver(exception):
    neo4j_conn.close()

# Funciones Neo4j
def obtener_nombre_nodo(consulta):
    resultado = neo4j_conn.query(consulta)
    return [record['n.name'] for record in resultado]

def ValidadorLogin(User, Password):
    query = "MATCH (u:User {name: $username, password: $password}) RETURN u.name AS name"
    result = neo4j_conn.query(query, parameters={'username': User, 'password': Password})
    return len(result) == 1

def get_product_names_for_user(Usuario):
    query = "MATCH (u:User {name: $user_id})-[:COMPRO]->(f:Factura) RETURN COLLECT(f.producto) AS productos"
    result = neo4j_conn.query(query, parameters={'user_id': Usuario})
    return result[0]["productos"] if result else []

def get_product_marca_for_compra(producto):
    query = "MATCH (n:Product {name:$producto}) RETURN n.marca AS marca"
    result = neo4j_conn.query(query, parameters={'producto': producto})
    return result[0]["marca"] if result else None

def get_product_tipo_for_compra(producto):
    query = "MATCH (n:Product {name:$producto}) RETURN n.Tipo AS Tipo"
    result = neo4j_conn.query(query, parameters={'producto': producto})
    return result[0]["Tipo"] if result else None

def get_product_sex_for_compra(producto):
    query = "MATCH (n:Product {name:$producto}) RETURN n.Sexo AS Sexo"
    result = neo4j_conn.query(query, parameters={'producto': producto})
    return result[0]["Sexo"] if result else None

def Precomendado(Usuario, result):
    for results in result:
        query = "MATCH (U:User{name:$usuario})-[r:COMPRO]->(f:Factura) WHERE f.producto=$producto RETURN f.producto AS producto"
        x = neo4j_conn.query(query, parameters={'usuario': Usuario, 'producto': results})
        x = [record['producto'] for record in x]
        if len(x) == 0:
            query = "MATCH (U:User{name:$usuario})-[r:RecommendsToBuy]->(p:Product) WHERE p.name=$producto RETURN p.name AS producto"
            x = neo4j_conn.query(query, parameters={'usuario': Usuario, 'producto': results})
            x = [record['producto'] for record in x]
            if len(x) == 0:
                return results
    query = "MATCH(p:Product) RETURN p.name AS name"
    result = neo4j_conn.query(query)
    result = [record['name'] for record in result]
    for results in result:
        query = "MATCH (U:User{name:$usuario})-[r:COMPRO]->(f:Factura) WHERE f.producto=$producto RETURN f.producto AS producto"
        x = neo4j_conn.query(query, parameters={'usuario': Usuario, 'producto': results})
        x = [record["producto"] for record in x]
        if len(x) == 0:
            query = "MATCH (U:User{name:$usuario})-[r:RecommendsToBuy]->(p:Product) WHERE p.name=$producto RETURN p.name AS producto"
            x = neo4j_conn.query(query, parameters={'usuario': Usuario, 'producto': results})
            x = [record['producto'] for record in x]
            if len(x) == 0:
                return results
    query = "MATCH(p:Product) RETURN p.name AS name"
    result = neo4j_conn.query(query)
    result = [record['name'] for record in result]
    return choice(result)

def borrar_Recomendaciones(Usuario):
    query = "MATCH (u:User)-[r:RecommendsToBuy]->() WHERE u.name=$user DELETE r"
    neo4j_conn.query(query, parameters={'user': Usuario})

def Crear_Recomendaciones(Usuario, precomend):
    try:
        query = """
        MATCH(u:User {name: $user})
        MATCH(f:Product {name: $producto})
        MERGE (u)-[:RecommendsToBuy]->(f)
        """
        neo4j_conn.query(query, parameters={'user': Usuario, 'producto': precomend})
        print(f"Recomendación creada: {Usuario} - RecommendsToBuy -> {precomend}")
    except Exception as e:
        print(f"Error creando la recomendación: {e}")

def Recomendaciones(Usuario, gender, tipo_preferido=None):
    borrar_Recomendaciones(Usuario)
    
    recomendaciones = []

    if tipo_preferido:
        # Obtener 3 productos del mismo tipo del producto comprado
        query = """
        MATCH (p:Product {Tipo: $tipo_preferido, Sexo: $sexo})
        RETURN p.name AS name, p.marca AS marca, p.Tipo AS tipo, p.Sexo AS sexo
        LIMIT 3
        """
        result = neo4j_conn.query(query, parameters={'tipo_preferido': tipo_preferido, 'sexo': gender})
        if result:
            recomendaciones.extend(result)
        
        # Obtener 2 productos de otros tipos
        query = """
        MATCH (p:Product {Sexo: $sexo})
        WHERE NOT p.Tipo = $tipo_preferido
        RETURN p.name AS name, p.marca AS marca, p.Tipo AS tipo, p.Sexo AS sexo
        LIMIT 2
        """
        result = neo4j_conn.query(query, parameters={'sexo': gender, 'tipo_preferido': tipo_preferido})
        if result:
            recomendaciones.extend(result)
    else:
        # Obtener 3 productos basados en la respuesta de la encuesta
        categorias = ['Deporte', 'Elegante', 'Montaña', 'Casual', 'Trabajo pesado']
        preferencia_categorias = []
        query = """
        MATCH (u:User {name: $username})-[:ANSWERED]->(a:Answer)
        RETURN a.question AS question, a.answer AS answer
        """
        result = neo4j_conn.query(query, parameters={'username': Usuario})
        answers = {record['question']: record['answer'] for record in result}
        
        if answers.get('question1') == 'yes':
            preferencia_categorias.append('Deporte')
        if answers.get('question2') == 'yes':
            preferencia_categorias.append('Elegante')
        if answers.get('question3') == 'yes':
            preferencia_categorias.append('Montaña')
        if answers.get('question4') == 'yes':
            preferencia_categorias.append('Casual')
        if answers.get('question5') == 'yes':
            preferencia_categorias.append('Trabajo pesado')
        
        if preferencia_categorias:
            for categoria in sample(preferencia_categorias, min(3, len(preferencia_categorias))):
                query = """
                MATCH (p:Product {Tipo: $categoria, Sexo: $sexo})
                RETURN p.name AS name, p.marca AS marca, p.Tipo AS tipo, p.Sexo AS sexo
                LIMIT 1
                """
                result = neo4j_conn.query(query, parameters={'categoria': categoria, 'sexo': gender})
                if result:
                    recomendaciones.extend(result)
        
        # Obtener 2 productos de otros tipos
        if len(recomendaciones) < 5:
            query = """
            MATCH (p:Product {Sexo: $sexo})
            WHERE NOT p.Tipo IN $preferencia_categorias
            RETURN p.name AS name, p.marca AS marca, p.Tipo AS tipo, p.Sexo AS sexo
            LIMIT 2
            """
            result = neo4j_conn.query(query, parameters={'sexo': gender, 'preferencia_categorias': preferencia_categorias})
            if result:
                recomendaciones.extend(result)
    
    # Crear relaciones de recomendación para el usuario
    for producto in recomendaciones:
        Crear_Recomendaciones(Usuario, producto['name'])

    print("Recomendaciones generadas para el usuario:", Usuario)

def Compra(Nombre, Producto, Precio):
    query = """
    MATCH (u:User {name:$nombre_usuario})
    MERGE (f:Factura {producto: $producto, total: $precio})
    MERGE (u)-[:COMPRO]->(f)
    RETURN u, f
    """
    neo4j_conn.query(query, parameters={'nombre_usuario': Nombre, 'producto': Producto, 'precio': Precio})
    print("Se ha realizado correctamente la compra")

# Rutas de Flask
@app.route('/')
def home():
    return render_template('introduccion.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Validar usuario y contraseña con Neo4j
        if ValidadorLogin(username, password):
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
        # Validar las contraseñas
        if password == confirm_password:
            session['username'] = username
            session['email'] = email
            session['password'] = password
            return redirect(url_for('survey'))
        else:
            flash('Las contraseñas no coinciden.')
    return render_template('register.html')

@app.route('/survey', methods=['GET', 'POST'])
def survey():
    if request.method == 'POST':
        answers = request.form.to_dict()
        username = session.get('username')
        email = session.get('email')
        password = session.get('password')
        gender = answers.get('gender')  # Obtener el género del formulario
        
        if username and email and password:
            # Crear el nodo de usuario en Neo4j
            try:
                query = """
                CREATE (u:User {name: $username, email: $email, password: $password, gender: $gender})
                """
                neo4j_conn.query(query, parameters={'username': username, 'email': email, 'password': password, 'gender': gender})
                print(f"Usuario creado: {username}")
                
                for question, answer in answers.items():
                    query = """
                    MATCH (u:User {name: $username})
                    MERGE (a:Answer {question: $question, answer: $answer})
                    MERGE (u)-[:ANSWERED]->(a)
                    """
                    neo4j_conn.query(query, parameters={'username': username, 'question': question, 'answer': answer})
                    print(f"Relacion creada: {username} - ANSWERED -> {question}: {answer}")

                # Generar recomendaciones basadas en la encuesta
                Recomendaciones(username, gender)
            except Exception as e:
                print(f"Error creando usuario y respuestas: {e}")
                flash('Error creando usuario y respuestas.')
                return redirect(url_for('register'))
            
            return redirect(url_for('web'))
        else:
            flash('No se pudo identificar al usuario.')
            return redirect(url_for('register'))
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
    
    query = """
        MATCH (u:User {name: $username})-[:RecommendsToBuy]->(p:Product)
        RETURN p.name AS name, p.marca AS marca, p.Tipo AS tipo, p.Sexo AS sexo
    """
    try:
        result = neo4j_conn.query(query, parameters={'username': username})
        products = [{'name': record['name'], 'marca': record['marca'], 'tipo': record['tipo'], 'sexo': record['sexo']} for record in result]
        if not products:
            flash('No hay recomendaciones disponibles en este momento.')
            print(f"No se encontraron recomendaciones para el usuario: {username}")
    except Exception as e:
        print(f"Error al obtener recomendaciones: {e}")
        products = []

    return render_template('web.html', products=products, username=username)

@app.route('/buy', methods=['POST'])
def buy():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    product_name = request.form['product_name']
    product_price = request.form['product_price']
    
    Compra(username, product_name, product_price)
    
    # Obtener el género del usuario para actualizar las recomendaciones
    query = "MATCH (u:User {name: $username}) RETURN u.gender AS gender"
    result = neo4j_conn.query(query, parameters={'username': username})
    gender = result[0]['gender']
    
    # Obtener el tipo del producto comprado
    query = "MATCH (p:Product {name: $product_name}) RETURN p.Tipo AS tipo"
    result = neo4j_conn.query(query, parameters={'product_name': product_name})
    tipo_preferido = result[0]['tipo']
    
    # Actualizar recomendaciones después de la compra
    Recomendaciones(username, gender, tipo_preferido)
    
    flash('Compra realizada con éxito.')
    return redirect(url_for('web'))

if __name__ == '__main__':
    app.run(debug=True)

# Cierre de la conexión al salir de la aplicación
@app.teardown_appcontext
def close_driver(exception):
    neo4j_conn.close()
