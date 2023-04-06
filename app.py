from fastapi import FastAPI, Request, Form
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from main import YouTubeTranscribe as YT
import MediaUpload as yt
import os
import glob

directory_path = 'Media/Result/'

app = FastAPI()
templates = Jinja2Templates(directory="templates/")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.post("/download")
def calculate(request: Request, operation: str = Form(...), link: str = Form(...), language: str = Form(...)):
    if operation == "download_video":
        print(link)
        print(language)
        result = YT.download_video(link=link)
        result = YT.extract_audio()
        result = YT.transcribe_audio()
        result = YT.translate_file(language)
        result = YT.speak_text(language)
        result = YT.connect_wave()
        result = YT.merge_audio_video()
    else:
        result = "Invalid operation"
    return templates.TemplateResponse("index1.html", {"request": request, "result": result})
    #return templates.TemplateResponse("hom.html", {"request": request, "result": result})

'''@app.post("/videoupload")
def ProcessSelection(request: Request, operation: str = Form(...), VideoTitle: str = Form(...), VideoDescription: str = Form(...), VideoKeywords: str = Form(...), VideoPrivacyStatus: str = Form(...)):
    if operation == "download_video":
        print(VideoTitle)
        list_of_files = glob.glob(directory_path + '/*')
        list_of_files.sort(key=os.path.getctime)
        result = list_of_files[-1]
        id = yt.UploadVideoInYT(result, VideoTitle, VideoDescription, VideoKeywords, VideoPrivacyStatus)
        print(id)
        yt.UploadThumnailInYT(id)  
        result = yt.SendMail(id)
    return templates.TemplateResponse("ytresult.html", {"request": request, "result": result}) #
'''
@app.get('/result')
def result_mp4():
    #video_path = "Media/Result/ZuYuY.mp4"
    list_of_files = glob.glob(directory_path + '/*')
    list_of_files.sort(key=os.path.getctime)
    result = list_of_files[-1]
    return FileResponse(result, media_type='video/mp4', filename='video.mp4')