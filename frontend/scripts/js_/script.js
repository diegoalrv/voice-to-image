
let isRecording = false;
let chunks = [];
let mediaRecorder;

var micButton = document.getElementById('micButton');
const transcriptionContainer = document.createElement('div');
const imageContainer = document.createElement('div'); // Contenedor para la imagen

// Estilos para la transcripción y la imagen
transcriptionContainer.style.color = 'white';
transcriptionContainer.style.marginTop = '20px';
transcriptionContainer.style.textAlign = 'center';
imageContainer.style.marginTop = '20px';
imageContainer.style.textAlign = 'center';

// Añadir los contenedores al cuerpo del documento
document.body.appendChild(transcriptionContainer);
document.body.appendChild(imageContainer);

micButton.addEventListener('click', toggleRecording);

async function toggleRecording() {
    if (isRecording) {
        stopRecording();
    } else {
        await startRecording();
    }
}

async function startRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    console.log('local')
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = e => chunks.push(e.data);
    mediaRecorder.onstop = saveAudio;
    mediaRecorder.start();
    isRecording = true;
}


function stopRecording() {
    mediaRecorder.stop();
    isRecording = false;
}

function saveAudio() {
    const blob = new Blob(chunks, { type: 'audio/wav' });
    chunks = []; // Clear the chunks array for the next recording
    const formData = new FormData();
    const date = new Date();
    const formattedDate = `${date.getDate().toString().padStart(2, '0')}${(date.getMonth() + 1).toString().padStart(2, '0')}${date.getFullYear()}-${date.getHours().toString().padStart(2, '0')}${date.getMinutes().toString().padStart(2, '0')}`;
    formData.append("file", blob, `record-${formattedDate}.wav`);

    fetch('http://localhost:8050/upload/', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.status === 200) {
            return response.json();
        } else {
            throw new Error('Upload failed');
        }
    })
    .then(data => {
        console.log(data.message);
        return fetch('http://localhost:8050/transcribe/');
    })
    .then(response => response.json())
    .then(data => {
        transcriptionContainer.textContent = data.transcription;
        return fetch('http://localhost:8050/generate-image/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt: data.transcription })
        });
    })
    .then(response => {
        if (response.ok) {
            return response.json(); // Cambiado para recibir JSON
        } else {
            throw new Error('Image generation failed');
        }
    })
    .then(data => {
        console.log('Image data received:', data); // Imprime los datos de la imagen recibidos
        displayGeneratedImage(data.image); // Asegúrate de que 'data.image' es la clave correcta
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function displayGeneratedImage(imageBase64) {
    const imageElement = new Image();
    imageElement.src = `data:image/jpeg;base64,${imageBase64}`;
    imageElement.onload = () => {
        console.log('Image loaded successfully');
    };
    imageElement.onerror = (error) => {
        console.error('Error loading image:', error);
    };
    imageElement.style.width = '100%'; // Ajustar al ancho del contenedor, si es necesario
    imageElement.style.height = 'auto';
    imageElement.style.marginTop = '20px'; // Añadir un poco de margen superior

    // Limpiar cualquier imagen existente y mostrar la nueva
    const imageContainer = document.getElementById('imageContainer');
    if (imageContainer) {
        imageContainer.innerHTML = ''; // Limpiar el contenedor de imágenes
        imageContainer.appendChild(imageElement); // Añadir la nueva imagen
    }
}