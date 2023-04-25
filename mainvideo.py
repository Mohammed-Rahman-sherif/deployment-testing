import requests
import json
import random
import os
import shutil
import yake
import openai
from gtts import gTTS
from translate import Translator
from PIL import Image
from moviepy.editor import *
from threading import Thread

url = "https://api.pexels.com/v1/search"
headers = {"Authorization": "bJVc4AUl6uV1ir8UZ9shca8p3DLHon5hCr92E0FUGVZW0yCUlGHuDMH4"}
openai.api_key = "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"

def generate(prompt):
    response = openai.Completion.create(
        engine = "text-davinci-003",
        prompt = prompt,
        max_tokens = 4000,
        n = 1,
        stop = None,
        temperature = 0.5,
    )
    result = response["choices"][0]["text"]
    words = result.split()
    new_result = " ".join(words)
    return new_result

def delete_files(dir):
    del_dir = dir
    for filename in os.listdir(del_dir):
        file_path = os.path.join(del_dir, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

def generate_audio(content_text, lang):
    for i in range(len(content_text)):
        translator = Translator(to_lang = lang)
        trans_text = translator.translate(content_text[i])
        tts = gTTS(text = trans_text, lang = lang)
        tts.save('audio/a' + str(i + 1) + '.mp3')

def extract_text(text):
    extractedresult = []
    keys_extractor = yake.KeywordExtractor()
    keywords = keys_extractor.extract_keywords(text)
    for keys in keywords:
        extractedresult.append(keys[0])
    return extractedresult

def generate_image(content_text):
    for i in range(len(content_text)):
        return_extracted = extract_text(content_text[i])
        if(len(return_extracted) >= 3):
            extracted_text = random.sample(return_extracted, 3)
        else:
            extracted_text = return_extracted
        dir_name = "image/i" + str(i + 1)
        os.mkdir(dir_name)
        for j in range(len(extracted_text)):
            params = {"query": extracted_text[j], "per_page": 10}
            response = requests.get(url, headers=headers, params=params)
            data = json.loads(response.text)
            img_collection = []
            for k, photo in enumerate(data["photos"]):
                img_url = photo["src"]["medium"]
                img_collection.append(img_url)
            try:
                img = random.choice(img_collection)
            except:
                img = img_url
            img_data = requests.get(img).content
            image_path = "image/i" + str(i + 1) + "/i" + str(i + 1) + str(j + 1) + ".jpg"
            with open(image_path, "wb") as handler:
                handler.write(img_data)
            image = Image.open(image_path)
            resized_img = image.resize((640, 480))
            resized_img.save(image_path)

def generate_video(content_text):
    content_count = len(content_text)
    img_folder = 'image/i'
    for count in range(content_count):
        img_dirs = os.listdir(img_folder + str(count + 1) + "/")
        audio = AudioFileClip('audio/a' + str(count + 1) + ".mp3")
        fourcc = 'mp4v'
        fps = 24
        size = (640, 480)
        img_duration = audio.duration / len(img_dirs)
        video = concatenate([ImageClip(os.path.join(img_folder + str(count + 1) + "/", img_name), duration = img_duration) for img_name in img_dirs], method = 'compose')
        final_clip = video.set_audio(audio)
        final_clip.write_videofile('video/v' + str(count + 1) + '.mp4', codec = 'libx264', fps = fps, audio_codec = 'aac', audio_bitrate = '320k')
    videos_folder = 'video/v'
    first_video = VideoFileClip(videos_folder + str(1) + ".mp4")
    final_video = first_video
    for count in range(2, content_count + 1):
        video_clip = VideoFileClip(videos_folder + str(count) + ".mp4")
        final_video = concatenate_videoclips([final_video, video_clip])
    final_video.write_videofile('final/result_video.mp4', codec = 'libx264', fps = 24, audio_codec = 'aac', audio_bitrate = '320k')

def copy_files():
    src_dirs = ['audio', 'image', 'video', 'final']
    os.mkdir("collections/" + new_query)
    dest_dir = "collections/" + new_query
    for src_dir in src_dirs:
        shutil.copytree(src_dir, os.path.join(dest_dir, os.path.basename(src_dir)))

#content create
query = input("Ask Anything : ")
language = None
while language not in ('ta', 'te', 'en'):
    language = input("Enter 'ta' for Tamil, 'te' for Telugu, 'en' for English : ")
    if language not in ('ta', 'te', 'en'):
        print("Language Context is Invalid!")
specified_element = ["script", "content"]
splitted_query = query.split()
if specified_element[0] in splitted_query or specified_element[1] in splitted_query:
    index = splitted_query.index(specified_element)
    new_query = " ".join(splitted_query[index + 1:])
else:
    new_query = query
final_query = "Act as a youtuber and create a script for the youtube video on " + new_query
content = generate(final_query)
content_split = content.split(".")

#delete files
delete_files("audio")
delete_files("video")
delete_files("final")

shutil.rmtree("image")
os.mkdir("image")

#generate audio and image
t1 = Thread(target = generate_audio, args = (content_split, language))
t2 = Thread(target = generate_image, args = (content_split,))

t1.start()
t2.start()

t1.join()
t2.join()

#video_creation
generate_video(content_split)

#copy generated files to collections
copy_files()