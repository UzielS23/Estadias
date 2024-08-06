import cv2
import paho.mqtt.client as mqtt
import time
import json


""" Completado 100% """

# Inicialización de variables globales
iniciar_P = False
visibilidad_P = [False, False, False, False]
coordenadas_P = [(536, 179, 30, 37), (189, 520, 31, 31), (397, 168, 32, 28), (434, 646, 30, 51)]
ruta_imagen_P = 'static/images/PDC-P.jpg'
imagen_P = cv2.imread(ruta_imagen_P)
detener_P = False

def iniciar_proceso_P():
    global iniciar_P
    iniciar_P = True

def detener_proceso_P():
    global iniciar_P, detener_P
    iniciar_P = False
    detener_P = True

def dibujar_rectangulos_P(img, coordenadas, visibilidad):
    img_con_rectangulos = img.copy()
    for (x, y, w, h), mostrar in zip(coordenadas, visibilidad):
        color = (0, 255, 0) if mostrar else (0, 0, 255)
        cv2.rectangle(img_con_rectangulos, (x, y), (x + w, y + h), color, 2)
    return img_con_rectangulos

def mostrar_imagen_P(img):
    cv2.imshow('Imagen_P', img)
    cv2.waitKey(2)

def on_message_P(client, userdata, msg):
    global iniciar_P, visibilidad_P, coordenadas_P, imagen_con_rectangulos_P, detener_P
    try:
        data = json.loads(msg.payload.decode())
        
        if "Iniciar_P" in data:
            iniciar_P = data["Iniciar_P"] == "True"
        elif msg.payload.decode() == '{"PDC-P_ERROR": true}' or msg.payload.decode() == '{"clamp_PDC-P": true}':
            visibilidad_P = [False] * len(coordenadas_P)
            ruta_guardar_P = 'static/images/imagen_final.jpg'
            cv2.imwrite(ruta_guardar_P, imagen_con_rectangulos_P)
            print(f"Imagen final guardada en '{ruta_guardar_P}'")
            detener_P = True
        else:
            if "raffi_PDCP" in data:
                visibilidad_P[0] = data["raffi_PDCP"] 
            elif "PDC-P RS 1" in data:
                visibilidad_P[2] = data["PDC-P RS 1"]
            elif "PDC-P RS 3" in data:
                visibilidad_P[1] = data["PDC-P RS 3"] 
            elif "PDC-P LS" in data:
                visibilidad_P[3] = data["PDC-P LS"] 
    except Exception as e:
        print("Error:", e)

def procesar_imagenes_P():
    global iniciar_P, imagen_P, coordenadas_P, visibilidad_P, imagen_con_rectangulos_P, detener_P
    client = mqtt.Client()
    client.on_message = on_message_P
    
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
        if detener_P:
            detener_P = False
            continue  # Reiniciar el bucle si detener_P es verdadero

        if iniciar_P:
            imagen_con_rectangulos_P = dibujar_rectangulos_P(imagen_P, coordenadas_P, visibilidad_P)
            mostrar_imagen_P(imagen_con_rectangulos_P)
        time.sleep(2)
