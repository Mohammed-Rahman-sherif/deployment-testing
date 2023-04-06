import argparse
import json
import math
import subprocess as sp
import sys
import tempfile
from pathlib import Path
import wave_1 as WV

import cairo
import numpy as np
import tqdm

import os
import random
import string
import concurrent.futures
from gtts import gTTS
from pytube import YouTube
import speech_recognition as sr
from playsound import playsound
from translate import Translator
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips

name = ''.join(random.choices(string.ascii_letters, k=5))
video_file = f"{name}.mp4"
audio_file = f"{name}.wav"
path: str = "Media/Downloads" 
audio_path: str = "Audio/Original"
input_file_path: str = f'Contents/Original/{name}.txt'
_is_main = False

class YouTubeTranscribe:
    def __init__(self, link: str, path: str = "../Media", audio_path: str = "../Audio/Original"):
        self.path = path
        self.audio_path = audio_path
        self.transcribed_text = ""
        #self.download_video()
        #self.extract_audio()
        #self.transcribe_audio()

        self.option = input("Enter 'ta' for Tamil, 'te' for Telugu, 'zh-cn' for Chinese: ")
        self.translate_file(f'../Contents/{self.name}.txt', self.option)
        self.speak_text(self.translation.text)
        #self.allign()

    def download_video(link):
        try:
            youtube = YouTube(link)
            video_stream = youtube.streams.get_highest_resolution()
            video_file = f"{name}.mp4"
            video_stream.download(output_path=path, filename=video_file)
            print('Video download complete.')
        except Exception as e:
            print(f"An error occurred while downloading the video: {e}")

    def extract_audio():
        try:            
            video = VideoFileClip(os.path.join(path, video_file))
            audio = video.audio
            duration = video.duration
            #print('Duration: ', duration)
            audio.write_audiofile(os.path.join(audio_path, audio_file))
            print('Audio extraction complete.')
        except Exception as e:
            print(f"An error occurred while extracting the audio: {e}")

    def transcribe_audio():
        try:
            r = sr.Recognizer()
            counter = 0
            failed_counter = 0
            with sr.AudioFile(os.path.join(audio_path, audio_file)) as source:
                r.adjust_for_ambient_noise(source)
                audio = r.record(source)
                duration = len(audio.get_wav_data()) / audio.sample_rate / audio.sample_width
                chunk_duration = 60  # duration of each chunk in seconds
                offset = 0  # starting point of the first chunk
                transcribed_text = ""

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = []
                    while offset < duration:
                        with sr.AudioFile(os.path.join(audio_path, audio_file)) as source:
                            audio_chunk = r.record(source, offset=offset, duration=chunk_duration)
                            if offset < duration:
                                futures.append(executor.submit(
                                    lambda x: r.recognize_google(x),
                                    audio_chunk))
                            offset += chunk_duration

                    for future in concurrent.futures.as_completed(futures):
                        try:
                            result = future.result()
                            transcribed_text += result + "\n"
                            counter += 1
                        except sr.UnknownValueError:
                            print("Could not understand audio, skipping chunk...")
                            failed_counter += 1

                with open(os.path.join("Contents/Original", f"{name}.txt"), "w") as file:
                    file.write(transcribed_text)

                #print(transcribed_text)
                print("Total chunks processed:", counter)
                print("Total chunks failed:", failed_counter)
                print('Audio Transcription complete.')

        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

        return ""

    def translate_file(dest_language):
        max_query_length = 500
        #print(dest_language)
        try:
            translator = Translator(to_lang=dest_language)
            #print('Translation complete')

            # Read the input text document
            with open(input_file_path, 'r') as f:
                text = f.read()

            segments = [text[i:i+max_query_length] for i in range(0, len(text), max_query_length)]

            translated_text = ''
            for segment in segments:
                translated_segment = translator.translate(segment)
                translated_text += translated_segment

            output_file_path = f'Contents/{dest_language}/{name}.txt'
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(translated_text)

            # Print a success message
            print(f'Text Translation complete. Output file saved to {os.path.abspath(output_file_path)}.')    

        except Exception as e:
            print(f'An error occurred while translating the file: {e}')

    def speak_text(dest_language, path: str = "Audio/Translated"):
        text_input = f'Contents/{dest_language}/{name}.txt'
        try:
            with open(text_input, 'r', encoding='utf-8') as f:
                text = f.read()
            tts = gTTS(text, lang=dest_language)
            tts.save(os.path.join(path, name + '.mp3'))
            #print(os.path.join(path, self.name + '.mp3'))
            #playsound(os.path.join(path, self.name + '.mp3'))
            print('Text to audio complete.')
        
        except Exception as e:
            print(f'An error occured while generating translated audio: {e}')
            
    def allign():
        #import words7inaline as w
        #w.format_text(f'/Contents/Original/{name}.txt')
        return

    def connect_wave():
        WV.generate_wave(audio_path = Path(f'Audio/Translated/{name}.mp3'), output_path= Path(f'Media/Waves/{name}.mp4'))
        print('Waveform generation complete.')

    def merge_audio_video(audio_path = f'Audio/Translated/{name}.mp3', video_path=f'Media/Waves/{name}.mp4', output_path = f'Media/Result/{name}.mp4'):
        video = VideoFileClip(video_path)
        audio = AudioFileClip(audio_path)
        audio = audio.set_duration(video.duration)
        final_clip = video.set_audio(audio)
        final_clip.write_videofile(output_path, codec="libxvid")
        print(f'Your video is ready! Output file saved to {os.path.abspath(output_path)}.')
        return output_path

if __name__ == "__main__":
    youtube_transcribe = YouTubeTranscribe("https://youtu.be/mZ4Mt7VzELA")
