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
    print(result)

User="Juan"
Password="Hola "
def ValidadorLogin(User,Password):
    pass
