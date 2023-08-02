# header
from fastapi import FastAPI, File, UploadFile, Response
import requests
import openai
import speech_recognition as sr
from googletrans import Translator
from configs import config

# deklarasi
app = FastAPI()
translator = Translator()
r = sr.Recognizer()
openai.api_key = config.api_key_openai

# function
def chat(pesan: str):
    response = openai.Completion.create(
        model="text-davinci-003",
       prompt=pesan
    )
    output = response['choices'][0]['text']
    return output

def request_audio(text):
    url = 'https://deprecatedapis.tts.quest/v2/voicevox/audio/'
    params = {
        'key': config.api_key_voicevox,
        'speaker': '0',
        'pitch': '0',
        'intonationScale': '1',
        'speed': '1',
        'text': text
    }
    response = requests.get(url, params=params)
    return response.content

# endpoint
@app.post("/talk/{language_used}")
async def talk(language_used: str, audio_talk: UploadFile = File(...)):
    with sr.AudioFile(audio_talk.file) as audio_file:
        audio_data = r.record(audio_file)
        transcript = r.recognize_google(audio_data, language=language_used)
    jawaban = chat(pesan=transcript)
    translation = translator.translate(jawaban, dest='ja')
    audio_response = request_audio(text=translation.text)
    return Response(content=audio_response, media_type="audio/wav")

@app.websocket("/websocket-talk/{language_used}")
async def talk(websocket: WebSocket, language_used: str):
    await websocket.accept()
    try:
        while True:
            audio_data = await websocket.receive_bytes()
            with sr.AudioData(audio_data) as audio:
                transcript = r.recognize_google(audio, language=language_used)
            jawaban = chat(pesan=transcript)
            translation = translator.translate(jawaban, dest='ja')
            audio_response = request_audio(text=translation.text)
            await websocket.send_bytes(audio_response)
    except WebSocketDisconnect:
        pass
