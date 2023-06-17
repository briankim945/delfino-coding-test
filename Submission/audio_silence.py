#!/usr/bin/env python

import os
from pydub import AudioSegment


def create_silenced_audio_file(
        file_name: str,
        transcriptions: list,
        words: list,
        output_name: str = "silenced.mp3"
):
    """
    Create a silenced audio file
    :param file_name: Name of original audio file
    :param transcriptions: List of Transcription created with empty sounds
    :param words: Words list with time stamps from Google Cloud
    :param output_name: New audio file name, default is "silenced.mp3"
    :return: None
    """
    # Get the time stamps of words not in transcription
    empty_times = []
    for i in range(len(transcriptions)):
        empty_times.extend(get_silenced_times(transcriptions[i], words[i]))
    try:
        extension = os.path.splitext(file_name)[1][1:]
        audio_data = AudioSegment.from_file(file_name, extension)

        # For each empty stretch of time, replace the audio with silence
        for empty_time in empty_times:
            start_time = empty_time[0] * 1000
            end_time = empty_time[1] * 1000
            s = AudioSegment.silent(end_time - start_time)
            audio_data = audio_data[:start_time] + s + audio_data[end_time:]

        audio_data.export(output_name, format=os.path.splitext(output_name)[1][1:])
        print("Created silenced audio file at {}".format(output_name))
    except OSError:
        print("Could not access or create file.")


def get_silenced_times(transcription: str, words: list):
    """
    Get time regions where silence should exist
    :param transcription: Transcription created with empty sounds
    :param words: Words list with time stamps from Google Cloud
    :return: List of tuples of start_time, end_tim
    """
    empty_times = []
    transcription_words = transcription.split()
    for word_info in words:
        word = word_info.word
        if word not in transcription_words:
            empty_times.append((word_info.start_time.total_seconds(), word_info.end_time.total_seconds()))
    return empty_times
