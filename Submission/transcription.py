#!/usr/bin/env python

from multiprocessing import Pool
from typing import Union

from google_cloud_functions import call_google_recognize
from hipaa_identification import setup_nltk, tokenize_nltk_analyze
from audio_silence import create_silenced_audio_file


def transcribe_audio(
        file_name: str,
        remove_hipaa_identifiers: bool = False,
        create_silenced_audio_file_bool: bool = False,
        silenced_audio_filename: str = "silenced.mp3"
):
    """
    Function for transcribing audio, either through print or into a file
    :param file_name: Required, the name of the input file
    :param remove_hipaa_identifiers: Boolean, determines whether to remove HIPAA identifiers in transcription
    :param create_silenced_audio_file_bool: Boolean, determines whether to remove HIPAA identifiers in audio file
    :param silenced_audio_filename: String, file for output if create_silenced_audio_file_bool
    :return: file_name, transcription of audio
    """
    try:
        # Set up multiprocessing
        print("Waiting for operation to complete...")
        response = call_google_recognize(file_name)
        assert response is not None

        if remove_hipaa_identifiers:
            setup_nltk()

        transcription = []
        word_times = []
        # Each result is for a consecutive portion of the audio. Iterate through
        # them to get the transcripts for the entire audio file.
        for i, result in enumerate(response[1].results):
            # The first alternative is the most likely one for this portion.
            transcript = result.alternatives[0].transcript

            if remove_hipaa_identifiers or create_silenced_audio_file_bool:
                tmp_transcript = ' '.join([
                    token[1] if token[0] == "No label" else "_" * len(token[1])
                    for token in tokenize_nltk_analyze(transcript)
                ])
                if create_silenced_audio_file_bool:
                    word_times.append(result.alternatives[0].words)

                if remove_hipaa_identifiers:
                    transcription.append(tmp_transcript)
                else:
                    transcription.append(transcript)
            else:
                transcription.append(transcript)

        if create_silenced_audio_file_bool:
            create_silenced_audio_file(
                file_name,
                transcription,
                word_times,
                silenced_audio_filename
            )

        return file_name, transcription
    except AssertionError:
        print("Unable to transcribe. Please check your file and your permissions.")
        return None, None
    except OSError:
        print("Unable to write to file.")
        return None, None


def audio_transcription_handler_with_multiprocessing(
        files: Union[str, list],
        remove_hipaa_identifiers: bool = False,
        create_silenced_audio_file_bool: bool = False
):
    """
    Handles individual audio file or list of files, sets up multiprocessing
    :param files: one string or list of strings, must point to audio files
    :param remove_hipaa_identifiers: Boolean, determines whether to remove HIPAA identifiers in transcription
    :param create_silenced_audio_file_bool: Boolean, determines whether to remove HIPAA identifiers in audio file
    :return:
    """
    if type(files) == str:
        files = [files]
    results = Pool(len(files)).starmap(
        transcribe_audio,
        zip(files, [remove_hipaa_identifiers] * len(files), [create_silenced_audio_file_bool] * len(files)),
    )
    transcription = {key: value for key, value in zip(
        [item[0] for item in results], [item[1] for item in results]
    )}
    return transcription
