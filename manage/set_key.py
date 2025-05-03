from cryptography.fernet import Fernet

def generate_key():
    key = Fernet.generate_key()
    with open('key/secret.key','wb') as key_file:
        key_file.write(key)

def load_key():
    with open('key/secret.key','rb') as key_file:
        return key_file.read()