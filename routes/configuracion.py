import subprocess
from flask import render_template, request, redirect, url_for

ruta_archivo_squid = '/etc/squid/squid.conf'
linea_port = 63

def configure_routes(app, conn):
    #leer cada vez que se accede a la configuracion

    @app.route('/configuracion')
    def configuracion():
        with open(ruta_archivo_squid, 'r') as archivo_configuracion:
            lineas = archivo_configuracion.readlines()
            puerto = lineas[linea_port].split()[1]

        #ver el estado de squid
        estado = subprocess.run(['sudo', 'systemctl', 'status', 'squid'], capture_output=True)
        estado = estado.stdout.decode('utf-8')
        estado = estado.split('\n')[2]
        estado = estado.split(':')[1]
        estado = estado.strip()
        estado = estado.split(' ')[0]
        return render_template('configuracion.html',
                                puerto=puerto,
                                estado=estado)

    #ruta para guardar la configuracion del puerto
    @app.route('/configurar_puerto', methods=['POST'])
    def guardar_configuracion():
        try:
            puerto = request.form['puerto']
            with open(ruta_archivo_squid, 'r+') as archivo_configuracion:
                lineas = archivo_configuracion.readlines()
                lineas[linea_port] = f'http_port {puerto}\n'
                archivo_configuracion.seek(0)
                archivo_configuracion.writelines(lineas)
                archivo_configuracion.truncate()
            # Reiniciar Squid para aplicar los cambios
            subprocess.run(['sudo', 'squid', '-k', 'reconfigure'])
            return redirect(url_for('configuracion'))
        except Exception as e:
            return f'Error al guardar la configuración: {e}'

    #ruta para apagar squid
    @app.route('/apagar_squid')
    def apagar_squid():
        subprocess.run(['sudo', 'systemctl', 'stop', 'squid'])
        return redirect(url_for('configuracion'))

    #ruta para encender squid
    @app.route('/encender_squid')
    def encender_squid():
        subprocess.run(['sudo', 'systemctl', 'start', 'squid'])
        return redirect(url_for('configuracion'))

    #ruta para reiniciar squid
    @app.route('/reiniciar_squid')
    def reiniciar_squid():
        subprocess.run(['sudo', 'systemctl', 'restart', 'squid'])
        return redirect(url_for('configuracion'))
    
     #ruta para reiniciar squid
    @app.route('/leer_squid')
    def leer_squid():
        subprocess.run(['sudo', 'squid', '-k', 'reconfigure'])
        return redirect(url_for('configuracion'))