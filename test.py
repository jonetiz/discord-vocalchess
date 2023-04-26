from client import *
import os
from dotenv import load_dotenv
from chess_functions import DiscordChessGame, ChessPlayer
import time

import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
import io

#import PyWave as wave

r = sr.Recognizer()
def speech_to_tex(audio_bytes: io.BytesIO | str):
    """Convert speech to text using google speech recognition."""

    # discord passes oddly formatted, we need to resave it
    sound_conversion = AudioSegment.from_file(audio_bytes)

    converted_audio = io.BytesIO()
    sound_conversion.export(converted_audio, format='wav')

    text = ""
    with sr.AudioFile(converted_audio) as source:
        try:
            audio_listened = r.record(source)
            try:
                text = r.recognize_sphinx(audio_listened, language = 'en-US', show_all=True)
                print(text)
                #text = text['alternative'][0]['transcript']
            except sr.UnknownValueError as e:
                text = "*inaudible*"
            except Exception as e: 
                print(e)
        except:
            text = ""

    return text

with open('asd.mp3', 'rb') as f:
    print(speech_to_tex(f))