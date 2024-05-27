"""
                DOCUMENTACIÓN INTERNA


    Autor: Olivier Viau
    Lenguajes: Python, Cypher

    Objetivo: Crear los querys y el algoritmo de recomendaciones de una página web de venta de zapatos

    #historial de modificaciones

    [000] 21/5/2024
    [001] 22/5/2024
    [002] 26/5/2024
"""




import os
import json 
from flask import Flask, g,Response, request
from neo4j import GraphDatabase, basic_auth
from random import randint

driver=GraphDatabase.driver(uri="bolt://localhost:7687",auth=("neo4j","password")) #sesión de la database
session=driver.session()#abre la session para poder buscar los datos en la base de datos
driver.verify_connectivity() #verifica la conexión
query="" "match (n:Product) return (n)" #query
results=session.run(query) #resultado
for result in results:
    #print(result)
    pass



def ValidadorLogin(User,Password):#Valida el login
    query="" "MATCH(n:User) WHERE n.name='{}' AND n.Password='{}' Return n.name".format(User,Password) #query para comparar los datos obtenidos con los de la db
    result=obtener_nombre_nodo(query)
    if len(result)==1: #si si existe un resultado entra a la cuenta
        print("Bienvenido")
    else: #si no da error
        print("Contraseña o usuario incorrecto")


def obtener_nombre_nodo(consulta):#encuentra el nombre de un nodo y lo da en una lista
    with driver.session() as sesion:
        resultado = sesion.run(consulta) 
        # Devuelve solo el nombre de cada nodo
        return ([record['n.name'] for record in resultado]) #da el formato en forma de lista
    
def IngresarProducto(Sexo,Tipo,marca,nombre):#ingresa productos nuevos
    query="" "MATCH(n:Product) WHERE n.name='{}' Return n.name".format(nombre)#valida que no exista el producto
    result=obtener_nombre_nodo(query)
    if len(result)==0:
        query= "" "CREATE (:Product {Sexo: $sexo, Tipo: $tipo, marca: $marca, name: $nombre})"#ingresa el producto ingresado si no existe
        session.run(query,sexo=Sexo,tipo=Tipo,marca=marca,nombre=nombre)
    else:
        print("el producto ya existe")

def ActualizarProducto(Sexo,Tipo,marca,nombre): #actualiza los datos o especificaciones de un producto existente
    query="" "MATCH(n:Product) WHERE n.name='{}' Return n.name".format(nombre)#valida que no exista el producto
    result=obtener_nombre_nodo(query)
    if len(result)!=0:
        print("Producto inexistente")
    else:   
        query="" "MATCH (p:Producto {name: $nombre}) SET p.Sexo = $sexo, p.Tipo=$tipo, p.Marca=$marca"
        session.run(query,sexo=Sexo,tipo=Tipo,marca=marca,nombre=nombre)
        print("Producto actualizado con exito")

def CrearUsuario(Nombre,Contraseña,BirthDay,Sexo):#crea usuario nuevo
    query="" "MATCH(n:User) WHERE n.name='{}' Return n.name".format(Nombre)
    result=obtener_nombre_nodo(query)
    if len(result)!=0:#verifica que no exista un usaurio con el mismo nombre
        print("Usuario existente, pruebe otro nombre")
    else:#si no existe el usuario crea el usuario
        query="" "create("+Nombre+":User {name:'"+Nombre+"',Password:'"+Contraseña+"',Sexo:'"+Sexo+"',BirthDay:'"+BirthDay+"'}) return("+Nombre+")"
        result=session.run(query)
        print("Cuenta creada con exito")

def ActualizarUsuario(Nombre,ContraseñaV,ContraseñaN):#Cambia la contraseña del usuario
    query="" "MATCH(n:User) WHERE n.name='{}' AND n.Password='{}' Return n.name".format(Nombre,ContraseñaV) #query para comparar los datos obtenidos con los de la db
    result=obtener_nombre_nodo(query)
    if len(result)==1:
        query="" "MATCH (p:User {name: $nombre}) SET p.Password = $password"
        session.run(query,nombre=Nombre,password=ContraseñaN)


def Compra(Nombre,Producto,Precio):
    #Este query crea la compra la cual se usara para recomendar futuros productos. Para esto basicamente se tendra guardado el nombre debido a que se necesita una sesión para crear 
    #una compra de igual forma el producto comprado es uno existente debido a que tiene que aparecer en la página.
    #recordar que no es una factura, al funal lo que hace es simplemente llevar un control de que productos a comprado nuestro consumidor y basado en eso va a recomendar otros productos
    query = """
    Match (u:User {name:$nombre_usuario})
    MERGE (f:Factura {producto: $producto, total: $precio})
    MERGE (u)-[:COMPRO]->(f)
    RETURN u, f
    """
    result=session.run(query,nombre_usuario=Nombre,producto=Producto,precio=Precio)
    print("Se ha realizado correctamente la compra")

#Compra("Nicola","ABC","12")
def Encuesta():
    pass



def get_product_names_for_user(Usuario):
    query = """
        MATCH (u:User {name: $user_id})-[:COMPRO]->(f:Factura)
        RETURN COLLECT(f.producto) AS productos
    """
    with driver.session() as session:
        result = session.run(query, user_id=Usuario)
        return result.single()["productos"]
    
def get_product_marca_for_compra(producto):
    query = """
        MATCH (n:Product {name:$producto})
        RETURN (n.marca) AS marca
    """
    with driver.session() as session:
        result = session.run(query, producto=producto)
        return(result.single()["marca"])
def get_product_tipo_for_compra(producto):
    query = """
        MATCH (n:Product {name:$producto})
        RETURN (n.Tipo) AS Tipo
    """
    with driver.session() as session:
        result = session.run(query, producto=producto)
        return(result.single()["Tipo"])

def get_product_sex_for_compra(producto):
    query = """
        MATCH (n:Product {name:$producto})
        RETURN (n.Sexo) AS Sexo
    """
    with driver.session() as session:
        result = session.run(query, producto=producto)
        return(result.single()["Sexo"])
    

def Precomendado(Usuario,result):#busca un producto no comprado para recomendar
    for results in result: #primero busca en la lista dada con anterioridad si 1 de los productos que complacen las caracteristicas no lo ha comprado
        query="MATCH (U:User{name:$usuario})-[COMPRO]-(f:Factura) WHERE f.producto=$producto Return f.producto AS producto"
        x=session.run(query,usuario=Usuario,producto=results)
        x=([record['producto'] for record in x])
        if len(x)==0:
            query="MATCH (U:User{name:$usuario})-[RecommendsToBuy]-(f:Product) WHERE f.name=$producto Return f.name AS producto"
            x=session.run(query,usuario=Usuario,producto=results)
            x=([record['producto'] for record in x])
            if len(x)==0:
                return(results)#en caso de encontrar un producto regresa ese producto
    query="MATCH(p:Product) Return(p.name) AS name"#si no encuentra el producto va a hacer un query sin filtro buscando cualquier producto que no este comprado
    result=session.run(query)
    result=([record['name'] for record in result])
    for results in result:
        query="MATCH (U:User{name:$usuario})-[COMPRO]-(f:Factura) WHERE f.producto=$producto Return f.producto as producto"
        x=session.run(query,usuario=Usuario,producto=results)
        x=([record["producto"] for record in x])
        if len(x)==0:#si encuentra un producto sin recomendar lo va a recomendar
            query="MATCH (U:User{name:$usuario})-[RecommendsToBuy]-(f:Product) WHERE f.name=$producto Return f.name AS producto"
            x=session.run(query,usuario=Usuario,producto=results)
            x=([record['producto'] for record in x])
            if len(x)==0:
                return(results)#en caso de encontrar un producto regresa ese producto
    #en el caso excepcional de que se haya comprado toda la tienda lo que se recomendara es un producto al azar 
    query="MATCH(p:Product) Return(p.name) AS name"
    result=session.run(query)
    result=([record['name'] for record in result])  
    return(result[randint(0,len(result)-1)])

def borrar_Recomendaciones(Usuario):
    query = """
            MATCH (u:User)-[r:RecommendsToBuy]-() WHERE u.name=$user
            DELETE r
        """
    result=session.run(query,user=Usuario)


def Crear_Recomendaciones(Usuario,precomend):
    query="""
             MATCH(u:User) WHERE u.name=$user
             MATCH(f:Product) WHERE f.name=$producto
             MERGE (u)-[:RecommendsToBuy]->(f)
    """
    session.run(query,user=Usuario,producto=precomend)

def Recomendaciones(Usuario):
    #IDEA
    #Obtener los ultimos nombres de los productos comprados (0-2)
    #Obtener la marca y el tipo de los productos comprados 
    #Buscar zapatos similares, realizando un match entre mezclando los obtenido de las ultimas compras
    #Crear una relación de recomendación de las ultimas compras y borrar las recomendaciones anteriores
    borrar_Recomendaciones(Usuario)
    nombres=get_product_names_for_user(Usuario)
    marca=[]
    tipo=[]
    sexo=[]
    if len(nombres)<3:
        rango=len(nombres)
    else:
        rango=3
    for i in range (rango):
        marca.append((get_product_marca_for_compra(nombres[i])))
        tipo.append(get_product_tipo_for_compra(nombres[i]))
        sexo.append(get_product_sex_for_compra(nombres[i]))
        """Se obtuvieron todos los datos"""
        #Inicio del fin  
    #Algoritmo simple de recomendación
    k=0#contador
    while k<4: #mientras no se hayan recomendado 3 productos va a hacer el while
        query="""MATCH(p:Product{marca:$marca,Tipo:$tipo,Sexo:$sexo}) 
            RETURN(p.name) AS name
            """  
        result=session.run(query,marca=marca[randint(0,2)],tipo=tipo[randint(0,2)],sexo=sexo[randint(0,2)]) #hace un query para recomendar un producto basado en todos los parametros al azar
        try:
            result=([record['name'] for record in result])
        except:
            query="""MATCH(p:Product{Tipo:$tipo,Sexo:$sexo}) 
                    RETURN(p.name) AS name
                    """  
            result=session.run(query,tipo=tipo[randint(0,2)],sexo=sexo[randint(0,2)])#vuelve a hacer un query pero ahora estan más filtrados los parametros para obtener un resultado
            try:
                result=([record['name'] for record in result])
            except:
                query="""MATCH(p:Product{marca:$marca,Sexo:$sexo})
                    RETURN(p.name) AS name
                    """  
                result=session.run(query,marca=marca[randint(0,2)],sexo=sexo[randint(0,2)]) #ultimo intento del query
                try:
                    result=([record['name'] for record in result])
                except:
                    pass
        recomen=Precomendado(Usuario,result) #va a revisar los productos recomendados y devolver 1 que no se encuentre en la lista de los productos ya comprados
        Crear_Recomendaciones(Usuario,recomen)
        k+=1
                
Recomendaciones("Nicola")
