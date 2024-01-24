import secrets


def generate_otp():
    return ''.join(secrets.choice("0123456789") for _ in range(6))


