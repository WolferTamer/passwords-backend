# file for storing keys using a json file
import os
import json
from .cryption import gen_key

KEY_FILE = "keys.json"

def initialize_key_store():
    #initialie key store file if it doesn't already exist
    if not os.path.exists(KEY_FILE):
        with open(KEY_FILE, "w") as f:
            # writing an empty dictionary json for storing keys
            json.dump({}, f)
            
def store_user_key(username):
    #checking key store file exists
    initialize_key_store()
    #generating key
    key = gen_key()
    with open(KEY_FILE, "r+") as f:
        #load existing keys
        keys = json.load(f)
        #store keys as hex string
        keys[username] = key.hex()
        f.seek(0)
        #write back updated keys
        json.dump(keys, f, indent=4)
    return key

def get_user_key(username):
    initialize_key_store()
    with open(KEY_FILE, "r") as f:
        keys = json.load(f)
        if username in keys:
            #converting hex string back to bytes and returning the key
            return bytes.fromhex(keys[username])
    #error checking
    raise ValueError("Key not found for the user")