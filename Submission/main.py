#!/usr/bin/env python

from transcription import audio_transcription_handler_with_multiprocessing


def transcribe_audio_wrapper_1(file_name: str = "Intern_Demo.mp3"):
    try:
        transcription = audio_transcription_handler_with_multiprocessing(file_name)
        assert transcription is not None

        for name in transcription.keys():
            print(name)
            for i, transcript in enumerate(transcription[name]):
                print("Line {}: {}".format(i, transcript))
    except AssertionError:
        print("Failure to transcribe")
    except TypeError:
        print("Failure to transcribe")


def transcribe_audio_wrapper_2(file_name: str = "Intern_Demo.mp3"):
    try:
        transcription = audio_transcription_handler_with_multiprocessing(file_name, True)
        assert transcription is not None

        for name in transcription.keys():
            print(name)
            for i, transcript in enumerate(transcription[name]):
                print("Line {}: {}".format(i, transcript))
    except AssertionError:
        print("Failure to transcribe")
    except TypeError:
        print("Failure to transcribe")


def transcribe_audio_wrapper_3(file_name: str = "Intern_Demo.mp3"):
    try:
        transcription = audio_transcription_handler_with_multiprocessing(file_name, True, True)
        assert transcription is not None

        for name in transcription.keys():
            print(name)
            for i, transcript in enumerate(transcription[name]):
                print("Line {}: {}".format(i, transcript))
    except AssertionError:
        print("Failure to transcribe")
    except TypeError:
        print("Failure to transcribe")


if __name__ == '__main__':
    # For problem 1
    print("Problem 1")
    transcribe_audio_wrapper_1()
    print()

    # For problem 2
    print("Problem 2")
    transcribe_audio_wrapper_2()
    print()

    # For problem 3
    print("Problem 3")
    transcribe_audio_wrapper_3()
    print()

    # Extra experiments

    # Testing out multiprocessing
    # transcribe_audio(["Intern_Demo.mp3", "Intern_Demo.mp3", "Intern_Demo.mp3", "Intern_Demo.mp3"])
