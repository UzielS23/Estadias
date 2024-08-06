from flask import Flask, render_template, request
import requests
import pandas as pd
import json

app = Flask(__name__)

API_URL = 'http://127.0.0.1:5000/api/get/'
DB_NAME = 'eiaf_3'

def obtener_datos(start_date, end_date):
    url = f"{API_URL}{DB_NAME}/historial/FIN/>=/{start_date.replace(' ', '%20')}/FIN/<=/{end_date.replace(' ', '%20')}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lanza una excepción si la solicitud no es exitosa
        
        data = response.json()
        reintentos = data.get('REINTENTOS', [])
        fusibles = data.get('FUSIBLES', [])
        
        # Convertir las cadenas JSON a diccionarios
        datos = [{'reintentos': json.loads(reintento), 'fusibles': json.loads(fusible)} for reintento, fusible in zip(reintentos, fusibles)]
        return datos
    except requests.exceptions.RequestException as e:
        # Manejar errores de solicitud HTTP
        print("Error de solicitud HTTP:", e)
        return []
    except (IndexError, KeyError) as e:
        # Manejar errores de acceso a datos JSON
        print("Error de acceso a datos JSON:", e)
        return []

@app.route('/estadisticas')
def index():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    datos = []
    if start_date and end_date:
        datos = obtener_datos(start_date, end_date)
    
    # Inicializar contadores para cada tabla
    tablas = {
        "PDC-D": {},
        "PDC-RMID": {},
        "PDC-P": {},
        "PDC-S": {},
        "PDC-R": {},
        "TBLU": {}
    }
    
    totales = {key: 0 for key in tablas.keys()}  # Inicializar totales

    # Procesar cada entrada de datos excluyendo "RELX"
    for dato in datos:
        reintentos = dato['reintentos']
        fusibles = dato['fusibles']
        for tabla, cavidades in reintentos.items():
            if tabla in tablas:
                for cavidad, conteo in cavidades.items():
                    if cavidad != "RELX" and cavidad in fusibles[tabla]:
                        fusible = fusibles[tabla][cavidad]
                        if fusible != "empty":
                            clave = f"{cavidad} ({fusible})"
                            if clave in tablas[tabla]:
                                tablas[tabla][clave] += conteo
                            else:
                                tablas[tabla][clave] = conteo
                            totales[tabla] += conteo  # Sumar el conteo al total de la tabla

    # Obtener los 5 elementos que más fallan por cada tabla
    top5_por_tabla = {
        tabla: pd.DataFrame(sorted(cavidades.items(), key=lambda item: item[1], reverse=True)[:5], columns=['Cavidad (Fusible)', 'Conteo'])
        for tabla, cavidades in tablas.items()
    }

    # Obtener los 5 elementos que más fallan en general
    total_fallas = {}
    for cavidades in tablas.values():
        for clave, conteo in cavidades.items():
            if clave in total_fallas:
                total_fallas[clave] += conteo
            else:
                total_fallas[clave] = conteo

    top5_general = pd.DataFrame(sorted(total_fallas.items(), key=lambda item: item[1], reverse=True)[:5], columns=['Cavidad (Fusible)', 'Conteo'])

    # Convertir todos los datos a un formato adecuado para renderizar en HTML
    tablas_html = {tabla: pd.DataFrame(list(cavidades.items()), columns=['Cavidad (Fusible)', 'Conteo']) for tabla, cavidades in tablas.items()}

    return render_template('estadisticasFUSE.html', tablas=tablas_html, top5_por_tabla=top5_por_tabla, top5_general=top5_general, totales=totales)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
