#!/usr/bin/env python

import os
import re
import random
import string

import json
from multiprocessing import Pool
from typing import Union, List
from pydub import AudioSegment

from google.cloud import speech_v1p1beta1 as speech
from google.cloud import storage
from google.cloud.storage import Blob
from google.oauth2 import service_account
from google.api_core.exceptions import GoogleAPIError

import nltk

GOOGLE_CREDENTIALS_FILE = "be-golden-coding-assignment-52b0df1ecd2c.json"
GOOGLE_BUCKET_NAME = "be-golden-bucket"


# ##############################
# # Google Cloud Functionality #
# ##############################
# class TemporaryStorage:
#     """
#     Class for handling the creation and destruction of a file in Google Cloud Storage
#     """
#
#     def __init__(self, bucket_name: str, path_to_file: str):
#         self.path_to_file = path_to_file
#         self.filename = path_to_file
#         self.client = storage.Client(credentials=get_google_credentials())
#         self.bucket = self.client.get_bucket(bucket_name)
#
#         _, file_ext = os.path.splitext(path_to_file)
#         self.blob_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)) + file_ext
#
#     def upload_file(self):
#         try:
#             blob = self.bucket.blob(self.blob_name)
#             blob.upload_from_filename(self.path_to_file)
#             uri = get_blob_uri(blob)
#
#             return uri
#         except GoogleAPIError:
#             print("There is an error with uploading the file. Please check your permissions.")
#             return None
#
#     def delete_file(self):
#         try:
#             blob = self.bucket.blob(self.blob_name)
#             blob.delete()
#         except GoogleAPIError:
#             print("There is an error with deleting the file. Please check your permissions.")
#
#
# def get_google_credentials(credentials_file: str = GOOGLE_CREDENTIALS_FILE):
#     """
#     Creating Google Cloud Speech Credentials from credentials JSON file
#     :param credentials_file: JSON file containing Google Cloud account credential with the correct permissions
#     :return: Google Cloud Credentials
#     """
#     with open(credentials_file) as source:
#         info = json.load(source)
#
#     google_credentials = service_account.Credentials.from_service_account_info(info)
#
#     return google_credentials
#
#
# def create_google_speech_client():
#     """
#     Client for handling Google Cloud Speech Operations
#     :return: Google Cloud Speech SpeechClient
#     """
#     google_client = speech.SpeechClient(credentials=get_google_credentials())
#
#     return google_client
#
#
# def get_blob_uri(blob: Blob):
#     """
#     :param blob: Google Cloud Storage Blob object
#     :return: uri to access from within Google Cloud Storage
#     """
#     return 'gs://' + blob.id[:-(len(str(blob.generation)) + 1)]
#
#
# def call_google_recognize(file_name: str):
#     """
#     Function to handle pushing the file to Google Cloud Storage, calling Google Cloud Speech-to-Text,
#     and returning results
#     :param file_name: string for location of input audio file relative to current file
#     :return: file_name, Google Cloud Speech RecognizeResponse
#     """
#     try:
#         # Create a client
#         client = create_google_speech_client()
#
#         # Create file name
#         file_name = os.path.join(os.path.dirname(__file__), file_name)
#
#         # TemporaryStorage object, get file upload
#         tmp_storage = TemporaryStorage(bucket_name=GOOGLE_BUCKET_NAME, path_to_file=file_name)
#         uri = tmp_storage.upload_file()
#         assert uri is not None
#
#         # Create audio file
#         audio = speech.RecognitionAudio(uri=uri)
#
#         # For audio data
#         extension = os.path.splitext(file_name)[1][1:]
#         audio_data = AudioSegment.from_file(file_name, extension)
#
#         config = speech.RecognitionConfig(
#             encoding=speech.RecognitionConfig.AudioEncoding.MP3,
#             language_code="en-US",
#             enable_word_time_offsets=True,
#             sample_rate_hertz=audio_data.frame_rate,
#             audio_channel_count=audio_data.channels,
#             # For improving results
#             use_enhanced=True,
#             # A model must be specified to use enhanced model.
#             model="phone_call",
#
#         )
#
#         operation = client.long_running_recognize(config=config, audio=audio)
#
#         response = operation.result()
#
#         tmp_storage.delete_file()
#
#         return file_name, response
#     except AssertionError:
#         print("Failure to upload file and get URI")
#     except OSError:
#         print("File does not seem to exist or be accessible.")
#
#
# #####################
# # HIPAA Identifiers #
# #####################
#
# def setup_nltk():
#     """
#     Important libraries to install for nltk in this program
#     """
#     nltk.download('punkt')
#     nltk.download('averaged_perceptron_tagger')
#     nltk.download('maxent_ne_chunker')
#     nltk.download('words')
#
#
# def tokenize_nltk_analyze(sentence: List[str]):
#     """
#     Analyze string sentence, return relevant information about each word
#     :param sentence: String sentence to be analyzed
#     :return: List of tuples of the form (label or 'No label'. word)
#     """
#     word_data = []
#
#     # Breaking sentence down into parts of speech
#     for sent in nltk.sent_tokenize(sentence):
#         # Getting tagged parts of sentence
#         word_tokens = nltk.pos_tag(nltk.word_tokenize(sent))
#         for i, chunk in enumerate(nltk.ne_chunk(word_tokens)):
#             # Using NLTK labels
#             if hasattr(chunk, 'label') and validate_label(chunk.label()):
#                 word_data.append((chunk.label(), ' '.join(c[0] for c in chunk)))
#             # Using Regex to check for email/URL
#             elif word_tokens[i][1] == "CD" or validate_word_email_url(word_tokens[i][1]):
#                 word_data.append(("NUMBER", word_tokens[i][0]))
#             else:
#                 word_data.append(("No label", word_tokens[i][0]))
#
#     return word_data
#
#
# def validate_label(label: str, hipaa_relevant_labels: Union[List[str], None] = None):
#     """
#     Checks for set pattern of labels from NLTK, currently defaults to "GPE" (location) and "PERSON" (name)
#     :param label: label to be checked against
#     :param hipaa_relevant_labels: None means default labels, option to have other labels to search for
#     :return: True if label is one of the hipaa_relevant_labels, False otherwise
#     """
#     if hipaa_relevant_labels is None:
#         hipaa_relevant_labels = ["GPE", "PERSON"]
#     return label in hipaa_relevant_labels
#
#
# def validate_word_email_url(word: str):
#     """
#     Uses regex to determine that word is not an email or a URL
#     :param word: String input word
#     :return: True if word matches either Regex, False otherwise
#     """
#     email_pattern = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
#     url_pattern = re.compile(
#         r'^(?:http|ftp)s?://'  # http:// or https://
#         r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
#         r'localhost|'  # localhost...
#         r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
#         r'(?::\d+)?'  # optional port
#         r'(?:/?|[/?]\S+)$', re.IGNORECASE
#     )
#     return email_pattern.match(word) or url_pattern.match(word)
#
#
# #################
# # Cutting Audio #
# #################
#
# def create_silenced_audio_file(
#         file_name: str,
#         transcriptions: list,
#         words: list,
#         output_name: str = "silenced.mp3"
# ):
#     """
#     Create a silenced audio file
#     :param file_name: Name of original audio file
#     :param transcriptions: List of Transcription created with empty sounds
#     :param words: Words list with time stamps from Google Cloud
#     :param output_name: New audio file name, default is "silenced.mp3"
#     :return: None
#     """
#     # Get the time stamps of words not in transcription
#     empty_times = []
#     for i in range(len(transcriptions)):
#         empty_times.extend(get_silenced_times(transcriptions[i], words[i]))
#     try:
#         extension = os.path.splitext(file_name)[1][1:]
#         audio_data = AudioSegment.from_file(file_name, extension)
#
#         # For each empty stretch of time, replace the audio with silence
#         for empty_time in empty_times:
#             start_time = empty_time[0] * 1000
#             end_time = empty_time[1] * 1000
#             s = AudioSegment.silent(end_time - start_time)
#             audio_data = audio_data[:start_time] + s + audio_data[end_time:]
#
#         audio_data.export(output_name, format=os.path.splitext(output_name)[1][1:])
#         print("Created silenced audio file at {}".format(output_name))
#     except OSError:
#         print("Could not access or create file.")
#
#
# def get_silenced_times(transcription: str, words: list):
#     """
#     Get time regions where silence should exist
#     :param transcription: Transcription created with empty sounds
#     :param words: Words list with time stamps from Google Cloud
#     :return: List of tuples of start_time, end_tim
#     """
#     empty_times = []
#     transcription_words = transcription.split()
#     for word_info in words:
#         word = word_info.word
#         if word not in transcription_words:
#             empty_times.append((word_info.start_time.total_seconds(), word_info.end_time.total_seconds()))
#     return empty_times
#
#
# def transcribe_audio(
#         file_name: str,
#         remove_hipaa_identifiers: bool = False,
#         create_silenced_audio_file_bool: bool = False,
#         silenced_audio_filename: str = "silenced.mp3"
# ):
#     """
#     Function for transcribing audio, either through print or into a file
#     :param file_name: Required, the name of the input file
#     :param remove_hipaa_identifiers: Boolean, determines whether to remove HIPAA identifiers in transcription
#     :param create_silenced_audio_file_bool: Boolean, determines whether to remove HIPAA identifiers in audio file
#     :param silenced_audio_filename: String, file for output if create_silenced_audio_file_bool
#     :return: file_name, transcription of audio
#     """
#     try:
#         # Set up multiprocessing
#         print("Waiting for operation to complete...")
#         response = call_google_recognize(file_name)
#         assert response is not None
#
#         if remove_hipaa_identifiers:
#             setup_nltk()
#
#         transcription = []
#         word_times = []
#         # Each result is for a consecutive portion of the audio. Iterate through
#         # them to get the transcripts for the entire audio file.
#         for i, result in enumerate(response[1].results):
#             # The first alternative is the most likely one for this portion.
#             transcript = result.alternatives[0].transcript
#
#             if remove_hipaa_identifiers or create_silenced_audio_file_bool:
#                 tmp_transcript = ' '.join([
#                     token[1] if token[0] == "No label" else "_" * len(token[1])
#                     for token in tokenize_nltk_analyze(transcript)
#                 ])
#                 if create_silenced_audio_file_bool:
#                     word_times.append(result.alternatives[0].words)
#
#                 if remove_hipaa_identifiers:
#                     transcription.append(tmp_transcript)
#                 else:
#                     transcription.append(transcript)
#             else:
#                 transcription.append(transcript)
#
#         if create_silenced_audio_file_bool:
#             create_silenced_audio_file(
#                 file_name,
#                 transcription,
#                 word_times,
#                 silenced_audio_filename
#             )
#
#         return file_name, transcription
#     except AssertionError:
#         print("Unable to transcribe. Please check your file and your permissions.")
#         return None, None
#     except OSError:
#         print("Unable to write to file.")
#         return None, None
#
#
# def audio_transcription_handler_with_multiprocessing(
#         files: Union[str, list],
#         remove_hipaa_identifiers: bool = False,
#         create_silenced_audio_file_bool: bool = False
# ):
#     """
#     Handles individual audio file or list of files, sets up multiprocessing
#     :param files: one string or list of strings, must point to audio files
#     :param remove_hipaa_identifiers: Boolean, determines whether to remove HIPAA identifiers in transcription
#     :param create_silenced_audio_file_bool: Boolean, determines whether to remove HIPAA identifiers in audio file
#     :return:
#     """
#     if type(files) == str:
#         files = [files]
#     results = Pool(len(files)).starmap(
#         transcribe_audio,
#         zip(files, [remove_hipaa_identifiers] * len(files), [create_silenced_audio_file_bool] * len(files)),
#     )
#     transcription = {key: value for key, value in zip(
#         [item[0] for item in results], [item[1] for item in results]
#     )}
#     return transcription
#
#
# def transcribe_audio_wrapper_1(file_name: str = "Intern_Demo.mp3"):
#     try:
#         transcription = audio_transcription_handler_with_multiprocessing(file_name)
#         assert transcription is not None
#
#         for name in transcription.keys():
#             print(name)
#             for i, transcript in enumerate(transcription[name]):
#                 print("Line {}: {}".format(i, transcript))
#     except AssertionError:
#         print("Failure to transcribe")
#
#
# def transcribe_audio_wrapper_2(file_name: str = "Intern_Demo.mp3"):
#     try:
#         transcription = audio_transcription_handler_with_multiprocessing(file_name, True)
#         assert transcription is not None
#
#         for name in transcription.keys():
#             print(name)
#             for i, transcript in enumerate(transcription[name]):
#                 print("Line {}: {}".format(i, transcript))
#     except AssertionError:
#         print("Failure to transcribe")
#
#
# def transcribe_audio_wrapper_3(file_name: str = "Intern_Demo.mp3"):
#     try:
#         transcription = audio_transcription_handler_with_multiprocessing(file_name, True, True)
#         assert transcription is not None
#
#         for name in transcription.keys():
#             print(name)
#             for i, transcript in enumerate(transcription[name]):
#                 print("Line {}: {}".format(i, transcript))
#     except AssertionError:
#         print("Failure to transcribe")
#
#
# if __name__ == '__main__':
#     # For problem 1
#     print("Problem 1")
#     transcribe_audio_wrapper_1()
#     print()
#
#     # For problem 2
#     print("Problem 2")
#     transcribe_audio_wrapper_2()
#     print()
#
#     # For problem 3
#     print("Problem 3")
#     transcribe_audio_wrapper_3()
#     print()
#
#     # Extra experiments
#
#     # Testing out multiprocessing
#     # transcribe_audio(["Intern_Demo.mp3", "Intern_Demo.mp3", "Intern_Demo.mp3", "Intern_Demo.mp3"])
