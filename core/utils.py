from django.utils.crypto import get_random_string


def generate_password():
    generated_password = get_random_string(
        12,
        allowed_chars="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*(-_=+)",
    )

    return generated_password


def normalize_string(input_string):
    normalized_string = input_string.lower()
    normalized_string = normalized_string.strip()

    return normalized_string
