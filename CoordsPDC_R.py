import cv2
import paho.mqtt.client as mqtt
import time
import json

# Inicialización de variables globales
iniciar_R = False
visibilidad_R = [False, False, False, False, False, False, False, False]
coordenadas_R = [(161, 190, 36, 38), (649, 388, 77, 51), (450, 194, 22, 39), (298, 520, 21, 27), (380, 104, 37, 21), (646, 578, 50, 41), (97, 320, 26, 34), (204, 38, 33, 35)]
ruta_imagen_R = 'static/images/PDC-R.jpg'
imagen_R = cv2.imread(ruta_imagen_R)
detener_R = False

def iniciar_proceso_R():
    global iniciar_R
    iniciar_R = True

def detener_proceso_R():
    global iniciar_R, detener_R
    iniciar_R = False
    detener_R = True

def dibujar_rectangulos_R(img, coordenadas, visibilidad):
    img_con_rectangulos = img.copy()
    for (x, y, w, h), mostrar in zip(coordenadas, visibilidad):
        color = (0, 255, 0) if mostrar else (0, 0, 255)
        cv2.rectangle(img_con_rectangulos, (x, y), (x + w, y + h), color, 2)
    return img_con_rectangulos

def mostrar_imagen_R(img):
    cv2.imshow('Imagen_R', img)
    cv2.waitKey(2)

def on_message_R(client, userdata, msg):
    global iniciar_R, visibilidad_R, coordenadas_R, imagen_con_rectangulos_R, detener_R
    try:
        data = json.loads(msg.payload.decode())

        if "Iniciar_R" in data:
            iniciar_R = data["Iniciar_R"] == "True"
        elif msg.payload.decode() == '{"PDC-R_ERROR": true}' or msg.payload.decode() == '{"clamp_PDC-R": true}':
            visibilidad_R = [False] * len(coordenadas_R)
            ruta_guardar_R = 'static/images/imagen_final.jpg'
            cv2.imwrite(ruta_guardar_R, imagen_con_rectangulos_R)
            print(f"Imagen final guardada en '{ruta_guardar_R}'")
            detener_R = True
        else:
            if "raffi_PDCR" in data:
                visibilidad_R[0] = data["raffi_PDCR"]
            elif "PDC-R LS" in data:
                visibilidad_R[1] = data["PDC-R LS"]
                visibilidad_R[2] = data["PDC-R LS"]
            elif "PDC-R RS 1" in data:
                visibilidad_R[6] = data["PDC-R RS 1"]
            elif "PDC-R RS 2" in data:
                visibilidad_R[7] = data["PDC-R RS 2"] == False
            elif "PDC-R RS 3" in data:
                visibilidad_R[4] = data["PDC-R RS 3"]
    except Exception as e:
        print("Error:", e)

def procesar_imagenes_R():
    global iniciar_R, imagen_R, coordenadas_R, visibilidad_R, imagen_con_rectangulos_R, detener_R
    client = mqtt.Client()
    client.on_message = on_message_R
    
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
        if detener_R:
            detener_R = False
            continue  # Reiniciar el bucle si detener_R es verdadero

        if iniciar_R:
            imagen_con_rectangulos_R = dibujar_rectangulos_R(imagen_R, coordenadas_R, visibilidad_R)
            mostrar_imagen_R(imagen_con_rectangulos_R)
        time.sleep(2)
