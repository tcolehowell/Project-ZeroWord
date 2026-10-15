from argon2 import PasswordHasher
from argon2.low_level import hash_secret_raw, Type
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import readchar
import json
import os
import platform

passwordHasher = PasswordHasher()

MASTER_FILE = "master_password.txt"
VAULT_FILE = "vault.bin"
VAULT_SALT_FILE = "vault_kdf_salt.bin"
VAULT_NONCE_FILE = "vault_nonce.bin"


def initialize_master_password():
    password = input("Enter master password: ")
    hashed_password = passwordHasher.hash(password)
    with open(MASTER_FILE, "w") as f:
        f.write(hashed_password)
    print("Master password initialized and saved.")


def verify_master_password():
    tries = 3
    while tries > 0:
        input_password = input("Enter master password: ")
        with open(MASTER_FILE, "r") as f:
            stored_hashed_password = f.read()
        try:
            passwordHasher.verify(stored_hashed_password, input_password)
            print("Master password verified.")
            return input_password
        except Exception:
            tries -= 1
            print(f"Incorrect password. {tries} tries left.")
    print("Too many failed attempts. Exiting.")
    return None


def derive_vault_key(master_password: str, salt: bytes) -> bytes:
    return hash_secret_raw(
        secret=master_password.encode("utf-8"),
        salt=salt,
        time_cost=3,
        memory_cost=64 * 1024, # 64 MB
        parallelism=4,
        hash_len=32, # 32-byte key
        type=Type.ID,
    )


def initialize_vault(master_password: str):
    vault_salt = os.urandom(16)
    with open(VAULT_SALT_FILE, "wb") as f:
        f.write(vault_salt)

    vault_key = derive_vault_key(master_password, vault_salt)

    plaintext_vault = b"[]"

    aesgcm = AESGCM(vault_key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext_vault, associated_data=None)

    with open(VAULT_FILE, "wb") as f:
        f.write(ciphertext)
    with open(VAULT_NONCE_FILE, "wb") as f:
        f.write(nonce)

    print("Vault initialized and encrypted.")


def unlock_vault():
    master_password = verify_master_password()
    if master_password is None:
        return

    with open(VAULT_SALT_FILE, "rb") as f:
        vault_salt = f.read()
    vault_key = derive_vault_key(master_password, vault_salt)

    with open(VAULT_NONCE_FILE, "rb") as f:
        nonce = f.read()
    with open(VAULT_FILE, "rb") as f:
        ciphertext = f.read()

    aesgcm = AESGCM(vault_key)
    plaintext_vault = aesgcm.decrypt(nonce, ciphertext, associated_data=None)
    return plaintext_vault.decode("utf-8")


def get_new_entry():
    name = input("\nEnter the name for the password entry: ")
    username = input("Enter the username: ")
    password = input("Enter the password: ")
    return {"name": name, "username": username, "password": password}


def add_password_entry(entry: dict, master_password: str):
    with open(VAULT_SALT_FILE, "rb") as f:
        vault_salt = f.read()
    vault_key = derive_vault_key(master_password, vault_salt)

    with open(VAULT_NONCE_FILE, "rb") as f:
        nonce = f.read()
    with open(VAULT_FILE, "rb") as f:
        ciphertext = f.read()

    aesgcm = AESGCM(vault_key)
    plaintext_vault = aesgcm.decrypt(nonce, ciphertext, associated_data=None)

    vault_data = json.loads(plaintext_vault.decode("utf-8"))
    vault_data.append(entry)

    new_plaintext_vault = json.dumps(vault_data).encode("utf-8")
    new_nonce = os.urandom(12)
    new_ciphertext = aesgcm.encrypt(new_nonce, new_plaintext_vault, associated_data=None)

    with open(VAULT_FILE, "wb") as f:
        f.write(new_ciphertext)
    with open(VAULT_NONCE_FILE, "wb") as f:
        f.write(new_nonce)

    print("\nPassword entry added to the vault.")


def list_password_entries(master_password: str):
    with open(VAULT_SALT_FILE, "rb") as f:
        vault_salt = f.read()
    vault_key = derive_vault_key(master_password, vault_salt)

    with open(VAULT_NONCE_FILE, "rb") as f:
        nonce = f.read()
    with open(VAULT_FILE, "rb") as f:
        ciphertext = f.read()

    aesgcm = AESGCM(vault_key)
    plaintext_vault = aesgcm.decrypt(nonce, ciphertext, associated_data=None)

    vault_data = json.loads(plaintext_vault.decode("utf-8"))
    print("\nStored Password Entries:\n")
    for entry in vault_data:
        print(f"Name: {entry['name']}, Username: {entry['username']}, Password: {entry['password']}")


def clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


def main():
    if not os.path.exists(MASTER_FILE):
        print("No master password set. Initializing...")
        initialize_master_password()
        print("Master password initialized.")
        master_password = verify_master_password()
        if master_password is None:
            return
        initialize_vault(master_password)
    else:
        master_password = verify_master_password()
        if master_password is None:
            return


        clear_screen()
        while True:
            print("\nOptions:")
            print("[1] Add a new password entry")
            print("[2] List all password entries")
            print("[Q] Exit")

            key = readchar.readkey()

            if key == '1':
                clear_screen()
                entry = get_new_entry()
                add_password_entry(entry, master_password)
            elif key == '2':
                clear_screen()
                list_password_entries(master_password)
            elif key == 'Q' or key == 'q':
                break
            else:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
