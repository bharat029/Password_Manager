import os 
import argparse 
import pyperclip
import json
from cryptography.fernet import Fernet
from getpass import getpass

VERSION = '1.0'

def reset():
    """ Delets all existing records """
    try:
        os.remove(r'D:\utills\passwords.txt')
        return True 
    except Exception as e:
        return False

def load_passwords():
    """ 
        Loads passwords from the passwords.txt file
    Returns:
        A dictionary from {account}-{username/main} -> {password}
    """
    try:
        with open(r'D:\utills\passwords.txt', 'rb') as file:
            decoded_text = cipher_suite.decrypt(file.read())
            passwords_loaded = json.loads(decoded_text) 

        return passwords_loaded
    except Exception as e:
        return {}

def encrypt_and_save(passwords):
    """ 
        Encripts and saves them into a txt file called passwords.txt
    Args:
        passwords: the dictionary of {account}-{username} -> {password}
    Returns:
        True if successful, False otherwise (in case an error occurs)
    """
    try:
        passwords = json.dumps(passwords)
        passwords = str.encode(passwords)        
        
        encoded_text = cipher_suite.encrypt(passwords)
        
        with open(r'D:\utills\passwords.txt', 'wb') as pwfile:
            pwfile.write(encoded_text)
        
        return True
    except Exception as e:
        return False

def get_all(passwords_loaded):
    """ Get all saved passwords
    Args:
        passwords_loaded: dictionary loaded from file containing the records of all accounts and passwords
    """
    print('-' * 85)
    print(f'| {"Account":25} | {"Username":25} | {"Password":25} |')
    print('-' * 85)

    for acc, password in passwords_loaded.items():
        idx = acc.find('-')
        print(f'| {acc[:idx]:25} | {acc[idx+1:]:25} | {len(password) * "*":25} |')
    print('-' * 85)

def save_new(passwords_loaded, account, username, password):
    """ 
        Adds the new {account}-{username}->{password} entry to passwords loaded
    Args: 
        passwords_loaded: dictionary loaded from file containing the records of all accounts and passwords
        account: account for the new entry
        username: username for the new entry (main is the default)
        password: password for the new entry
    """
    if account is None:
        account = input('Account: ').lower()
    else:
        account = account[0].lower()

    if username is None:
        username = 'main'
    else:
        username = username[0].lower()

    if password is None:
        password = input('Password: ')
    else:
        password = password[0]

    if len(username) == 0:
        username = 'main'

    passwords_loaded[f'{account}-{username}'] = password 
    if encrypt_and_save(passwords_loaded):
        print('Saved')
    else:
        print('An Error occured')

def get_password(passwords_loaded, account, username):
    """ 
        Find the password for given account and usernme in the loaded passwords.
            if found the password is coppied to the clipboard
            else a not found message is printed
    Args:
        passwords_loaded: dictionary loaded from file containing the records of all accounts and passwords
        account: account for the entry
        username: username for the entry (main is the default)
    """
    if account is None:
        account = input('Account: ').lower()
    else:
        account = account[0].lower()

    if username is None:
        username = 'main'
    else:
        username = username[0].lower()

    password = passwords_loaded.get(f'{account}-{username}')

    if password is None:
        print('Password not found')
    else:
        pyperclip.copy(password)
        print(f'The password has been coppied to clipboard')

def process_args(args, master_password, passwords_loaded):
    """ 
        Checks if the master password is correct, if so uses parsed arguments adn calls the relevant functions.
    Args:
        args: the parsed command line arguments
        master_password: the password for the password manager (it has to be set before hand in the MASTER_PASSWORD environment variable)
        passwords_loaded: dictionary loaded from file containing the records of all accounts and passwords
    """
    if args.version:
        print(VERSION)
        return

    if args.master_password is None:
        password = getpass('Master Password: ')
    else: 
        password = args.master_password[0]
    
    if password == master_password:
        if args.reset:
            if reset():
                print('Reset Success')
            else:
                print('Reset Error')
        elif args.get_all:
            get_all(passwords_loaded)
        elif args.save:
            save_new(passwords_loaded, args.account, args.username, args.password)
        else:
            get_password(passwords_loaded, args.account, args.username)
    else:
        print('error: Incorrect Password')

def main(): 
    """ 
        This fuction is responsibel for starting up the whole application. Functionalities include:
            - Load master password from environment variable
            - load passwords from file (calls load_passwords)
            - sets up the argument parser
            - parses the arguments
            - hands over the parsed arguments to process_args
    
    """
    master_password = os.environ.get('MASTER_PASSWORD')

    if master_password is None:
        print(f'error: "MASTER_PASSWORD" environment variable not set.')
        exit(1)
        
    passwords_loaded = load_passwords()

    parser = argparse.ArgumentParser(description='My Password manager') 

    parser.add_argument('-a', '--account', type = str, nargs = 1, 
                        default = None, help = 'Account') 

    parser.add_argument('-u', '--username', type = str, nargs = 1, 
                        default = None, help = 'Username for the account') 

    parser.add_argument('-p', '--password', type = str, nargs = 1, 
                        default = None, help = 'Password used fot the save mode only') 

    parser.add_argument('-m', '--master_password', type = str, nargs = 1, 
                        default = None, help = 'Master password of the password manager') 

    parser.add_argument('-s', '--save', action='store_true',
                        default = None, help = 'Save new password') 

    parser.add_argument('-g', '--get_all', action='store_true',
                        default = None, help = 'Get all saved passwords') 

    parser.add_argument('-r', '--reset', action='store_true',
                        default = None, help = 'Reset the application (Delete all entries)') 

    parser.add_argument('-v', '--version', action='store_true',
                        default = None, help = 'Version') 

    args = parser.parse_args() 

    process_args(args, master_password, passwords_loaded)

if __name__ == "__main__": 
    # Global variables for encription and decription
    key = str.encode(os.environ.get('MASTER_SECRET_KEY'))
    cipher_suite = Fernet(key)

    # Run the application
    main()
