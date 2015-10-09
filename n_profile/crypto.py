

from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Hash import SHA256, HMAC
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random.random import getrandbits
from Crypto import Random
from Crypto.Util import Counter

from django.conf import settings


EXPANSION_COUNT = 10000
AES_KEY_LEN = 256
SALT_LEN = 128
HASH = SHA256
HEADER = b'sc\x00\x00'

SECRET_KEY = 'Sf34Drfv65yhRgtDD390Gfff--d'

if hasattr(settings, 'PROFILE_SECRET_KEY'):
    if settings.PROFILE_SECRET_KEY:
        SECRET_KEY = settings.PROFILE_SECRET_KEY
    

HALF_BLOCK = AES.block_size*8//2

assert HALF_BLOCK <= SALT_LEN

def user_activation_token(username, email, due_date):
    msg = username + ',' + email + ',' + due_date.strftime("%Y-%m-%d")
    return encrypt(msg)

def encrypt(data):

    data = _str_to_bytes(data)
    salt = bytes(_random_bytes(SALT_LEN//8))
    hmac_key, cipher_key = _expand_keys(SECRET_KEY, salt)
    counter = Counter.new(HALF_BLOCK, prefix=salt[:HALF_BLOCK//8])
    cipher = AES.new(cipher_key, AES.MODE_CTR, counter=counter)
    encrypted = cipher.encrypt(data)
    hmac = _hmac(hmac_key, HEADER + salt + encrypted)
    msg = HEADER + salt + encrypted + hmac
    b64E=b64encode(msg)
    return b64E.decode()

def decrypt(data):

    if isinstance(data, str):
        data = str.encode(data)

    data = b64decode(data)
    raw = data[len(HEADER):]
    salt = raw[:SALT_LEN//8]
    hmac_key, cipher_key = _expand_keys(SECRET_KEY, salt)
    hmac = raw[-HASH.digest_size:]
    hmac2 = _hmac(hmac_key, data[:-HASH.digest_size])
    counter = Counter.new(HALF_BLOCK, prefix=salt[:HALF_BLOCK//8])
    cipher = AES.new(cipher_key, AES.MODE_CTR, counter=counter)
    return cipher.decrypt(raw[SALT_LEN//8:-HASH.digest_size]).decode()

def _expand_keys(password, salt):
    key_len = AES_KEY_LEN // 8
    keys = PBKDF2(_str_to_bytes(password), salt, dkLen=2*key_len,
        count=EXPANSION_COUNT, prf=lambda p,s: HMAC.new(p,s,HASH).digest())
    return keys[:key_len], keys[key_len:]

def _random_bytes(n):
    Random.atfork()
    return bytearray(getrandbits(8) for _ in range(n))

def _hmac(key, data):
    return HMAC.new(key, data, HASH).digest()

def _str_to_bytes(data):
    u_type = type(b''.decode('utf8'))
    if isinstance(data, u_type):
        return data.encode('utf8')
    return data