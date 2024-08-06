let currentRobot = '3';

function moveRobot(direction) {
    console.log(`Moving robot ${currentRobot} in direction: ${direction}`);
}

document.getElementById('savePoint').addEventListener('click', function() {
    console.log(`Point saved for Robot ${currentRobot}`);
});

document.getElementById('changeTool').addEventListener('click', function() {
    console.log('Tool changed');
});

document.getElementById('changeTool2').addEventListener('click', function() {
    console.log('Tool changed');
});

document.getElementById('pickFuseBtn').addEventListener('click', function() {
    const fuse = document.getElementById('pickFuse').value;
    console.log(`Picked ${fuse}`);
});

document.getElementById('insertFuseBtn').addEventListener('click', function() {
    const position = document.getElementById('insertFuse').value;
    console.log(`Inserted fuse at ${position}`);
});

document.getElementById('selectHandBtn').addEventListener('click', function() {
    console.log('Hand selected');
});


function showDetails(nNumber) {
    fetch(`/point/${nNumber}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('details').innerHTML = 'Point not found';
            } else {
                document.getElementById('details').innerHTML = `<pre>${data.details}</pre>`;
                document.getElementById('currentPositionX').value = data.rX;
                document.getElementById('currentPositionY').value = data.rY;
                document.getElementById('currentPositionZ').value = data.rZ;
                document.getElementById('currentPositionU').value = data.rU;
                document.getElementById('currentPositionV').value = data.rV;
                document.getElementById('currentPositionW').value = data.rW;
            }
        });
}

function handleSelectChange(selectElement) {
    const selectedOption = selectElement.options[selectElement.selectedIndex];
    const nNumber = selectedOption.value;
    const sLabel = selectedOption.text;

    showDetails(nNumber);
    sendMQTTMessage3(sLabel);
}

function handleSelectChange2(selectElement) {
    const selectedOption = selectElement.options[selectElement.selectedIndex];
    const VALOR = selectedOption.value
    sendMQTTMessage3(VALOR);
}

function handleSelectChange3(selectElement) {
    const selectedOption = selectElement.options[selectElement.selectedIndex];
    const VALOR = selectedOption.value
    sendMQTTMessage3(VALOR);
}

function sendMQTTMessageGP() {
    // Obtener el valor del input
    var numberInput = document.getElementById('numberInput').value;

    // Verificar si el input tiene un valor válido
    if (numberInput) {
        // Construir el mensaje MQTT
        var message = 'save_' + numberInput;

        // Llamar a la función para enviar el mensaje MQTT
        sendMQTTMessage3(message);
    } else {
        alert('Por favor, ingrese un número válido entre 520 y 999.');
    }
}

var currentTool = 'Tool4';
var currentTool2 = 'Tool1';

function changeTool() {
    // Alternar entre Tool4 y Tool3
    if (currentTool === 'Tool4') {
        currentTool = 'Tool3';
    } else {
        currentTool = 'Tool4';
    }

    // Enviar el mensaje MQTT
    sendMQTTMessage3(currentTool);
    
    // Actualizar el texto del botón
    document.getElementById('changeTool').textContent = `Cambiar a ${currentTool}`;
}

var currentTool2 = 'Tool1';
function changeTool2() {
    // Alternar entre Tool4 y Tool3
    if (currentTool2 === 'Tool1') {
        currentTool2 = 'Tool2';
    } else {
        currentTool2 = 'Tool1';
    }

    // Enviar el mensaje MQTT
    sendMQTTMessage3(currentTool2);
    
    // Actualizar el texto del botón
    document.getElementById('changeTool2').textContent = `Cambiar a ${currentTool2}`;
}

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('pickFuseBtn').addEventListener('click', function () {
        const selectElement = document.getElementById('fuseSelect');
        const selectedValue = selectElement.value;
            sendMQTTMessage3(selectedValue);
        
    });
});

function moveRobot(direction) {
    const currentX = parseFloat(document.getElementById('currentPositionX').value) || 0;
    const currentY = parseFloat(document.getElementById('currentPositionY').value) || 0;
    const currentZ = parseFloat(document.getElementById('currentPositionZ').value) || 0;
    const currentU = parseFloat(document.getElementById('currentPositionU').value) || 0;
    const currentV = parseFloat(document.getElementById('currentPositionV').value) || 0;
    const currentW = parseFloat(document.getElementById('currentPositionW').value) || 0;

    const jogX = parseFloat(document.getElementById('jogDistanceX').value) || 0;
    const jogY = parseFloat(document.getElementById('jogDistanceY').value) || 0;
    const jogZ = parseFloat(document.getElementById('jogDistanceZ').value) || 0;
    const jogU = parseFloat(document.getElementById('jogDistanceU').value) || 0;
    const jogV = parseFloat(document.getElementById('jogDistanceV').value) || 0;
    const jogW = parseFloat(document.getElementById('jogDistanceW').value) || 0;

    switch (direction) {
        case '+X':
            document.getElementById('currentPositionX').value = currentX + jogX;
            break;
        case '-X':
            document.getElementById('currentPositionX').value = currentX - jogX;
            break;
        case '+Y':
            document.getElementById('currentPositionY').value = currentY + jogY;
            break;
        case '-Y':
            document.getElementById('currentPositionY').value = currentY - jogY;
            break;
        case '+Z':
            document.getElementById('currentPositionZ').value = currentZ + jogZ;
            break;
        case '-Z':
            document.getElementById('currentPositionZ').value = currentZ - jogZ;
            break;
        case '+U':
            document.getElementById('currentPositionU').value = currentU + jogU;
            break;
        case '-U':
            document.getElementById('currentPositionU').value = currentU - jogU;
            break;
        case '+V':
            document.getElementById('currentPositionV').value = currentV + jogV;
            break;
        case '-V':
            document.getElementById('currentPositionV').value = currentV - jogV;
            break;
        case '+W':
            document.getElementById('currentPositionW').value = currentW + jogW;
            break;
        case '-W':
            document.getElementById('currentPositionW').value = currentW - jogW;
            break;
    }
}
