from flask import Flask
import pymongo
# Crear un objeto de tipo Flask
app = Flask(__name__)

app.config["UPLOAD_FOLDER"]="./Static/img"

miConexion = pymongo.MongoClient("mongodb://localhost:27017/")

# Crear una base de datos
baseDatos = miConexion['Tienda']
#  Crear una colección Productos
productos = baseDatos['Productos']
# Crear una colección Usuarios
usuarios = baseDatos['Usuarios']

if __name__=="__main__":
    from controller.productoController import *
    app.run(port=8000, debug=True)