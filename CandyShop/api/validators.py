from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator


def correct_time(string):
    string = string.split(':')
    if len(string) != 2:
        return False

    try:
        hours = int(string[0])
        if hours < 0 or hours > 23:
            return False
        minutes = int(string[1])
        if minutes < 0 or minutes > 59:
            return False
    except:
        return False

    return True


def validate_working_time(value):
    error = ValidationError("Неправильный формат даты")
    value = value.split('-')
    if len(value) != 2:
        raise error

    if not (correct_time(value[0]) and correct_time(value[1])):
        raise error


def validate_hours(arr):
    for item in arr:
        validate_working_time(item)


def validate_regions(arr):
    for item in arr:
        MinValueValidator(item)
