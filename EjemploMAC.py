from librouteros import connect

try:
    username = input("Ingrese el nombre de usuario: ")
    password = input("Ingrese la contraseña: ")
    host = input("Ingrese la dirección IP del dispositivo MikroTik: ")

    # Establecer conexión con el dispositivo MikroTik
    connection = connect(username=username, password=password, host=host, port=8728)

    command = "/interface/ethernet/print"

    # Enviar el comando ingresado al dispositivo MikroTik y obtener la respuesta
    response_generator = connection(cmd=command)

    # Imprimir la respuesta del dispositivo en forma de generador
    print("Respuesta del dispositivo MikroTik:")
    for item in response_generator:
        print(item)

finally:
    # Cerrar la conexión
    connection.close()
