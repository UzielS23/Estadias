// Función para buscar elementos
function searchFunction() {
  var input, filter, cards, card, title, i, txtValue;
  input = document.getElementById('searchInput');
  filter = input.value.toUpperCase();
  cards = document.getElementsByClassName('card');
  
  for (i = 0; i < cards.length; i++) {
      title = cards[i].querySelector('.card-title');
      txtValue = title.textContent || title.innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
          cards[i].style.display = '';
      } else {
          cards[i].style.display = 'none';
      }
  }
}

// Función para abrir una ventana emergente con botones
function openPopup() {
    // Abre una nueva ventana con las siguientes características
    var popup = window.open('', '_blank', 'width=400,height=300,top=100,left=100');

    // Genera dinámicamente los botones en la ventana emergente
    var buttons = ['Botón 1', 'Botón 2', 'Botón 3', 'Botón 4', 'Botón 5', 'Botón 6'];
    var buttonContainer = popup.document.createElement('div');
    buttonContainer.className = 'popup-buttons';
    buttons.forEach(function(label) {
      var button = popup.document.createElement('button');
      button.className = 'popup-button';
      button.textContent = label;
      buttonContainer.appendChild(button);
    });
    popup.document.body.appendChild(buttonContainer);
  }
  
// Funcion para reproducir un GIR al presionar un boton
function reproducirGif() {
    var gifContainer = document.getElementById("gifContainer");
    var overlay = document.getElementById("overlay");
    gifContainer.style.display = "block";
    overlay.style.display = "block";

    setTimeout(function(){
        gifContainer.style.display = "none";
        overlay.style.display = "none";
    }, 3000); // Cambia este valor al tiempo en milisegundos que quieras que dure el gif antes de desaparecer (en este caso, 3 segundos)
  }

function sendFuseValue() {
    // Obtener el valor seleccionado del select
    const selectedValue = document.getElementById('mySelect').value;

    // Verificar si se seleccionó un valor válido
    if (selectedValue) {
        // Verificar si el valor contiene 'R1' en el texto
        if (selectedValue.includes('R1')) {
            // Hacer la petición POST al servidor a la ruta /send_message2
            fetch('/send_message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: 'button_name=' + selectedValue
            })
            .then(response => {
                if (response.ok) {
                    console.log('Mensaje MQTT enviado correctamente a /send_message2');
                } else {
                    console.error('Error al enviar el mensaje MQTT a /send_message2');
                }
            })
            .catch(error => {
                console.error('Error de red:', error);
            });
        } else {
            // Hacer la petición POST al servidor a la ruta /send_message
            fetch('/send_message2', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: 'button_name=' + selectedValue
            })
            .then(response => {
                if (response.ok) {
                    console.log('Mensaje MQTT enviado correctamente a /send_message');
                } else {
                    console.error('Error al enviar el mensaje MQTT a /send_message');
                }
            })
            .catch(error => {
                console.error('Error de red:', error);
            });
        }
    } else {
        console.error('Debe seleccionar un fusible antes de enviar el mensaje MQTT');
    }
}


document.addEventListener('click', function(event) {
    if (event.target && event.target.id === 'sendFuseButton') {
        sendFuseValue();
    }
});

function sendMQTTMessage3(buttonName) {
    fetch('/send_message3', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: 'button_name=' + buttonName
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

function sendMQTTMessage4(buttonName) {
    fetch('/send_message4', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: 'button_name=' + buttonName
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


// Función para enviar un mensaje MQTT  
function sendMQTTMessage(buttonName) {
    fetch('/send_message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: 'button_name=' + buttonName
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

$(document).ready(function(){
    $('.modal-button').on('click', function(){
        var buttonText = $(this).text();
        $.ajax({
            url: '/send-mqtt',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ estado: buttonText }),
            success: function(response) {
                console.log(response);
            },
            error: function(error) {
                console.error(error);
            }
        });
    });
});

// Función para verificar los campos del formulario en tiempo real
function checkFormFields() {
    var nombre = $('#nombre').val().trim();
    var area = $('#area').val();
    var problema = $('#problema').val().trim();

    if (nombre && area && problema) {
        $('#submitBtn').prop('disabled', false);
    } else {
        $('#submitBtn').prop('disabled', true);
    }
}

// Eventos para verificar los campos del formulario en tiempo real
$('#nombre, #area, #problema').on('input change', function() {
    checkFormFields();
});

// Llamar a la función de verificación cuando se cargue la página
$(document).ready(function() {
    checkFormFields();
});

// Función para confirmar el cierre de sesión
function confirmLogout(event) {
    event.preventDefault();
    var confirmation = confirm("¿Seguro que deseas cerrar sesión?");
    if (confirmation) {
        window.location.href = event.currentTarget.getAttribute('href');
    }
}

// Función para reiniciar el temporizador de sesión
let timeout;

        function resetTimer() {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                alert("Tu sesión ha expirado por inactividad.");
                window.location.href = "/logout";;
            }, 15 * 60 * 1000); // 15 minutos en milisegundos
        }

        // Eventos que reinician el temporizador de sesión
        document.onload = resetTimer;
        document.onmousemove = resetTimer;
        document.onkeydown = resetTimer;

        function confirmLogout(event) {
            event.preventDefault();
            var confirmation = confirm("¿Seguro que deseas cerrar sesión?");
            if (confirmation) {
                window.location.href = event.currentTarget.getAttribute('href');
            }
        }

        function iniciarProceso() {
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/start', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    var data = JSON.parse(xhr.responseText);
                    alert("Nido PDC-R habilitado correctamente");
                }
            };
            xhr.send();
        }

        function iniciarProceso_D() {
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/start_D', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    var data = JSON.parse(xhr.responseText);
                    alert("Nido PDC-D habilitado correctamente");
                }
            };
            xhr.send();
        }

        function iniciarProceso_P() {
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/start_P', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    var data = JSON.parse(xhr.responseText);
                    alert("Nido PDC-P habilitado correctamente");
                }
            };
            xhr.send();
        }  
        
        function iniciarProceso_S() {
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/start_S', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    var data = JSON.parse(xhr.responseText);
                    alert("Nido PDC-S Habilitado correctamente");
                }
            };
            xhr.send();
        }  

        function iniciarProceso_TBLU() {
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/start_TB', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    var data = JSON.parse(xhr.responseText);
                    alert("Nido TBLU habilitado correctamente");
                }
            };
            xhr.send();
        }  

        // Función para verificar si hay una redirección y redirigir si es necesario
        function checkForRedirect() {
            fetch('/check_redirect')
                .then(response => response.json())
                .then(data => {
                    if (data.redirect) {
                        window.location.href = '/result';
                    }
                })
                .catch(error => console.error('Error checking redirect:', error));
        }

        // Verificar redirección cada 5 segundos
        setInterval(checkForRedirect, 5000);    

        function toggleMenu(event, id) {
            event.preventDefault();
            var submenu = document.getElementById(id);
            if (submenu.style.display === "none" || submenu.style.display === "") {
                submenu.style.display = "block";
            } else {
                submenu.style.display = "none";
            }
        }

        function redirectTo(url) {
            window.location.href = url;
        }

        function regresarModal(currentModalId, targetModalId) {
            // Cerrar el modal actual
            $('#' + currentModalId).modal('hide');
            // Abrir el modal de destino después de un pequeño retraso para permitir la transición
            setTimeout(function() {
                $('#' + targetModalId).modal('show');
            }, 500); // 500 milisegundos de retraso
        }