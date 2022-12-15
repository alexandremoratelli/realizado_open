
import base64
from cryptography.fernet import Fernet

key = Fernet.generate_key()
print(f'key: {key}')

cipher_suite = Fernet(key)


text = "Datainfo-Digital#Transformers+22"
btext = text.encode("utf-8")
b64text = base64.urlsafe_b64encode(btext)
print(f'text: {text}')
print(f'btext: {btext}')
print(f'b64text: {b64text}')
print(f'b64text: {b64text.decode("utf-8")}')
print()
print()


key_1 = "NUcmFuc2Zvcm1lcnMrMjI="
key_2 = "RGF0YWluZm8tRGlnaXRhbC"

b64text = (key_2 + key_1).encode("utf-8")

cipher_suite = Fernet(b64text)

cipher_text = cipher_suite.encrypt(b'senha')
print(f'cipher_text: {cipher_text.decode("utf-8")}')

plain_text = cipher_suite.decrypt(cipher_text)
print(f'plain_text: {plain_text}')
print(f'plain_text: {plain_text.decode("utf-8")}')

