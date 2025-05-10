from cryptography.fernet import Fernet
import manage.set_key
import os

def encrypt_file(input_file,output_file):
    key = manage.set_key.load_key()
    f = Fernet(key)
    
    with open(input_file,'rb') as f_in:
        data = f_in.read()

    encrypted = f.encrypt(data)

    with open(output_file,'wb') as f_out:
        f_out.write(encrypted)
    os.remove(input_file)
    print('Encode')

def decrypt_file(input_file,output_file):
    key = manage.set_key.load_key()
    f = Fernet(key)

    with open(input_file,'rb') as f_in:
        encrypted_data = f_in.read()
        
    decrypted = f.decrypt(encrypted_data)
    
    with open(output_file,'wb') as f_out:
        f_out.write(decrypted)
    print('Decode')


