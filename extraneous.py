# def print_response_results(response: RecognizeResponse):
#     """
#     Print out most useful results from response object
#     :param response: Recognize Response object
#     :return: None
#     """
#     # Each result is for a consecutive portion of the audio. Iterate through
#     # them to get the transcripts for the entire audio file.
#     for result in response.results:
#         # The first alternative is the most likely one for this portion.
#         print()
#         alternative = result.alternatives[0]
#         print("Transcript: {}".format(alternative.transcript))
#         print("Confidence: {}".format(alternative.confidence))
#
#         for word_info in alternative.words:
#             word = word_info.word
#             start_time = word_info.start_time
#             end_time = word_info.end_time
#
#             print(
#                 f"Word: {word}, start_time: {start_time.total_seconds()}, end_time: {end_time.total_seconds()}"
#             )
#
#         print()
#
#     # Handle the response
#     print(response)
#     print(response.results)
