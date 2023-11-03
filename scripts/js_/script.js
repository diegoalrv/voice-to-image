let isRecording = false;
let chunks = [];
let mediaRecorder;

const micButton = document.getElementById('micButton');
const transcriptionContainer = document.createElement('div'); // Contenedor para la transcripción
transcriptionContainer.style.color = 'white'; // Establecer el color del texto a blanco
transcriptionContainer.style.marginTop = '20px'; // Añadir un poco de margen superior
transcriptionContainer.style.textAlign = 'center'; // Centrar el texto
document.body.appendChild(transcriptionContainer); // Añadir el contenedor al cuerpo del documento

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
    const formData = new FormData();
    const date = new Date();
    const formattedDate = `${date.getDate().toString().padStart(2, '0')}${(date.getMonth() + 1).toString().padStart(2, '0')}${date.getFullYear()}-${date.getHours().toString().padStart(2, '0')}${date.getMinutes().toString().padStart(2, '0')}`;
    formData.append("file", blob, `record-${formattedDate}.wav`);

    fetch('http://127.0.0.1:8000/upload/', {
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
        return fetch('http://127.0.0.1:8000/transcribe/'); // Solicitar la transcripción
    })
    .then(response => response.json())
    .then(data => {
        transcriptionContainer.textContent = data.transcription; // Mostrar la transcripción
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}
