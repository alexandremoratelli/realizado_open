
import json
import inspect
import os
from cryptography.fernet import Fernet

config_file = "cfg/config.json"
config = {}


def __inspect_helper():
    path = os.getcwd()
    module_path = os.path.dirname(os.path.realpath(__file__))
    print('Detalhes:')
    print(f'File: {__file__}')
    print(f'Working path:{path}')
    print(f'Module path: {module_path}')
    print(f'ModuleName: {__file__}')
    print(f'Inspect: {inspect.stack()[-1].filename}')

    caller = inspect.stack()[2]
    print(f"\nThis is  caller[3]:  {caller[3]}")

    caller = inspect.stack()[2]
    print(f"This is  caller[3] inside function:  {caller[3]}")

    for item in caller:
        print(f"This is  caller item:  {item}")

    print('')
    stack_list = inspect.stack()
    for stack in stack_list:
        print(f'Stack: {stack}')

    return inspect.stack()[-1].filename


def set_config_file(new_config_file):
    global config_file
    config_file = new_config_file


def decrypt(key, encrypted_text):
    #cipher_suite = Fernet(key.encode("utf-8"))
    cipher_suite = Fernet((key_2 + key_1).encode("utf-8"))
    decrypted_text = cipher_suite.decrypt(encrypted_text.encode("utf-8"))
    return decrypted_text.decode("utf-8")


def load_config():
    global config
    global config_file

    try:
        with open(config_file, "r") as f:
            config = json.load(f)

        config_secrets_file = config["config.secrets_file"]

        if config_secrets_file != "":
            with open(config_secrets_file, "r") as f:
                config_secrets = json.load(f)
                config_secrets["secrets.service_user"] = decrypt(
                    config_secrets["secrets.crypto.key"],
                    config_secrets["secrets.service_user"]
                )
                config_secrets["secrets.service_pwd"] = decrypt(
                    config_secrets["secrets.crypto.key"],
                    config_secrets["secrets.service_pwd"]
                )
                config = config | config_secrets
        config["config.service_pwd"] = decrypt(
            (key_2 + key_1).encode("utf-8"),
            config["config.service_pwd"]
        )

    except Exception as e:
        config = None
        print("myconfigOcorreu erro em:", e)


def get_config(config_name):
    global config
    config = {}
    # inspect_helper()
    try:
        load_config()
        return config[config_name]
    except Exception as e:
        #print("inspect: ", inspect_helper())
        print(e)
        return ""


def get_all_config():
    global config
    config = {}
    if not config:
        load_config()
    return config


key_1 = "NUcmFuc2Zvcm1lcnMrMjI="
key_2 = "RGF0YWluZm8tRGlnaXRhbC"


if __name__ == "__main__":
    print(get_config("config.service_user"))
    print(get_config("config.service_pwd"))
    print(get_all_config())
