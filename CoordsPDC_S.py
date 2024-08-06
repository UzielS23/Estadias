import cv2
import paho.mqtt.client as mqtt
import time
import json


""" Completado 100% """

# Inicialización de variables globales
iniciar_S = False
visibilidad_S = [False, False, False]
coordenadas_S = [(265, 525, 66, 44), (637, 372, 34, 39), (439, 403, 36, 42)]
ruta_imagen_S = 'static/images/PDC-S.jpg'
imagen_S = cv2.imread(ruta_imagen_S)
detener_S = False

def iniciar_proceso_S():
    global iniciar_S
    iniciar_S = True

def detener_proceso_S():
    global iniciar_S, detener_S
    iniciar_S = False
    detener_S = True

def dibujar_rectangulos_S(img, coordenadas, visibilidad):
    img_con_rectangulos = img.copy()
    for (x, y, w, h), mostrar in zip(coordenadas, visibilidad):
        color = (0, 255, 0) if mostrar else (0, 0, 255)
        cv2.rectangle(img_con_rectangulos, (x, y), (x + w, y + h), color, 2)
    return img_con_rectangulos

def mostrar_imagen_S(img):
    cv2.imshow('Imagen_S', img)
    cv2.waitKey(2)

def on_message_S(client, userdata, msg):
    global iniciar_S, visibilidad_S, coordenadas_S, imagen_con_rectangulos_S, detener_S
    try:
        data = json.loads(msg.payload.decode())
        
        if "Iniciar_S" in data:
            iniciar_S = data["Iniciar_S"] == "True"
        elif msg.payload.decode() == '{"PDC-S_ERROR": true}' or msg.payload.decode() == '{"clamp_PDC-S": true}':
            visibilidad_S = [False] * len(coordenadas_S)
            ruta_guardar_S = 'static/images/imagen_final.jpg'
            cv2.imwrite(ruta_guardar_S, imagen_con_rectangulos_S)
            print(f"Imagen final guardada en '{ruta_guardar_S}'")
            detener_S = True
        else:
            if "raffi_PDCS" in data:
                visibilidad_S[0] = data["raffi_PDCS"]
            elif "PDC-S RS 1" in data:
                visibilidad_S[1] = data["PDC-S RS 1"] 
            elif "PDC-S LS" in data:
                visibilidad_S[2] = data["PDC-S LS"] 
    except Exception as e:
        print("Error:", e)

def procesar_imagenes_S():
    global iniciar_S, imagen_S, coordenadas_S, visibilidad_S, imagen_con_rectangulos_S, detener_S
    client = mqtt.Client()
    client.on_message = on_message_S
    
    try:
        client.connect("127.0.0.1", 1883)  # Primer intento de conexión
    except Exception as e:
        print(f"Error al conectar con 127.0.0.1: {e}")
        try:
            client.connect("192.168.15.70", 502)  # Segundo intento de conexión
        except Exception as e:
            print(f"Error al conectar con 192.168.15.70: {e}")
            return  # Termina la función si no puede conectarse a ningún servidor

    client.subscribe("PLC/1/status")
    client.subscribe("PLC/1")
    client.loop_start()

    while True:
        if detener_S:
            detener_S = False
            continue  # Reiniciar el bucle si detener_S es verdadero

        if iniciar_S:
            imagen_con_rectangulos_S = dibujar_rectangulos_S(imagen_S, coordenadas_S, visibilidad_S)
            mostrar_imagen_S(imagen_con_rectangulos_S)
        time.sleep(2)
