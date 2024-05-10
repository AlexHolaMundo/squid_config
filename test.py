# Abre el archivo de configuración
with open('squid.conf', 'r') as file:
    lines = file.readlines()

# Encuentra la línea que contiene el texto buscado
for i, line in enumerate(lines):
    if "#CONFIGURACION DE ACLS" in line:
        line_index = i
        break

# Inserta tu texto debajo de la línea encontrada
nuevo_texto = "Tu nuevo texto aquí\n"

lines.insert(line_index + 1, nuevo_texto)

# Reescribe el archivo con el texto añadido
with open('tu_archivo_de_configuracion.conf', 'w') as file:
    file.writelines(lines)
