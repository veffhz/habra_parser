import re

from datetime import timedelta
from collections import OrderedDict


def clean_word(word):
    """cleat text of special characters"""
    return re.sub('[^a-zа-я]+', '', word.lower())


def group_by_weeks(data):
    grouped = OrderedDict()
    for item in data:
        delta = timedelta(days=-item.weekday(), weeks=1)
        monday = item + delta
        if monday in grouped:
            grouped[monday].extend(data[item])
        else:
            grouped[monday] = data[item]
    return grouped
