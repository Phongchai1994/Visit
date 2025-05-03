from cryptography.fernet import Fernet
import manage.set_key as set_key
import os

EN_DB = 'data/visit_report.db.enc'
DE_DB = 'data/visit_report.db'

def encrypt_file_onetime(input_file,output_file):
    key = set_key.load_key()
    f = Fernet(key)
    
    with open(input_file,'rb') as f_in:
        data = f_in.read()

    encrypted = f.encrypt(data)

    with open(output_file,'wb') as f_out:
        f_out.write(encrypted)
    os.remove(input_file)
    print('Encode')

def decrypt_file_onetime(input_file,output_file):
    key = set_key.load_key()
    f = Fernet(key)

    with open(input_file,'rb') as f_in:
        encrypted_data = f_in.read()
        
    decrypted = f.decrypt(encrypted_data)
    
    with open(output_file,'wb') as f_out:
        f_out.write(decrypted)
    print('Decode')


# decrypt_file_onetime(EN_DB,DE_DB)

encrypt_file_onetime(DE_DB,EN_DB)