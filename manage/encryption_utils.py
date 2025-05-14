from cryptography.fernet import Fernet
import manage.set_key
import atexit
import os

def delete_later(path):
    def remove_file():
        try:
            os.remove(path)
            print(f"Deleted on exit: {path}")
        except Exception as e:
            print(f"Still could not delete {path}: {e}")
    atexit.register(remove_file)

def encrypt_file(input_file,output_file):
    key = manage.set_key.load_key()
    f = Fernet(key)
    
    with open(input_file,'rb') as f_in:
        data = f_in.read()

    encrypted = f.encrypt(data)

    with open(output_file,'wb') as f_out:
        f_out.write(encrypted)

    delete_later(input_file)

    # try:
    #     os.remove(input_file)
    #     print('Encode and delete original file')
    # except Exception as e:
    #     print(f'Encode done, but failed to delete original file: {e}')

def decrypt_file(input_file,output_file):
    key = manage.set_key.load_key()
    f = Fernet(key)

    with open(input_file,'rb') as f_in:
        encrypted_data = f_in.read()
        
    decrypted = f.decrypt(encrypted_data)
    
    with open(output_file,'wb') as f_out:
        f_out.write(decrypted)
    print('Decode')


