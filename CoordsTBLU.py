import cv2
import paho.mqtt.client as mqtt
import time
import json


""" Completado 100% """

# Inicialización de variables globales
iniciar_TB = False
visibilidad_TB = [False, False, False]
coordenadas_TB = [(220, 556, 41, 47), (478, 375, 42, 66), (278, 414, 27, 31)]
ruta_imagen_TB = 'static/images/TBLU.jpg'
imagen_TB = cv2.imread(ruta_imagen_TB)
detener_TB = False

def iniciar_proceso_TB():
    global iniciar_TB
    iniciar_TB = True

def detener_proceso_TB():
    global iniciar_TB, detener_TB
    iniciar_TB = False
    detener_TB = True

def dibujar_rectangulos_TB(img, coordenadas, visibilidad):
    img_con_rectangulos = img.copy()
    for (x, y, w, h), mostrar in zip(coordenadas, visibilidad):
        color = (0, 255, 0) if mostrar else (0, 0, 255)
        cv2.rectangle(img_con_rectangulos, (x, y), (x + w, y + h), color, 2)
    return img_con_rectangulos

def mostrar_imagen_TB(img):
    cv2.imshow('Imagen_TB', img)
    cv2.waitKey(2)

def on_message_TB(client, userdata, msg):
    global iniciar_TB, visibilidad_TB, coordenadas_TB, imagen_con_rectangulos_TB, detener_TB
    try:
        data = json.loads(msg.payload.decode())
        
        if "Iniciar_TB" in data:
            iniciar_TB = data["Iniciar_TB"] == "True"
        elif msg.payload.decode() == '{"TBLU_ERROR": true}' or msg.payload.decode() == '{"clamp_TBLU": true}':
            visibilidad_TB = [False] * len(coordenadas_TB)
            ruta_guardar_TB = 'static/images/imagen_final.jpg'
            cv2.imwrite(ruta_guardar_TB, imagen_con_rectangulos_TB)
            print(f"Imagen final guardada en '{ruta_guardar_TB}'")
            detener_TB = True
        else:
            if "raffi_TBLU" in data:
                visibilidad_TB[0] = data["raffi_TBLU"]
            elif "TBLU RS" in data:
                visibilidad_TB[1] = data["TBLU RS"] 
            elif "TBLU LS" in data:
                visibilidad_TB[2] = data["TBLU LS"] 
    except Exception as e:
        print("Error:", e)

def procesar_imagenes_TB():
    global iniciar_TB, imagen_TB, coordenadas_TB, visibilidad_TB, imagen_con_rectangulos_TB, detener_TB
    client = mqtt.Client()
    client.on_message = on_message_TB
    
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
        if detener_TB:
            detener_TB = False
            continue  # Reiniciar el bucle si detener_TB es verdadero

        if iniciar_TB:
            imagen_con_rectangulos_TB = dibujar_rectangulos_TB(imagen_TB, coordenadas_TB, visibilidad_TB)
            mostrar_imagen_TB(imagen_con_rectangulos_TB)
        time.sleep(2)
