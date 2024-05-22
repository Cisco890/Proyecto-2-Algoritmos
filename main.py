import os
import json 
from flask import Flask, g,Response, request
from neo4j import GraphDatabase, basic_auth

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
    if len(result)!=0:
        query= "" "CREATE (:Producto {Sexo: $sexo, Tipo: $tipo, Marca: $marca, name: $nombre})"#ingresa el producto ingresado si no existe
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


def Compra():
    pass

def Encuesta():
    pass

    

def Recomendaciones():
    pass
