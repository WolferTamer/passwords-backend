#encryption and decryption

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

KEY_SIZE = 32 #256 bits
BLOCK_SIZE = 16

def gen_key():
    return get_random_bytes(KEY_SIZE)

def encryption(plain_text, key):
    #padding length for plaintext
    padding = BLOCK_SIZE - len(plain_text) % BLOCK_SIZE 
    #pkcs#7 padding standard
    pad_text = plain_text + chr(padding) * padding 
    #initializing the cypher
    aes_cipher = AES.new(key, AES.MODE_CBC)
    #encrypt padded plaintext with cipher
    encrypted_msg = aes_cipher.encrypt(pad_text.encode('utf-8'))
    #returning concatneated msg
    return base64.b64encode(aes_cipher.iv + encrypted_msg).decode('utf-8')

#decryption
def decrypt_msg(encrypted_text, key):
    #decode base64 msg
    enc_data = base64.b64decode(encrypted_text)
    #extracting initilization vector
    iv = enc_data[:BLOCK_SIZE]
    #extract encrypted msg (excluding iv)
    encrypted_msg = enc_data[BLOCK_SIZE:]
    #cipher initialization
    aes_cipher = AES.new(key, AES.MODE_CBC, iv)
    #decrypt message
    decrypted_msg = aes_cipher.decrypt(encrypted_msg)
    #identify padding in last byte
    padding = decrypted_msg[-1]
    #remove padding
    return decrypted_msg[:-padding].decode('utf-8')