#!/usr/bin/env python

import nltk
import re

from typing import Union, List


def setup_nltk():
    """
    Important libraries to install for nltk in this program
    """
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('maxent_ne_chunker')
    nltk.download('words')


def tokenize_nltk_analyze(sentence: List[str]):
    """
    Analyze string sentence, return relevant information about each word
    :param sentence: String sentence to be analyzed
    :return: List of tuples of the form (label or 'No label'. word)
    """
    word_data = []

    # Breaking sentence down into parts of speech
    for sent in nltk.sent_tokenize(sentence):
        # Getting tagged parts of sentence
        word_tokens = nltk.pos_tag(nltk.word_tokenize(sent))
        for i, chunk in enumerate(nltk.ne_chunk(word_tokens)):
            # Using NLTK labels
            if hasattr(chunk, 'label') and validate_label(chunk.label()):
                word_data.append((chunk.label(), ' '.join(c[0] for c in chunk)))
            # Using Regex to check for email/URL
            elif word_tokens[i][1] == "CD" or validate_word_email_url(word_tokens[i][1]):
                word_data.append(("NUMBER", word_tokens[i][0]))
            else:
                word_data.append(("No label", word_tokens[i][0]))

    return word_data


def validate_label(label: str, hipaa_relevant_labels: Union[List[str], None] = None):
    """
    Checks for set pattern of labels from NLTK, currently defaults to "GPE" (location) and "PERSON" (name)
    :param label: label to be checked against
    :param hipaa_relevant_labels: None means default labels, option to have other labels to search for
    :return: True if label is one of the hipaa_relevant_labels, False otherwise
    """
    if hipaa_relevant_labels is None:
        hipaa_relevant_labels = ["GPE", "PERSON"]
    return label in hipaa_relevant_labels


def validate_word_email_url(word: str):
    """
    Uses regex to determine that word is not an email or a URL
    :param word: String input word
    :return: True if word matches either Regex, False otherwise
    """
    email_pattern = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
    url_pattern = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    return email_pattern.match(word) or url_pattern.match(word)
