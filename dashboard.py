import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Inicializa la app
app = dash.Dash(__name__)

mic_url = 'https://e7.pngegg.com/pngimages/76/379/png-clipart-computer-icons-symbol-microphone-sound-recording-and-reproduction-symbol-miscellaneous-microphone.png'

# Define la apariencia del dashboard
app.layout = html.Div(style={
    'backgroundColor': 'black', 
    'height': '100vh', 
    'display': 'flex', 
    'alignItems': 'center', 
    'justifyContent': 'center',
    'overflow': 'hidden'
}, children=[
    html.Div(id='recording-circle', 
             style={
                 'width': '50px', 
                 'height': '50px', 
                 'borderRadius': '50%', 
                 'backgroundColor': 'red',
                 'position': 'absolute',
                 'top': '20px',
                 'left': '20px',
                 'boxShadow': '0 0 15px rgba(0, 0, 0, 0.2)',  # Sombra suave
                 'border': '2px solid rgba(255, 255, 255, 0.1)'  # Borde sutil
             }),
    html.Img(id='microphone-icon',
             src=mic_url,
             style={'width': '100px', 'cursor': 'pointer'}),
    dcc.Store(id='memory-store', storage_type='memory'),  # Para almacenar el audio
    html.Script("""
        var mediaRecorder;
        var audioChunks = [];
        
        document.getElementById("microphone-icon").onclick = function() {
            if (mediaRecorder && mediaRecorder.state === "recording") {
                mediaRecorder.stop();
            } else {
                navigator.mediaDevices.getUserMedia({ audio: true })
                .then(stream => {
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];
                    
                    mediaRecorder.ondataavailable = event => {
                        audioChunks.push(event.data);
                    };
                    
                    mediaRecorder.onstop = () => {
                        let audioBlob = new Blob(audioChunks, {
                            type: "audio/wav"
                        });
                        let audioUrl = URL.createObjectURL(audioBlob);
                        document.getElementById("memory-store").data = audioUrl;
                    };
                    
                    mediaRecorder.start();
                });
            }
        };
    """)
])

@app.callback(
    [Output('microphone-icon', 'src'), 
     Output('recording-circle', 'style')],
    Input('microphone-icon', 'n_clicks')
)
def toggle_recording(n_clicks):
    circle_style = {
        'width': '50px', 
        'height': '50px', 
        'borderRadius': '50%', 
        'position': 'absolute',
        'top': '20px',
        'left': '20px',
        'boxShadow': '0 0 15px rgba(0, 0, 0, 0.2)',  # Sombra suave
        'border': '2px solid rgba(255, 255, 255, 0.1)'  # Borde sutil
    }
    
    if n_clicks and n_clicks % 2 == 0:
        circle_style['backgroundColor'] = 'red'
        return mic_url, circle_style
    elif n_clicks:
        circle_style['backgroundColor'] = 'green'
        return mic_url, circle_style
    return mic_url, circle_style

if __name__ == '__main__':
    app.run_server(debug=True)
