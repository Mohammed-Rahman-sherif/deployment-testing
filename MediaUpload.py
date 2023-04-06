import httplib2
import os
import os.path
import sys
import random
import time
import google.auth
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from google_auth_oauthlib.flow import InstalledAppFlow
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage 
from oauth2client.tools import argparser, run_flow
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


def UploadVideoInYT(VideoFile, VideoTitle, VideoDescription, VideoKeywords, VideoPrivacyStatus = "public", VideoCategory = 22):
    tags = None
    if VideoKeywords:
        tags = VideoKeywords.split(",")
    response = None
    error = None
    retry = 0

    body = dict(
        snippet = dict(
            title = VideoTitle,
            description = VideoDescription,
            tags = tags,
            categoryId = VideoCategory
        ),
        status = dict(
            privacyStatus = VideoPrivacyStatus
        )
    )

    insert_request = youtube.videos().insert(
        part = ",".join(body.keys()),
        body = body,
        media_body = MediaFileUpload(VideoFile, chunksize=-1, resumable=True)
    )

    while response is None:
        try:
            print("Uploading file...")
            status, response = insert_request.next_chunk()

            if response is not None:
                if 'id' in response:
                    print("Video id '%s' was successfully uploaded." % response['id'])
                    VideoId = response['id']
                    return VideoId
                else:
                    exit("The upload failed with an unexpected response: %s" % response)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                                e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: %s" % e

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit("No longer attempting to retry.")

        max_sleep = 2 ** retry
        sleep_seconds = random.random() * max_sleep
        print("Sleeping %f seconds and then retrying..." % sleep_seconds)
        time.sleep(sleep_seconds)

def UploadThumnailInYT(VideoId):
    ThumbnailPath = "hello.jpg"
    try:
        youtube.thumbnails().set(
            videoId = VideoId,
            media_body = MediaFileUpload(ThumbnailPath)
        ).execute()
    except:
        print("Your Youtube channel is unverified so that you cannot upload custom Thumbnails." + "\n" +
                "You need to verify your account to upload Thumbnail." + "\n" +
                "You can do this by navigating to YouTube > clicking your profile icon > Settings > Channel status and features > Channel > Feature eligibility > Intermediate features.")

def SendMail(VideoId):
    msglink = 'http://www.youtube.com/watch?v=' + VideoId
    msg = MIMEMultipart()
    msg['From'] = 'lp8511701@gmail.com'
    msg['To'] = 'smartsherif1503@gmail.com'
    msg['Subject'] = 'Youtube Video Uploaded Successfully'
    msg.attach(MIMEText('Your AI generated video have been successfully uploaded.' + '\n' + 
                        'You can check your video by clicking this link : ' + '\n' + msglink))

    smtp_server = 'smtp.gmail.com'
    port = 587
    username = 'lp8511701@gmail.com'
    password = 'lxme qvhc xiew yami'
    try:
        server = smtplib.SMTP(smtp_server,port)
        server.starttls()
        server.login(username,password)
        text = msg.as_string()
        server.sendmail('lp8511701@gmail.com','smartsherif1503@gmail.com', text)
        print('Email sent successfully!')
    except Exception as e:
        print('Something went wrong:', e)
    finally:
        server.quit()
    return msglink

httplib2.RETRIES = 1
MAX_RETRIES = 10
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

CLIENT_SECRETS_FILE = "client_secret_new.json"
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
MISSING_CLIENT_SECRETS_MESSAGE = os.path.abspath(os.path.join(os.path.dirname(__file__), CLIENT_SECRETS_FILE))
VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")

flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_UPLOAD_SCOPE, message=MISSING_CLIENT_SECRETS_MESSAGE)
storage = Storage("MediaUpload.py-oauth2.json")
credentials = storage.get()
if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage)

youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=credentials.authorize(httplib2.Http()))
