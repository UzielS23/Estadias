function sendMQTTMessage(buttonName, mnsj) {
  fetch('/send_message', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: 'button_name=' + encodeURIComponent(buttonName) + '&mnsj=' + encodeURIComponent(mnsj)
  })
  .then(response => {
      if (response.ok) {
          console.log('Mensaje MQTT enviado correctamente');
      } else {
          console.error('Error al enviar el mensaje MQTT');
      }
  })
  .catch(error => {
      console.error('Error de red:', error);
  });
}
