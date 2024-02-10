import itertools
import os
from flask import Flask, render_template, request, redirect, url_for, session
import folium
import mysql.connector
from folium.plugins import *
from itertools import permutations
from geopy.distance import great_circle
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Cambia esto por tu propia clave secreta
'''
Configuracion de la base de datos
'''
# Configuración de la conexión a la base de datos
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'carlos18',
    'database': 'Logistica'
}





'''
inicio de sesion
'''
# Función para verificar las credenciales de inicio de sesión
def verificar_credenciales(nombre_usuario, password):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Consulta para obtener la contraseña del usuario
        query = "SELECT id, usuario, password FROM usuarios WHERE usuario = %s"
        cursor.execute(query, (nombre_usuario,))
        result = cursor.fetchone()

        # Verificar la contraseña
        if result and result[2] == password:
            return result[1]  # Devuelve el nombre de usuario si las credenciales son válidas
        else:
            return None
    except mysql.connector.Error as error:
        print("Error al consultar la base de datos:", error)
        return None
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
@app.route('/')
def index():
    return render_template('index.html')
# Endpoint para el inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        password = request.form['password']

        usuario_valido = verificar_credenciales(nombre_usuario, password)
        if usuario_valido:
            # Iniciar sesión del usuario
            session['nombre_usuario'] = usuario_valido
            return redirect(url_for('inicio'))
        else:
            return 'Credenciales inválidas', 401
    else:
        return render_template('login.html')

@app.route('/inicio')
def inicio():
    # Obtener el nombre de usuario de la sesión
    nombre_usuario = session.get('nombre_usuario')
    pagos=contarPagos()
    galvanizado=contarGalvanizado()
    requi = contarRequi()
    entregas= contarEntre()
    users = contarUser()
    if nombre_usuario:
        return render_template('inicio.html', nombre_usuario=nombre_usuario, pagos=pagos, galvanizado=galvanizado, requi=requi, entregas=entregas, users=users)
    else:
        return 'Acceso no autorizado', 401
    
    

'''
Optimizador de rutas

'''

def calcular_distancia_total(ruta, ubicaciones):
    distancia_total = 0
    for i in range(len(ruta) - 1):
        punto_actual = ubicaciones[ruta[i]]
        punto_siguiente = ubicaciones[ruta[i + 1]]
        distancia_total += great_circle((punto_actual['latitud'], punto_actual['longitud']),
                                        (punto_siguiente['latitud'], punto_siguiente['longitud'])).kilometers
    return distancia_total

def encontrar_ruta_optima(ubicaciones):
    mejor_distancia = float('inf')
    mejor_ruta = []
    for ruta_permutada in itertools.permutations(range(len(ubicaciones))):
        distancia = calcular_distancia_total(ruta_permutada, ubicaciones)
        if distancia < mejor_distancia:
            mejor_distancia = distancia
            mejor_ruta = ruta_permutada
    return mejor_ruta

@app.route('/mapa-entregas')
def mapa_entregas():
    nombre_usuario = session.get('nombre_usuario')
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT latitud, longitud FROM solicitudes_entregas')
    ubicaciones_entregas = cursor.fetchall()
    ruta_optima_entregas = encontrar_ruta_optima(ubicaciones_entregas)
    ruta_coords_entregas = [[ubicaciones_entregas[i]['latitud'], ubicaciones_entregas[i]['longitud']] for i in ruta_optima_entregas]
    m = folium.Map(location=[ruta_coords_entregas[0][0], ruta_coords_entregas[0][1]], zoom_start=12)
    folium.PolyLine(locations=ruta_coords_entregas, color='blue').add_to(m)
    return render_template('mapa-entrega.html', mapa_entregas=m._repr_html_(), nombre_usuario=nombre_usuario)

@app.route('/mapa-recolecciones')
def mapa_recolecciones():
    nombre_usuario = session.get('nombre_usuario')
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT latitud, longitud FROM vitacora_galvanizado')
    ubicaciones_recolecciones = cursor.fetchall()
    ruta_optima_recolecciones = encontrar_ruta_optima(ubicaciones_recolecciones)
    ruta_coords_recolecciones = [[ubicaciones_recolecciones[i]['latitud'], ubicaciones_recolecciones[i]['longitud']] for i in ruta_optima_recolecciones]
    m = folium.Map(location=[ruta_coords_recolecciones[0][0], ruta_coords_recolecciones[0][1]], zoom_start=12)
    folium.PolyLine(locations=ruta_coords_recolecciones, color='red').add_to(m)
    return render_template('mapa-recoleccion.html', mapa_recolecciones=m._repr_html_(), nombre_usuario=nombre_usuario) 



'''
Manejo de pagos
'''

# Ruta para ver todos los pagos
@app.route('/ver-pago')
def ver_pagos():
    nombre_usuario = session.get('nombre_usuario')
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM pagos")
    pagos = cursor.fetchall()
    cursor.close()
    return render_template('ver-pagos.html', pagos=pagos, nombre_usuario=nombre_usuario)

@app.route('/crear_pago', methods=['GET', 'POST'])
def crear_pago():
    nombre_usuario = session.get('nombre_usuario')
    if request.method == 'POST':
        nombre_archivo = request.form['nombre_archivo']
        descripcion = request.form['descripcion']
        
        # Guardar el archivo en la carpeta static
        archivo = request.files['archivo']
        if archivo:
            filename = secure_filename(archivo.filename)
            archivo.save(os.path.join(app.root_path, 'static', filename))

        # Guardar los datos en la base de datos
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO pagos (nombre_archivo, descripcion) VALUES (%s, %s)", (nombre_archivo, descripcion))
        connection.commit()  # <-- Corregido
        cursor.close()
        
        return redirect(url_for('ver_pagos'))
    return render_template('crear-pago.html', nombre_usuario=nombre_usuario)  # <-- Corregido


# Ruta para editar un pago existente
@app.route('/editar_pago/<int:id>', methods=['GET', 'POST'])
def editar_pago(id):
    nombre_usuario = session.get('nombre_usuario')
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    if request.method == 'POST':
        nombre_archivo = request.form['nombre_archivo']
        descripcion = request.form['descripcion']
        cursor.execute("UPDATE pagos SET nombre_archivo = %s, descripcion = %s WHERE id = %s", (nombre_archivo, descripcion, id))
        connection.commit()  # <-- Corregido
        cursor.close()
        return redirect(url_for('ver_pagos'))
    cursor.execute("SELECT * FROM pagos WHERE id = %s", (id,))
    pago = cursor.fetchone()
    cursor.close()
    return render_template('editar-pago.html', pago=pago, nombre_usuario=nombre_usuario)  # <-- Corregido


# Ruta para eliminar un pago
@app.route('/eliminar_pago/<int:id>')
def eliminar_pago(id):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM pagos WHERE id = %s", (id,))
    connection.commit()  # <-- Corregido
    cursor.close()
    return redirect(url_for('ver_pagos'))



'''
solicitudes de entrega
'''

# Ruta para ver todas las solicitudes de entrega
@app.route('/solicitudes_entrega')
def ver_solicitudes_entrega():
    nombre_usuario = session.get('nombre_usuario')
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM solicitudes_entregas")
    solicitudes = cursor.fetchall()
    cursor.close()
    return render_template('ver-solicitudes.html', solicitudes=solicitudes, nombre_usuario=nombre_usuario)

# Ruta para crear una nueva solicitud de entrega
@app.route('/solicitudes_entrega/crear', methods=['GET', 'POST'])
def crear_solicitud_entrega():
    nombre_usuario = session.get('nombre_usuario')
    if request.method == 'POST':
        # Obtener los datos del formulario
        fecha_solicitada = request.form['fecha_solicitada']
        fecha_entrega = request.form['fecha_entrega']
        material_a = request.form['material_a']
        folio = request.form['folio']
        material = request.form['material']
        cantidad = request.form['cantidad']
        obra = request.form['obra']
        estatus = request.form['estatus']
        entregada = request.form['entregada']
        restante = request.form['restante']
        remision = request.form['remision']
        latitud = request.form['latitud']
        longitud = request.form['longitud']
        
        # Insertar la nueva solicitud en la base de datos
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO solicitudes_entregas (fecha_solicitada, fecha_entrega, material_a, folio, material, cantidad, obra, estatus, entregada, restante, remision, latitud, longitud) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (fecha_solicitada, fecha_entrega, material_a, folio, material, cantidad, obra, estatus, entregada, restante, remision, latitud, longitud))
        connection.commit()
        cursor.close()
        
        return redirect(url_for('ver_solicitudes_entrega'))
    return render_template('crear-solicitud.html', nombre_usuario=nombre_usuario)

# Ruta para modificar una solicitud de entrega
@app.route('/solicitudes_entrega/modificar/<int:id>', methods=['GET', 'POST'])
def modificar_solicitud_entrega(id):
    nombre_usuario = session.get('nombre_usuario')
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)  # Obtener resultados como diccionarios
    if request.method == 'POST':
        # Obtener los datos del formulario y actualizar la solicitud en la base de datos
        fecha_solicitada = request.form['fecha_solicitada']
        fecha_entrega = request.form['fecha_entrega']
        material_a = request.form['material_a']
        folio = request.form['folio']
        material = request.form['material']
        cantidad = request.form['cantidad']
        obra = request.form['obra']
        estatus = request.form['estatus']
        entregada = request.form['entregada']
        restante = request.form['restante']
        remision = request.form['remision']
        latitud = request.form['latitud']
        longitud = request.form['longitud']

        cursor.execute("""
            UPDATE solicitudes_entregas 
            SET fecha_solicitada = %s, fecha_entrega = %s, material_a = %s, folio = %s, material = %s, cantidad = %s, 
            obra = %s, estatus = %s, entregada = %s, restante = %s, remision = %s, latitud = %s, longitud = %s 
            WHERE id = %s
        """, (fecha_solicitada, fecha_entrega, material_a, folio, material, cantidad, obra, estatus, entregada, restante, remision, latitud, longitud, id))
        
        connection.commit()
        cursor.close()
        return redirect(url_for('ver_solicitudes_entrega'))

    cursor.execute("SELECT * FROM solicitudes_entregas WHERE id = %s", (id,))
    solicitud = cursor.fetchone()
    cursor.close()
    return render_template('modificar-solicitud.html', solicitud=solicitud, nombre_usuario=nombre_usuario)


# Ruta para eliminar una solicitud de entrega
@app.route('/solicitudes_entrega/eliminar/<int:id>')
def eliminar_solicitud_entrega(id):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM solicitudes_entregas WHERE id = %s", (id,))
    connection.commit()
    cursor.close()
    return redirect(url_for('ver_solicitudes_entrega'))






'''
galvanizado
'''
@app.route('/vitacora_galvanizado')
def get_vitacora_galvanizado():
    nombre_usuario = session.get('nombre_usuario')
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM vitacora_galvanizado")
    vitacora = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('galvanizado.html', vitacora=vitacora, nombre_usuario=nombre_usuario)



# Ruta para crear una nueva entrada en la tabla vitacora_galvanizado
@app.route('/vitacora_galvanizado/crear', methods=['GET', 'POST'])
def crear_vitacora_galvanizado():
    nombre_usuario = session.get('nombre_usuario')
    if request.method == 'POST':
        np = request.form['np']
        fecha = request.form['fecha']
        remision = request.form['remision']
        orden_de_t = request.form['orden_de_t']
        folio = request.form['folio']
        viaticos = request.form['viaticos']
        cert_calidad = request.form['cert_calidad']
        cumple = request.form['cumple']
        factura = request.form['factura']
        folio_factura = request.form['folio_factura']
        producto = request.form['producto']
        cantidad = request.form['cantidad']
        parcialidad_recolectada = request.form['parcialidad_recolectada']
        recoleccion = request.form['recoleccion']
        peso = request.form['peso']
        costo = request.form['costo']
        estatus = request.form['estatus']
        nombre_empresa = request.form['nombre_empresa']
        latitud = request.form['latitud']
        longitud = request.form['longitud']

        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO vitacora_galvanizado (np, fecha, remision, orden_de_t, folio, viaticos, cert_calidad, cumple, factura, folio_factura, producto, cantidad, parcialidad_recolectada, recoleccion, peso, costo, estatus, nombre_empresa, latitud, longitud) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (np, fecha, remision, orden_de_t, folio, viaticos, cert_calidad, cumple, factura, folio_factura, producto, cantidad, parcialidad_recolectada, recoleccion, peso, costo, estatus, nombre_empresa, latitud, longitud))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('get_vitacora_galvanizado'))
    return render_template('crear_vitacora_galvanizado.html', nombre_usuario=nombre_usuario)


@app.route('/vitacora_galvanizado/modificar/<int:id>', methods=['GET', 'POST'])
def modificar_vitacora_galvanizado(id):
    nombre_usuario = session.get('nombre_usuario')
    if request.method == 'POST':
        np = request.form['np']
        fecha = request.form['fecha']
        remision = request.form['remision']
        orden_de_t = request.form['orden_de_t']
        folio = request.form['folio']
        viaticos = request.form['viaticos']
        cert_calidad = request.form['cert_calidad']
        cumple = request.form['cumple']
        factura = request.form['factura']
        folio_factura = request.form['folio_factura']
        producto = request.form['producto']
        cantidad = request.form['cantidad']
        parcialidad_recolectada = request.form['parcialidad_recolectada']
        recoleccion = request.form['recoleccion']
        peso = request.form['peso']
        costo = request.form['costo']
        estatus = request.form['estatus']
        nombre_empresa = request.form['nombre_empresa']
        latitud = request.form['latitud']
        longitud = request.form['longitud']

        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("UPDATE vitacora_galvanizado SET np=%s, fecha=%s, remision=%s, orden_de_t=%s, folio=%s, viaticos=%s, cert_calidad=%s, cumple=%s, factura=%s, folio_factura=%s, producto=%s, cantidad=%s, parcialidad_recolectada=%s, recoleccion=%s, peso=%s, costo=%s, estatus=%s, nombre_empresa=%s, latitud=%s, longitud=%s WHERE id=%s", (np, fecha, remision, orden_de_t, folio, viaticos, cert_calidad, cumple, factura, folio_factura, producto, cantidad, parcialidad_recolectada, recoleccion, peso, costo, estatus, nombre_empresa, latitud, longitud, id))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('get_vitacora_galvanizado'))
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM vitacora_galvanizado WHERE id=%s", (id,))
    vitacora = cursor.fetchone()
    cursor.close()
    connection.close()
    return render_template('modificar_vitacora_galvanizado.html', vitacora=vitacora, nombre_usuario=nombre_usuario)

@app.route('/vitacora_galvanizado/eliminar/<int:id>', methods=['POST'])
def eliminar_vitacora_galvanizado(id):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM vitacora_galvanizado WHERE id=%s", (id,))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('get_vitacora_galvanizado'))

'''
Requisisciones
'''

# Ruta para ver todas las requisiciones
@app.route('/requisiciones', methods=['GET'])
def ver_requisiciones():
    nombre_usuario = session.get('nombre_usuario')
        
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Requisiciones")
    requisiciones = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('requi.html', requisiciones=requisiciones, nombre_usuario=nombre_usuario)

    
# Ruta para procesar el formulario de creación de una nueva requisición
@app.route('/requisiciones/crear', methods=['POST', 'GET'])
def crear_requisicion():
    nombre_usuario = session.get('nombre_usuario')
    if request.method == 'POST':
        # Obtener los datos del formulario
        descripcion = request.form.get('descripcion')
        id_area = request.form.get('id_area')
        estado = request.form.get('estado')

        if not descripcion or not id_area or not estado:
            # Mostrar un mensaje de error si algún campo está vacío
            error_message = "Todos los campos son obligatorios."
            return render_template('error.html', error=error_message)

        # Establecer conexión con la base de datos
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Insertar la nueva requisición en la base de datos
        cursor.execute("INSERT INTO Requisiciones (Descripcion, ID_Area, Estado) VALUES (%s, %s, %s)", (descripcion, id_area, estado))
        connection.commit()

        # Cerrar conexión
        cursor.close()
        connection.close()

        # Redirigir a la página de ver requisiciones
        return redirect(url_for('ver_requisiciones'))

    # Renderizar el formulario de creación si la solicitud no es POST
    return render_template('crear-requi.html', nombre_usuario=nombre_usuario)


    
# Ruta para procesar el formulario de edición de una requisición
# Ruta para editar una requisición existente
@app.route('/requisiciones/<int:id_requisicion>/editar', methods=['GET', 'POST'])
def editar_requisicion(id_requisicion):
    nombre_usuario = session.get('nombre_usuario')
    if request.method == 'POST':
        try:
            # Obtener los datos del formulario
            descripcion = request.form['descripcion']
            id_area = int(request.form['id_area'])  # Asegúrate de que id_area sea un número entero
            estado = request.form['estado']

            # Establecer conexión con la base de datos
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()

            # Verificar si la requisición existe antes de intentar actualizarla
            cursor.execute("SELECT * FROM Requisiciones WHERE ID_Requisicion = %s", (id_requisicion,))
            requisicion = cursor.fetchone()
            if requisicion is None:
                # Si la requisición no existe, mostrar un mensaje de error o redirigir a una página de error
                return f'error'

            # Actualizar la requisición en la base de datos
            cursor.execute("UPDATE Requisiciones SET Descripcion=%s, ID_Area=%s, Estado=%s WHERE ID_Requisicion=%s", (descripcion, id_area, estado, id_requisicion))
            connection.commit()

            # Cerrar conexión y redirigir a la página de ver requisiciones
            cursor.close()
            connection.close()
            return redirect(url_for('ver_requisiciones'))
        except Exception as e:
            # Mostrar página de error en caso de excepción
            return f'error'
    else:
        try:
            # Obtener la requisición a editar de la base de datos
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM Requisiciones WHERE ID_Requisicion = %s", (id_requisicion,))
            requisicion = cursor.fetchone()
            cursor.close()
            connection.close()

            if requisicion is None:
                # Si la requisición no existe, mostrar un mensaje de error o redirigir a una página de error
                return f'error'

            # Renderizar el formulario de edición con los datos de la requisición
            return render_template('editar-requi.html', requisicion=requisicion, nombre_usuario=nombre_usuario)
        except Exception as e:
            # Mostrar página de error en caso de excepción
            return f'error'

    
# Ruta para eliminar una requisición existente
@app.route('/requisiciones/<int:id_requisicion>/eliminar', methods=['POST'])
def eliminar_requisicion(id_requisicion):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("DELETE FROM Requisiciones WHERE ID_Requisicion=%s", (id_requisicion,))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('ver_requisiciones'))
    except Exception as e:
        return render_template('error.html', error=str(e))


def contarPagos():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM pagos"

        # Ejecutar la consulta SQL
    cursor.execute(query)

        # Obtener el resultado de la consulta
    count = cursor.fetchone()[0]

        # Cerrar el cursor y la conexión
    cursor.close()
    connection.close()

        # Devolver el número de registros contados
    return count
def contarGalvanizado():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM vitacora_galvanizado"

        # Ejecutar la consulta SQL
    cursor.execute(query)

        # Obtener el resultado de la consulta
    count = cursor.fetchone()[0]

        # Cerrar el cursor y la conexión
    cursor.close()
    connection.close()
    

        # Devolver el número de registros contados
    return count
def contarRequi():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM Requisiciones"

        # Ejecutar la consulta SQL
    cursor.execute(query)

        # Obtener el resultado de la consu
    count = cursor.fetchone()[0]

        # Cerrar el cursor y la conexión
    cursor.close()
    connection.close()
    return count
def contarEntre():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM solicitudes_entregas"

        # Ejecutar la consulta SQL
    cursor.execute(query)

        # Obtener el resultado de la consulta
    count = cursor.fetchone()[0]

        # Cerrar el cursor y la conexión
    cursor.close()
    connection.close()
    return count
def contarUser():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM usuarios"

        # Ejecutar la consulta SQL
    cursor.execute(query)

        # Obtener el resultado de la consulta
    count = cursor.fetchone()[0]

        # Cerrar el cursor y la conexión
    cursor.close()
    connection.close()
    return count
'''
Cierre de sesion
'''
@app.route('/logout')
def logout():
    # Cerrar sesión del usuario eliminando la información de la sesión
    session.pop('nombre_usuario', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
