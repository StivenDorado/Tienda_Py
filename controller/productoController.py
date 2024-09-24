from flask import Flask, request, render_template, redirect
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
import pymongo
import pymongo.errors
import os
import json
# Crear un objeto de tipo Flask
app = Flask(__name__)

app.config["UPLOAD_FOLDER"]="./Static/img"

miConexion = pymongo.MongoClient("mongodb://localhost:27017/")

baseDatos = miConexion['Tienda']
productos = baseDatos['Productos']

@app.route('/')
def inicio():
    try:
        mensaje = None
        listaProductos = list(productos.find())  # Convertimos el cursor a una lista
        if len(listaProductos) == 0:
            mensaje = "No hay productos"
    except pymongo.errors.PyMongoError as error:
        mensaje = str(error)
    return render_template('index.html', productos=listaProductos, mensaje=mensaje)

@app.route('/agregar', methods=['POST', 'GET'])
def agregar():
    mensaje = ""  # Inicializar la variable
    producto = ""
    if(request.method == 'POST'):
        try:
            producto=None
            codigo = int(request.form['txtCodigo'])
            nombre = request.form['txtNombre']
            precio = int(request.form['txtPrecio'])
            categoria = request.form['cbCategoria']
            foto = request.files['fileFoto']
            nombreArchivo = secure_filename(foto.filename)
            listaNombreArchivo = nombreArchivo.rsplit(".", 1)
            extension = listaNombreArchivo[1].lower()
            # Nombre de la foto se compone del código y la extensión
            nombreFoto = f"{codigo}.{extension}"
            producto = {
                "codigo": codigo,
                "nombre": nombre,
                "precio": precio,
                "categoria": categoria,
                "foto": nombreFoto
            }
            # Verificar si ya existe un producto con ese código
            existe = existeProducto(codigo) # Se llama a la función
            if (not existe):
                resultado = productos.insert_one(producto)
                if(resultado.acknowledged):
                    mensaje = "Producto agregado correctamente"
                    foto.save(os.path.join(app.config['UPLOAD_FOLDER'], nombreFoto))
                    return redirect('/') # Se redirecciona a la ruta raíz
                else:
                    mensaje = "Error al agregar producto"
            else:
                mensaje = "El producto ya existe con ese código"
        except pymongo.errors.PyMongoError as error:
            mensaje = (error)
            
    return render_template("frmAgregarProducto.html", mensaje=mensaje, producto=producto)

def existeProducto(codigo):
    try:
        consulta = {"codigo": codigo}
        producto = productos.find_one(consulta)
        if(producto is not None):
            return True
        else:
            return False
    except pymongo.errors as error:
        print(error)
        return False

@app.route("/consultar/<string:id>", methods=["GET"])
def consultar(id):
    if(request.method == 'GET'):
        try:
            id = ObjectId(id)
            consulta = {"_id": id}
            producto = productos.find_one(consulta)
            return render_template("frmActualizarProducto.html", producto=producto)
        except pymongo.errors as error:
            mensaje = error
        return redirect("/")
    
@app.route("/actualizar", methods=["POST"])
def actualizarProducto():
    try:
        if(request.method=="POST"):
            #recibir los valores de la vista en variables locales
            codigo=int(request.form["txtCodigo"])
            nombre=request.form["txtNombre"]
            precio=int(request.form["txtPrecio"])
            categoria=request.form["cbCategoria"]
            id=ObjectId(request.form["id"])
            #verificar si viene foto para actualizarla
            foto = request.files["fileFoto"]
            if(foto.filename!=""):
                nombreArchivo = secure_filename(foto.filename)
                listaNombreArchivo = nombreArchivo.split(".")
                extension = listaNombreArchivo[1].lower()
                nombreFoto = f"{codigo}.{extension}"
                producto = {
                    "_id": id, "codigo":codigo,"nombre":nombre,
                    "precio":precio,"categoria":categoria,"foto": nombreFoto
                }
            else:
                producto = {
                    "_id":id, "codigo":codigo, "nombre":nombre,
                    "precio":precio, "categoria":categoria
                }
            criterio = {"_id":id}
            consulta = {"$set": producto}
            #verificar si el nuevo código ya existe de un producto diferente a sí mismo
            existe = productos.find_one({"codigo": codigo, "_id":{"$ne": id}})
            if existe:
                mensaje="Producto ya existe con ese código"
                return render_template("frmActualizarProducto.html", producto=producto, mensaje=mensaje)
            else:
                resultado=productos.update_one(criterio,consulta)
                if(resultado.acknowledged):
                    mensaje="Producto Actualizado"
                    if(foto.filename!=""):
                        foto.save(os.path.join(app.config["UPLOAD_FOLDER"],nombreFoto))
                    return redirect("/")
    except pymongo.errors as error:
        mensaje=error
    return redirect("/")

@app.route("/eliminar/<string:id>", methods=["GET"])
def eliminarProducto(id):
    try:
        id = ObjectId(id)
        criterio = {"_id":id}
        producto = productos.find_one(criterio)
        resultado = productos.delete_one(criterio)
        if(resultado.acknowledged):
            mensaje = "Producto Eliminado"
            os.remove(app.config['UPLOAD_FOLDER']+"/"+producto['foto'])
        else:
            mensaje = "Producto no encontrado"
    except pymongo.errors as error:
        mensaje = str(error)
    return redirect('/')

if __name__=="__main__":
    app.run(port=8000, debug=True)