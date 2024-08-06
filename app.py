from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from functools import wraps
from datetime import timedelta, datetime
import threading
import time
import json 
import paho.mqtt.client as mqtt
import requests
import pandas as pd
import re
from CoordsPDC_R import iniciar_proceso_R, detener_proceso_R, procesar_imagenes_R
from CoordsPDC_D import iniciar_proceso_D, detener_proceso_D, procesar_imagenes_D
from CoordsPDC_P import iniciar_proceso_P, detener_proceso_P, procesar_imagenes_P
from CoordsPDC_S import iniciar_proceso_S, detener_proceso_S, procesar_imagenes_S
from CoordsTBLU import iniciar_proceso_TB, detener_proceso_TB, procesar_imagenes_TB
from BD import insertar, verificar, obtener_nombre, obtener_rol, insertarusos, insertarusosFuse, obtener_problemas_desde_bd, eliminar_problema,insertarusosVentosa, obtenertblventosa, obtener_fusibles, insertarcalibraciones


app = Flask(__name__)
app.config['SECRET_KEY'] = 'wa4325ws&$/&$agjhag65$'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)
mqtt_client = mqtt.Client()
mqtt_broker = '127.0.0.1'
mqtt_port = 1883
mqtt_topic = 'PLC/1'
mqtt_receiveTopic = '#'
nombre_usuario = None
estado = ''
p1 = ''
p2 = ''
p3 = ''
mnsj = ''
mostrar = ''
x = 1
redirect_needed = False 
last_processed_time = None
last_message = None

def on_message(mqtt_client, userdata, message):
    global nombre_usuario, x, redirect_needed, last_processed_time, last_message, y, estado, mostrar
    msg = message.payload.decode("utf-8")
    
    # Check for duplicate messages
    current_time = time.time()
    if last_message == msg and (last_processed_time is None or current_time - last_processed_time < 1):
        return  

    last_message = msg
    last_processed_time = current_time

    if msg == '{"PDC-R_ERROR": true}' or msg == '{"clamp_PDC-R": true}':
        x = 0
        redirect_needed = True
        y = "PDC-R"
        insertarusos(nombre=nombre_usuario, hora=datetime.now().isoformat(), nido=y)
    elif msg == '{"PDC-D_ERROR": true}' or msg == '{"clamp_PDC-D": true}':
        x = 0
        redirect_needed = True
        y = "PDC-D"
        insertarusos(nombre=nombre_usuario, hora=datetime.now().isoformat(), nido=y)
    elif msg == '{"PDC-S_ERROR": true}' or msg == '{"clamp_PDC-S": true}':
        x = 0
        redirect_needed = True 
        y = "PDC-S"
        insertarusos(nombre=nombre_usuario, hora=datetime.now().isoformat(), nido=y)
    elif msg == '{"PDC-P_ERROR": true}' or msg == '{"clamp_PDC-P": true}':
        x = 0
        redirect_needed = True 
        y = "PDC-P"
        insertarusos(nombre=nombre_usuario, hora=datetime.now().isoformat(), nido=y)
    elif msg == '{"TBLU_ERROR": true}' or msg == '{"clamp_TBLU": true}':
        x = 0
        redirect_needed = True 
        y = "TBLU"
        insertarusos(nombre=nombre_usuario, hora=datetime.now().isoformat(), nido=y)
    elif msg == '{"response" : "El cilindro esta Funcionando bien\r\n"}':
        estado = 'Cilindro funcionando correctamente'
        mostrar = 'si'
    elif msg == '{"response" : "El cilindro esta fallando \r\n"}':
        estado = 'El cilindro no esta funcionando correctamente'
        mostrar = 'si'
        try:
            response = requests.post('http://127.0.0.1:8000/stop')
            if response.status_code == 200:
                print("Proceso detenido con éxito")
            else:
                print(f"Error al detener el proceso: {response.status_code}")
        except Exception as e:
            print(f"Error al enviar la solicitud POST: {e}")
    else:
        x = 1

mqtt_client.on_message = on_message
mqtt_client.connect(mqtt_broker, mqtt_port, 60)
mqtt_client.subscribe(mqtt_receiveTopic)

def mqtt_loop():
    mqtt_client.loop_forever()
    

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'nombre_usuario' not in session:
            return redirect(url_for('serve_login'))
        return f(*args, **kwargs)
    return decorated_function

def session_expired(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'nombre_usuario' in session:
            last_active = session.get('_last_active', None)
            if last_active is not None and datetime.now() > last_active + timedelta(minutes=15):
                session.pop('nombre_usuario', None)
                return redirect(url_for('serve_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def update_last_active():
    session['_last_active'] = datetime.now()

@app.route('/registro', methods=['POST'])
def registrar_usuario():
    nombre = request.form['nombre']
    area = request.form['area']
    problema = request.form['problema']
    insertar(nombre, area, problema)
    return redirect(url_for('serve_index'))

@app.route('/Login', methods=['POST'])
def login_usuario():
    global nombre_usuario  # Indica que la variable a modificar es la global
    gafet = request.form['GAFET']
    if verificar(gafet):
        nombre_usuario = obtener_nombre(gafet)
        session['nombre_usuario'] = nombre_usuario
        session['TIPO'] = obtener_rol(gafet)
        # session.permanent = True  # No necesitas esto
        return redirect(url_for('serve_index'))
    else:
        return redirect(url_for('serve_login', error=True))

@app.route('/logout')
def logout_usuario():
    session.pop('nombre_usuario', None)
    return redirect(url_for('serve_login'))

@app.route('/', methods=['GET'])
@session_expired
def serve_login():
    error = request.args.get('error')
    return render_template('Login.html', error=error)

def parse_points_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    points = []
    pattern = re.compile(r'Point\d+ \{[^}]+\}', re.MULTILINE)
    matches = pattern.findall(content)

    for match in matches:
        point_data = {}
        lines = match.split('\n')
        point_data['nNumber'] = int(re.search(r'nNumber=(\d+)', lines[1]).group(1))
        point_data['sLabel'] = re.search(r'sLabel="([^"]+)"', lines[2]).group(1)
        point_data['details'] = match.strip()
        point_data['rX'] = float(re.search(r'rX=([\-0-9\.]+)', lines[5]).group(1))
        point_data['rY'] = float(re.search(r'rY=([\-0-9\.]+)', lines[6]).group(1))
        point_data['rZ'] = float(re.search(r'rZ=([\-0-9\.]+)', lines[7]).group(1))
        point_data['rU'] = float(re.search(r'rU=([\-0-9\.]+)', lines[8]).group(1))
        point_data['rV'] = float(re.search(r'rV=([\-0-9\.]+)', lines[9]).group(1))
        point_data['rW'] = float(re.search(r'rW=([\-0-9\.]+)', lines[10]).group(1))
        points.append(point_data)

    return points

@app.route('/point/<int:nNumber>')
def get_point_details(nNumber):
    points = parse_points_file(r'C:\EpsonRC70\projects\EPSON INSERCION3 RC+7\RobotA\RobotA_code\robot1.pts')
    point = next((p for p in points if p['nNumber'] == nNumber), None)
    if point is None:
        return jsonify({"error": "Point not found"}), 404
    return jsonify(point)

def parse_points_file2(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    points = []
    pattern = re.compile(r'Point\d+ \{[^}]+\}', re.MULTILINE)
    matches = pattern.findall(content)

    for match in matches:
        point_data = {}
        lines = match.split('\n')
        point_data['nNumber'] = int(re.search(r'nNumber=(\d+)', lines[1]).group(1))
        point_data['sLabel'] = re.search(r'sLabel="([^"]+)"', lines[2]).group(1)
        point_data['details'] = match.strip()
        point_data['rX'] = float(re.search(r'rX=([\-0-9\.]+)', lines[5]).group(1))
        point_data['rY'] = float(re.search(r'rY=([\-0-9\.]+)', lines[6]).group(1))
        point_data['rZ'] = float(re.search(r'rZ=([\-0-9\.]+)', lines[7]).group(1))
        point_data['rU'] = float(re.search(r'rU=([\-0-9\.]+)', lines[8]).group(1))
        point_data['rV'] = float(re.search(r'rV=([\-0-9\.]+)', lines[9]).group(1))
        point_data['rW'] = float(re.search(r'rW=([\-0-9\.]+)', lines[10]).group(1))
        points.append(point_data)

    return points

@app.route('/point/<int:nNumber>')
def get_point_details2(nNumber):
    points = parse_points_file2(r'C:\EpsonRC70\projects\EPSON INSERCION3 RC+7\bbbbaaaack\RobotB_code\robot1.pts')
    point = next((p for p in points if p['nNumber'] == nNumber), None)
    if point is None:
        return jsonify({"error": "Point not found"}), 404
    return jsonify(point)

@app.route('/mrobot', methods=['GET'])
@session_expired
def serve_mrobot():
    points = parse_points_file(r'C:\EpsonRC70\projects\EPSON INSERCION3 RC+7\RobotA\RobotA_code\robot1.pts')
    return render_template('moverobot.html', points=points)

@app.route('/mrobot2', methods=['GET'])
@session_expired
def serve_mrobot2():
    points = parse_points_file2(r'C:\EpsonRC70\projects\EPSON INSERCION3 RC+7\bbbbaaaack\RobotB_code\robot1.pts')
    return render_template('moverobot2.html', points=points)

@app.route('/mantenimiento', methods=['GET'])
@login_required
@session_expired
def serve_index():
    return render_template('index.html')

@app.route('/ayuda', methods=['GET'])
@login_required
@session_expired
def serve_ayuda():
    return render_template('ayuda.html')

@app.route('/pasos', methods=['GET'])
@login_required
@session_expired
def pasos():
    robot = request.args.get('robot', '') 
    herramienta = request.args.get('herramienta', '')
    if robot == 'RobotA' and herramienta == 'Herramienta1':
        mnsj = 'RA'
        p1 = 'up_calibration_cA'
        p2 = 'down_calibration_cA'
        p3 = 'calibrate_position_cA'
    elif robot == 'RobotA' and herramienta == 'Herramienta2':
        mnsj = 'RA'
        p1 = 'up_calibration_cB'
        p2 = 'down_calibration_cB'
        p3 = 'calibrate_position_cB'
    elif robot == 'RobotB' and herramienta == 'Herramienta1':
        mnsj = 'RB'
        p1 = 'up_calibration_cB'
        p2 = 'down_calibration_cB'
        p3 = 'calibrate_position_cB'
    elif robot == 'RobotB' and herramienta == 'Herramienta2':
        mnsj = 'RB'
        p1 = 'up_calibration_cA'
        p2 = 'down_calibration_cA'
        p3 = 'calibrate_position_cA'
    return render_template('pasos.html', robot=robot, herramienta=herramienta, p1=p1, p2=p2, p3=p3, mnsj=mnsj, mostrar=mostrar)

@app.route('/carrera', methods=['GET'])
@login_required
@session_expired
def carrera():
    robot = request.args.get('robot', '') 
    herramienta = request.args.get('herramienta', '')
    if robot == 'RobotA' and herramienta == 'Herramienta1':
        mnsj = 'RA'
        p1 = 'VC1'
        p2 = ''
        p3 = ''
    elif robot == 'RobotA' and herramienta == 'Herramienta2':
        mnsj = 'RA'
        p1 = 'VC2'
        p2 = ''
        p3 = ''
    elif robot == 'RobotB' and herramienta == 'Herramienta1':
        mnsj = 'RB'
        p1 = 'VC3'
        p2 = ''
        p3 = ''
    elif robot == 'RobotB' and herramienta == 'Herramienta2':
        mnsj = 'RB'
        p1 = 'VC4'
        p2 = ''
        p3 = ''
    return render_template('carrera.html', robot=robot, herramienta=herramienta, p1=p1, p2=p2, p3=p3, mnsj=mnsj, estado=estado)

@app.route('/admin', methods=['GET'])
@login_required
@session_expired
def serve_admin():
    problemas = obtener_problemas_desde_bd()  # Llama a una función para obtener los problemas desde la base de datos
    ventosa = obtenertblventosa()
    fusible = obtener_fusibles()
    return render_template('admin.html', problemas=problemas,ventosa=ventosa,fusible=fusible)

@app.route('/delete_problema/<int:id>', methods=['POST'])
@login_required
@session_expired
def delete_problema(id):
    eliminar_problema(id)
    return '', 204  # Responde con 204 No Content

@app.route('/result', methods=['GET'])
@login_required
@session_expired
def serve_result():
    return render_template('resultados.html', x=x, y=y)

@app.route('/send_message', methods=['POST'])
@login_required
@session_expired
def send_mqtt_message():
    button_name = request.form['button_name']
    
    # Eliminar 'R1' del button_name si está presente
    if 'R1' in button_name:
        button_name = button_name.replace(' R1', '')
        
    if button_name in ['CV1', 'MINI_5', 'MINI_15', 'MULTI_7.5', 'MINI_7.5', 'ATO_30', 'ATO_5', 'ATO_15', 'MULTI_5', 'MINI_7.5', 'MINI_10', 'ATO_25', 'ATO_7.5', 'ATO_15']:
        mqtt_topic = 'RobotEpson/3'
        mqtt_message = {"trigger": button_name}
        if button_name == 'CV1':
            insertarusosVentosa(nombre=nombre_usuario, hora=datetime.now().isoformat(), ventosa=button_name)
        else:
            insertarusosFuse(nombre=nombre_usuario, hora=datetime.now().isoformat(), fusible=button_name)
    elif button_name == 'Stop':
        mqtt_topic = 'RobotEpson/3'
        mqtt_message = {"command": button_name}
        mqtt_client.publish(mqtt_topic, json.dumps(mqtt_message))
        mqtt_message = {"command": 'Start'}
        mqtt_client.publish(mqtt_topic, json.dumps(mqtt_message))
        mqtt_topic = 'RobotEpson/4'
        mqtt_message = {"command": button_name}
        mqtt_client.publish(mqtt_topic, json.dumps(mqtt_message))
        mqtt_message = {"command": 'Start'}
    elif button_name == 'CV2':
        mqtt_topic = 'RobotEpson/4'
        mqtt_message = {"trigger" : button_name}
        insertarusosVentosa(nombre=nombre_usuario, hora=datetime.now().isoformat(), ventosa=button_name)
    elif button_name in ['up_calibration_cA', 'down_calibration_cA', 'calibrate_position_cA', 'up_calibration_cB', 'down_calibration_cB', 'calibrate_position_cB']:
        mnsj = request.form['mnsj']
        if mnsj == 'RB':
            mqtt_topic = 'RobotEpson/4'
            if button_name =='calibrate_position_cA':
                insertarcalibraciones(nombre=nombre_usuario, hora=datetime.now().isoformat(), robot='Herramienta 2 del robot B calibrada')
            elif button_name == 'calibrate_position_cB':
                insertarcalibraciones(nombre=nombre_usuario, hora=datetime.now().isoformat(), robot='Herramienta 1 del robot B calibrada')
        elif mnsj == 'RA':
            mqtt_topic = 'RobotEpson/3'
            if button_name == 'calibrate_position_cA':
                insertarcalibraciones(nombre=nombre_usuario, hora=datetime.now().isoformat(), robot='Herramienta 1 del robot A calibrada')
            elif button_name == 'calibrate_position_cB':
                insertarcalibraciones(nombre=nombre_usuario, hora=datetime.now().isoformat(), robot="Herramienta 2 del robot A calibrada")
        mqtt_message = {"trigger": button_name}
    elif button_name in ['V1','V2']:
        mqtt_topic = 'RobotEpson/3'
        mqtt_message = {"trigger" : button_name}
    elif button_name in ['V3','V4']:
        mqtt_topic = 'RobotEpson/4'
        mqtt_message = {"trigger" : button_name} 
    elif button_name in ['PDC-R', 'PDC-P', 'TBLU', 'PDC-RMID', 'PDC-S', 'PDC-D']:
        mqtt_topic = 'PLC/1'
        mqtt_message = {button_name: True}
    elif button_name == 'tool3RA':
        mqtt_topic = 'RobotEpson/3'
        mqtt_message = {"trigger" : 'tool3'}
    elif button_name == 'tool4RA':
        mqtt_topic = 'RobotEpson/3'
        mqtt_message = {"trigger" : 'tool4'}
    elif button_name == 'tool3RB':
        mqtt_topic = 'RobotEpson/4'
        mqtt_message = {"trigger" : 'tool3'}
    elif button_name == 'tool4RB':
        mqtt_topic = 'RobotEpson/4'
        mqtt_message = {"trigger" : 'tool4'}
    elif button_name in ['VC1', 'VC2']:
        mqtt_topic = 'RobotEpson/3'
        mqtt_message = {"trigger" : button_name}
    elif button_name in ['VC4', 'VC3']:
        mqtt_topic = 'RobotEpson/4'
        mqtt_message = {"trigger" : button_name}

    mqtt_client.publish(mqtt_topic, json.dumps(mqtt_message))
    return jsonify({'status': 'Message sent'}), 200

@app.route('/send_message2', methods=['POST'])
@login_required
@session_expired
def send_mqtt_message2():
    button_name = request.form['button_name']
    
    if button_name in ['MINI_5', 'MINI_7.5', 'MINI_10', 'ATO_7.5', 'ATO_25', 'ATO_30', 'REALY_132', 'RELAY_112', 'ATO_15', 'MAXI_50', 'MAXI_40', 'MAXI_30', 'ATOC_10', 'ATOC_5', 'ATO_20', 'ATO_5', 'ATO_10', 'ATOC_15']:
        mqtt_topic = 'RobotEpson/4'
        mqtt_message = {"trigger": button_name}
        insertarusosFuse(nombre=nombre_usuario, hora=datetime.now().isoformat(), fusible=button_name)
    # Publicar el mensaje MQTT
    mqtt_client.publish(mqtt_topic, json.dumps(mqtt_message))

    return jsonify({'status': 'Message sent'}), 200

@app.route('/send_message3', methods=['POST'])
@login_required
@session_expired
def send_mqtt_message3():
    button_name = request.form['button_name'] 
    mqtt_topic = 'RobotEpson/3'
    mqtt_message = {"trigger": button_name}
    # Publicar el mensaje MQTT
    mqtt_client.publish(mqtt_topic, json.dumps(mqtt_message))
    return jsonify({'status': 'Message sent'}), 200

@app.route('/send_message4', methods=['POST'])
@login_required
@session_expired
def send_mqtt_message4():
    button_name = request.form['button_name'] 
    mqtt_topic = 'RobotEpson/4'
    mqtt_message = {"trigger": button_name}
    # Publicar el mensaje MQTT
    mqtt_client.publish(mqtt_topic, json.dumps(mqtt_message))
    return jsonify({'status': 'Message sent'}), 200

@app.route('/start', methods=['POST'])
@login_required
@session_expired
def start_process():
    iniciar_proceso_R()
    return jsonify({'status': 'started'})

@app.route('/stop', methods=['POST'])
@login_required
@session_expired
def stop_process():
    detener_proceso_R()
    return jsonify({'status': 'stopped'})

@app.route('/start_D', methods=['POST'])
@login_required
@session_expired
def start_process_D():
    iniciar_proceso_D()
    return jsonify({'status': 'started_D'})

@app.route('/stop_D', methods=['POST'])
@login_required
@session_expired
def stop_process_D():
    detener_proceso_D()
    return jsonify({'status': 'stopped_D'})

@app.route('/start_P', methods=['POST'])
@login_required
@session_expired
def start_process_P():
    iniciar_proceso_P()
    return jsonify({'status': 'started_P'})

@app.route('/stop_P', methods=['POST'])
@login_required
@session_expired
def stop_process_P():
    detener_proceso_P()
    return jsonify({'status': 'stopped_P'})

@app.route('/start_S', methods=['POST'])
@login_required
@session_expired
def start_process_S():
    iniciar_proceso_S()
    return jsonify({'status': 'started_S'})

@app.route('/stop_S', methods=['POST'])
@login_required
@session_expired
def stop_process_S():
    detener_proceso_S()
    return jsonify({'status': 'stopped_S'})

@app.route('/start_TB', methods=['POST'])
@login_required
@session_expired
def start_process_TB():
    iniciar_proceso_TB()
    return jsonify({'status': 'started_TB'})

@app.route('/stop_TB', methods=['POST'])
@login_required
@session_expired
def stop_process_TB():
    detener_proceso_TB()
    return jsonify({'status': 'stopped_TB'})


@app.route('/check_redirect', methods=['GET'])
@login_required
@session_expired
def check_redirect():
    global redirect_needed
    if redirect_needed:
        redirect_needed = False
        return jsonify({'redirect': True})
    return jsonify({'redirect': False})

API_URL = 'http://127.0.0.1:5000/api/get/'
DB_NAME = 'eiaf_3'

def obtener_datos(start_date, end_date):
    url = f"{API_URL}{DB_NAME}/historial/FIN/>=/{start_date.replace(' ', '%20')}/FIN/<=/{end_date.replace(' ', '%20')}"
    
    try:
        response = requests.get(url)
        response.raise_for_status() 
        
        data = response.json()
        reintentos = data.get('REINTENTOS', [])
        fusibles = data.get('FUSIBLES', [])
        resultados = data.get('RESULTADO', [])
        fechas = data.get('FIN', [])
        
        # Convertir las cadenas JSON a diccionarios
        datos = [{'reintentos': json.loads(reintento), 'fusibles': json.loads(fusible), 'resultado': resultado, 'fecha': fecha} for reintento, fusible, resultado, fecha in zip(reintentos, fusibles, resultados, fechas)]
        return datos
    except requests.exceptions.RequestException as e:
        # Manejar errores de solicitud HTTP
        print("Error de solicitud HTTP:", e)
        return []
    except (IndexError, KeyError) as e:
        # Manejar errores de acceso a datos JSON
        print("Error de acceso a datos JSON:", e)
        return []
    
def obtener_fechas_semana(semana, year):
    inicio_semana = datetime.strptime(f'{year}-W{int(semana)}-1', "%Y-W%U-%w")
    fin_semana = inicio_semana + timedelta(days=6.9)
    return inicio_semana.strftime('%Y-%m-%d'), fin_semana.strftime('%Y-%m-%d')

@login_required
@app.route('/estadisticas')
def index():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    datos = []
    if start_date and end_date:
        datos = obtener_datos(start_date, end_date)
    
    for dato in datos:
        dato['semana'] = datetime.strptime(dato['fecha'], '%a, %d %b %Y %H:%M:%S %Z').strftime('%Y-%U')

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
    total_resultados_buenos = 0

    # Procesar cada entrada de datos excluyendo "RELX"
    for dato in datos:
        reintentos = dato['reintentos']
        fusibles = dato['fusibles']
        resultado = dato['resultado']
        semana = dato['semana']
        if resultado == 'BUENO':
            total_resultados_buenos += 1
        for tabla, cavidades in reintentos.items():
            if tabla in tablas:
                for cavidad, conteo in cavidades.items():
                    if cavidad != "RELX" and cavidad in fusibles[tabla]:
                        fusible = fusibles[tabla][cavidad]
                        if fusible != "empty":
                            clave = f"{cavidad} ({fusible})"
                            if clave not in tablas[tabla]:
                                tablas[tabla][clave] = {}
                            if semana in tablas[tabla][clave]:
                                tablas[tabla][clave][semana] += conteo
                            else:
                                tablas[tabla][clave][semana] = conteo
                            totales[tabla] += conteo  # Sumar el conteo al total de la tabla

    # Obtener los 5 elementos que más fallan por cada tabla
    top5_por_tabla = {
        tabla: pd.DataFrame(sorted(
            [(clave, sum(semanas.values())) for clave, semanas in cavidades.items()],
            key=lambda item: item[1], reverse=True)[:5],
            columns=['Cavidad (Fusible)', 'Conteo'])
        for tabla, cavidades in tablas.items()
    }

    # Obtener los 5 elementos que más fallan en general
    total_fallas = {}
    for cavidades in tablas.values():
        for clave, semanas in cavidades.items():
            total_fallas[clave] = sum(semanas.values())

    top5_general = pd.DataFrame(sorted(total_fallas.items(), key=lambda item: item[1], reverse=True)[:5], columns=['Cavidad (Fusible)', 'Conteo'])

    # Convertir todos los datos a un formato adecuado para renderizar en HTML
    tablas_html = {tabla: pd.DataFrame.from_dict(cavidades, orient='index') for tabla, cavidades in tablas.items()}

    # Transformar las semanas en columnas
    for tabla, df in tablas_html.items():
        tablas_html[tabla] = df.fillna(0).transpose().to_dict()

    semanas_fechas = {semana: obtener_fechas_semana(semana.split('-')[1], semana.split('-')[0]) for semana in set(dato['semana'] for dato in datos)}

    return render_template('estadisticas.html', tablas=tablas_html, top5_por_tabla=top5_por_tabla, top5_general=top5_general, totales=totales, total_resultados_buenos=total_resultados_buenos, semanas_fechas=semanas_fechas)

if __name__ == '__main__':
    threading.Thread(target=procesar_imagenes_R).start()
    threading.Thread(target=procesar_imagenes_D).start() 
    threading.Thread(target=procesar_imagenes_P).start()
    threading.Thread(target=procesar_imagenes_S).start()
    threading.Thread(target=procesar_imagenes_TB).start()
    mqtt_thread = threading.Thread(target=mqtt_loop)
    mqtt_thread.daemon = True
    mqtt_thread.start()
    app.run(debug=True, port=8000)
