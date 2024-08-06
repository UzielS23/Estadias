import requests
import json
import datetime

def insertar(nombre, area, problema):
    url = 'http://127.0.0.1:5000/api/insert/sspdm/tblproblemas' 
    
    # Obtener la fecha y hora actual
    fecha_hora_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Crear el payload con los datos incluyendo la fecha y hora
    data = {
        "Nombre": nombre,
        "Area": area,
        "Problema": problema,
        "Fecha": fecha_hora_actual
    }
    
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=json.dumps(data), headers=headers)
        response.raise_for_status()  
        result = response.json()
        
        if "exception" in result:
            print("Error al insertar:", result["exception"])
        else:
            print("Inserción exitosa:", result)
    except requests.exceptions.RequestException as e:
        print("Error de solicitud HTTP:", e)

def insertarusos(nombre, hora, nido):
    if nombre is None:
        return
    
    url = 'http://127.0.0.1:5000/api/insert/sspdm/tblusos'
    
    # Crear el payload con los datos
    data = {
        "Nombre": nombre,
        "Hora": hora,
        "Nido": nido,
    }

    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    response.raise_for_status()  
    result = response.json()

    return result

def insertarusosFuse(nombre, hora, fusible):
    if nombre is None:
        return
    
    url = 'http://127.0.0.1:5000/api/insert/sspdm/tblusosfusibles'
    
    # Crear el payload con los datos
    data = {
        "Nombre": nombre,
        "Hora": hora,
        "Fusible": fusible
    }

    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    response.raise_for_status()  
    result = response.json()

    return result   

def insertarusosVentosa(nombre, hora, ventosa):
    if nombre is None:
        return
    
    url = 'http://127.0.0.1:5000/api/insert/sspdm/tblventosa'
    
    # Crear el payload con los datos
    data = {
        "Nombre": nombre,
        "Fecha": hora,
        "Ventosa": ventosa
    }

    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    response.raise_for_status()  
    result = response.json()

    return result      

def insertarcalibraciones(nombre, hora, robot):
    if nombre is None:
        return
    
    url = 'http://127.0.0.1:5000/api/insert/sspdm/tblcalibracion'
    
    # Crear el payload con los datos
    data = {
        "Nombre": nombre,
        "Hora": hora,
        "Robot": robot
    }

    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    response.raise_for_status()  
    result = response.json()

    return result   

def verificar(gafet):
    # Construir la URL de la API
    url = f'http://127.0.0.1:5000/api/get/usuarios/GAFET/=/{gafet}/_/=/_'
        # Realizar la solicitud GET
    response = requests.get(url)
    response.raise_for_status()

    data = response.json()
    if 'items' in data:
        return False
    else:
        return True

def obtener_nombre(gafet):
    url = f'http://127.0.0.1:5000/api/get/usuarios/GAFET/=/{gafet}/_/=/_'
    
    try:
        response = requests.get(url)
        response.raise_for_status()  
        data = response.json()

        if 'NOMBRE' in data:
            nombre_usuario = data['NOMBRE'][0] 
            return nombre_usuario
    except requests.exceptions.RequestException as e:
        # Manejar errores de solicitud HTTP
        print("Error de solicitud HTTP:", e)
    except (IndexError, KeyError) as e:
        # Manejar errores de acceso a datos JSON
        print("Error de acceso a datos JSON:", e)


def obtener_rol(gafet):
    url = f'http://127.0.0.1:5000/api/get/usuarios/GAFET/=/{gafet}/_/=/_'
    
    try:
        response = requests.get(url)
        response.raise_for_status() 
        
        data = response.json()
        
        if 'TIPO' in data:
            TIPO = data['TIPO'][0]
            return TIPO
    except requests.exceptions.RequestException as e:
        # Manejar errores de solicitud HTTP
        print("Error de solicitud HTTP:", e)
    except (IndexError, KeyError) as e:
        # Manejar errores de acceso a datos JSON
        print("Error de acceso a datos JSON:", e)

def obtener_problemas_desde_bd():
    url = 'http://127.0.0.1:5000/api/get/sspdm/tblproblemas/all/all/_/_/_/_'
    
    try:
        response = requests.get(url)
        response.raise_for_status()  
        data = response.json()

        if 'Problema' in data:
            problemas = []
            for i in range(len(data['Problema'])):
                problema = {
                    'ID': data['ID'][i],  # Añadimos el ID del problema
                    'Fecha': data['Fecha'][i],  # Añadimos la Fecha del problema
                    'Problema': data['Problema'][i],
                    'Nombre': data['Nombre'][i],
                    'Area': data['Area'][i]
                }
                problemas.append(problema)
            return problemas
        else:
            return []
    except requests.exceptions.RequestException as e:
        print("Error de solicitud HTTP:", e)
        return []
    except (IndexError, KeyError) as e:
        print("Error de acceso a datos JSON:", e)
        return []
    
def eliminar_problema(id):
    url = f'http://127.0.0.1:5000/api/delete/sspdm/tblproblemas/{id}'
    
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers)
        response.raise_for_status()  
        result = response.json()

        if "exception" in result:
            print("Error al eliminar:", result["exception"])
        else:
            print("Eliminación exitosa:", result)
    except requests.exceptions.RequestException as e:
        print("Error de solicitud HTTP:", e)

def obtenertblventosa():
    url = 'http://127.0.0.1:5000/api/get/sspdm/tblventosa/all/all/_/_/_/_'
    
    try:
        response = requests.get(url)
        response.raise_for_status()  
        data = response.json()

        if 'Ventosa' in data:
            ventosas = []
            for i in range(len(data['Ventosa'])):
                ventosa = {
                    'ID': data['ID'][i],  # Añadimos el ID del ventosa
                    'Nombre': data['Nombre'][i],  # Añadimos la Fecha del ventosa
                    'Fecha': data['Fecha'][i],
                    'Ventosa': data['Ventosa'][i],
                }
                ventosas.append(ventosa)
            return ventosas
        else:
            return []
    except requests.exceptions.RequestException as e:
        print("Error de solicitud HTTP:", e)
        return []
    except (IndexError, KeyError) as e:
        print("Error de acceso a datos JSON:", e)
        return []
    
def obtener_fusibles():
    url = 'http://127.0.0.1:5000/api/get/sspdm/tblusosfusibles/all/all/_/_/_/_'
    
    try:
        response = requests.get(url)
        response.raise_for_status()  
        data = response.json()

        if 'Fusible' in data:
            fusibles = []
            for i in range(len(data['Fusible'])):
                fusible = {
                    'ID': data['ID'][i],  # Añadimos el ID del fusible
                    'Nombre': data['Nombre'][i],  # Añadimos la Fecha del fusible
                    'Hora': data['Hora'][i],
                    'Fusible': data['Fusible'][i],
                }
                fusibles.append(fusible)
            return fusibles
        else:
            return []
    except requests.exceptions.RequestException as e:
        print("Error de solicitud HTTP:", e)
        return []
    except (IndexError, KeyError) as e:
        print("Error de acceso a datos JSON:", e)
        return []