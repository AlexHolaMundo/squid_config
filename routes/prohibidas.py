import subprocess
from flask import render_template, request, redirect, url_for

#ruta_archivo = '/etc/squid/dominios_prohibidos'
ruta_archivo = '/etc/squid/dominios_prohibidos'
ruta_archivo_squid = '/etc/squid/squid.conf'
linea_acl_filtro_prohibidas = 23
linea_acl_filtro_admitidas = 24
linea_http_filtro_prohibidas = 49
linea_http_filtro_admitidas = 50

# Ruta para mostrar las páginas prohibidas
def configure_routes(app, conn):
    @app.route('/paginas_prohibidas')
    def paginas_prohibidas():
        cur = conn.cursor()
        cur.execute("SELECT * FROM PaginasProhibidas")
        datos = cur.fetchall()
        print(datos)
        cur.close()
        return render_template('pgProhibidas.html', paginas_prohibidas=datos)

    # Ruta para guardar un nuevo usuario en la base de datos
    @app.route('/guardar_pgProhibidas', methods=['POST'])
    def guardar_pgProhibidas():
        try:
            nombre_pgp = request.form['nombre_pgp']
            razon_pgp = request.form['razon_pgp']
            categoria_pgp = request.form["categoria_pgp"]
            dominio_pgp = request.form['dominio_pgp']
            cursor = conn.cursor()
            cursor.execute("INSERT INTO PaginasProhibidas (nombre_pgp, razon_pgp, categoria_pgp, dominio_pgp ) VALUES (%s, %s, %s, %s)", (nombre_pgp, razon_pgp, categoria_pgp, dominio_pgp))  # Corregido aquí
            conn.commit()

            # Agregar el sitio prohibido al archivo
            guardar_dominio =  f''' .{dominio_pgp}'''

            with open(ruta_archivo, 'a') as archivo:
                archivo.write(guardar_dominio)

            # Agregar la nueva ACL al archivo de configuración de Squid
            with open(ruta_archivo_squid, 'r+') as archivo_configuracion:
                lineas = archivo_configuracion.readlines()

                if len(lineas) >= 2:
                    lineas[linea_acl_filtro_prohibidas] = f'''acl filtro_prohibidos dstdomain '/etc/squid/dominios_prohibidos'\n'''
                    lineas[linea_http_filtro_prohibidas] = f'''http_access deny filtro_prohibidos\n'''
                archivo_configuracion.seek(0)
                archivo_configuracion.writelines(lineas)
                archivo_configuracion.truncate()

            # Reiniciar Squid para aplicar los cambios
            subprocess.run(['sudo', 'squid', '-k', 'reconfigure'])

            return redirect('paginas_prohibidas')
        except Exception as e:
            return f'Error al registrar la pagina: {e}'
        
    @app.route('/eliminar_pgp/<int:id>', methods=['POST'])
    def eliminar_pgp(id):
        cur = conn.cursor()
        cur.execute("DELETE FROM PaginasProhibidas WHERE id_pgp = %s", (id,))
        conn.commit()
        cur.close()

         
        cur.execute("SELECT * FROM PaginasProhibidas WHERE id_pgp = %s", (id,))
        paginas_prohibida = cur.fetchone()  # fetchone() para obtener solo un registro
        cur.close()

        
    
    

