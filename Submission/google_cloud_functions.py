#!/usr/bin/env python

import random
import string
import os
import json

from pydub import AudioSegment

from google.cloud import speech_v1p1beta1 as speech
from google.cloud import storage
from google.cloud.storage import Blob
from google.oauth2 import service_account
from google.api_core.exceptions import GoogleAPIError

GOOGLE_CREDENTIALS_FILE = "be-golden-coding-assignment-52b0df1ecd2c.json"
GOOGLE_BUCKET_NAME = "be-golden-bucket"


class TemporaryStorage:
    """
    Class for handling the creation and destruction of a file in Google Cloud Storage
    """

    def __init__(self, bucket_name: str, path_to_file: str):
        self.path_to_file = path_to_file
        self.filename = path_to_file
        self.client = storage.Client(credentials=get_google_credentials())
        self.bucket = self.client.get_bucket(bucket_name)

        _, file_ext = os.path.splitext(path_to_file)
        self.blob_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)) + file_ext

    def upload_file(self):
        try:
            blob = self.bucket.blob(self.blob_name)
            blob.upload_from_filename(self.path_to_file)
            uri = get_blob_uri(blob)

            return uri
        except GoogleAPIError:
            print("There is an error with uploading the file. Please check your permissions.")
            return None

    def delete_file(self):
        try:
            blob = self.bucket.blob(self.blob_name)
            blob.delete()
        except GoogleAPIError:
            print("There is an error with deleting the file. Please check your permissions.")


def get_google_credentials(credentials_file: str = GOOGLE_CREDENTIALS_FILE):
    """
    Creating Google Cloud Speech Credentials from credentials JSON file
    :param credentials_file: JSON file containing Google Cloud account credential with the correct permissions
    :return: Google Cloud Credentials
    """
    with open(credentials_file) as source:
        info = json.load(source)

    google_credentials = service_account.Credentials.from_service_account_info(info)

    return google_credentials


def create_google_speech_client():
    """
    Client for handling Google Cloud Speech Operations
    :return: Google Cloud Speech SpeechClient
    """
    google_client = speech.SpeechClient(credentials=get_google_credentials())

    return google_client


def get_blob_uri(blob: Blob):
    """
    :param blob: Google Cloud Storage Blob object
    :return: uri to access from within Google Cloud Storage
    """
    return 'gs://' + blob.id[:-(len(str(blob.generation)) + 1)]


def call_google_recognize(file_name: str):
    """
    Function to handle pushing the file to Google Cloud Storage, calling Google Cloud Speech-to-Text,
    and returning results
    :param file_name: string for location of input audio file relative to current file
    :return: file_name, Google Cloud Speech RecognizeResponse
    """
    try:
        # Create a client
        client = create_google_speech_client()

        # Create file name
        file_name = os.path.join(os.path.dirname(__file__), file_name)

        # TemporaryStorage object, get file upload
        tmp_storage = TemporaryStorage(bucket_name=GOOGLE_BUCKET_NAME, path_to_file=file_name)
        uri = tmp_storage.upload_file()
        assert uri is not None

        # Create audio file
        audio = speech.RecognitionAudio(uri=uri)

        # For audio data
        extension = os.path.splitext(file_name)[1][1:]
        audio_data = AudioSegment.from_file(file_name, extension)

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.MP3,
            language_code="en-US",
            enable_word_time_offsets=True,
            sample_rate_hertz=audio_data.frame_rate,
            audio_channel_count=audio_data.channels,
            # For improving results
            use_enhanced=True,
            # A model must be specified to use enhanced model.
            model="phone_call",

        )

        operation = client.long_running_recognize(config=config, audio=audio)

        response = operation.result()

        tmp_storage.delete_file()

        return file_name, response
    except AssertionError:
        print("Failure to upload file and get URI")
    except OSError as e:
        print("File does not seem to exist or be accessible.")
        print(e)
