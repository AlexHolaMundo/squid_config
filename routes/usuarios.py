from flask import Flask, render_template, request

# Ruta para mostrar el formulario de usuarios
def configure_routes(app, conn):
    # Ruta para mostrar el formulario de usuarios
    @app.route('/usuarios')
    def usuarios():
        # Obtener la lista de departamentos desde la base de datos
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_dep, nombre_dep FROM Departamentos")
        departamentos = cursor.fetchall()
        cursor.close()
        # Pasar la lista de departamentos al contexto de la plantilla
        return render_template('usuarios.html', departamentos=departamentos)

    # Ruta para guardar un nuevo usuario en la base de datos
    @app.route('/guardar_usuario', methods=['POST'])
    def guardar_usuario():
        try:
            nombre_usu = request.form['nombre_usu']
            password_usu = request.form['password_usu']
            departamento = request.form["departamento"]  # Corregido aquí
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Usuarios (nombre_usu, password_usu, fkid_dep) VALUES (%s, %s, %s)", (nombre_usu, password_usu, departamento))  # Corregido aquí
            conn.commit()
            return 'Usuario guardado correctamente'
        except Exception as e:
            return f'Error al registrar el usuario: {e}'
