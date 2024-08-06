import cv2
import paho.mqtt.client as mqtt
import time
import json

""" Completado 100%"""

# Inicialización de variables globales
iniciar_D = False
visibilidad_D = [False, False, False, False]
coordenadas_D = [(474, 274, 34, 36), (447, 575, 31, 24), (336, 227, 26, 24), (186, 462, 27, 37)]
ruta_imagen_D = 'static/images/PDC-D.jpg'
imagen_D = cv2.imread(ruta_imagen_D)
detener_D = False

def iniciar_proceso_D():
    global iniciar_D
    iniciar_D = True

def detener_proceso_D():
    global iniciar_D, detener_D
    iniciar_D = False
    detener_D = True

def dibujar_rectangulos_D(img, coordenadas, visibilidad):
    img_con_rectangulos = img.copy()
    for (x, y, w, h), mostrar in zip(coordenadas, visibilidad):
        color = (0, 255, 0) if mostrar else (0, 0, 255)
        cv2.rectangle(img_con_rectangulos, (x, y), (x + w, y + h), color, 2)
    return img_con_rectangulos

def mostrar_imagen_D(img):
    cv2.imshow('Imagen_D', img)
    cv2.waitKey(2)

def on_message_D(client, userdata, msg):
    global iniciar_D, visibilidad_D, coordenadas_D, imagen_con_rectangulos_D, detener_D
    try:
        data = json.loads(msg.payload.decode())
        
        if "Iniciar_D" in data:
            iniciar_D = data["Iniciar_D"] == "True"
        elif msg.payload.decode() == '{"PDC-D_ERROR": true}' or msg.payload.decode() == '{"clamp_PDC-D": true}':
            visibilidad_D = [False] * len(coordenadas_D)
            ruta_guardar_D = 'static/images/imagen_final.jpg'
            cv2.imwrite(ruta_guardar_D, imagen_con_rectangulos_D)
            print(f"Imagen final guardada en '{ruta_guardar_D}'")
            detener_D = True
        else:
            if "raffi_PDCD" in data:
                visibilidad_D[0] = data["raffi_PDCD"]
            elif "PDC-D LS" in data:
                visibilidad_D[1] = data["PDC-D LS"] 
            elif "PDC-D RS 1" in data:
                visibilidad_D[2] = data["PDC-D RS 1"]
            elif "PDC-D RS 2" in data:
                visibilidad_D[3] = data["PDC-D RS 2"]
    except Exception as e:
        print("Error:", e)

def procesar_imagenes_D():
    global iniciar_D, imagen_D, coordenadas_D, visibilidad_D, imagen_con_rectangulos_D, detener_D
    client = mqtt.Client()
    client.on_message = on_message_D
    
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
        if detener_D:
            detener_D = False
            continue  # Reiniciar el bucle si detener_D es verdadero

        if iniciar_D:
            imagen_con_rectangulos_D = dibujar_rectangulos_D(imagen_D, coordenadas_D, visibilidad_D)
            mostrar_imagen_D(imagen_con_rectangulos_D)
        time.sleep(2)
