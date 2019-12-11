import os 
import argparse 
import pyperclip
import json
from cryptography.fernet import Fernet
from getpass import getpass
from dotenv import load_dotenv

# COMMAND_TO_CREATE_EXE = 'pyinstaller -F -n pm --distpath . password_manager.py'

VERSION = '2.1'

def get_path():
    """ Get path (directory) of the current exe """
    for p in os.environ['path'].split(';'):
        if os.path.exists(os.path.join(p, 'pm.exe')):
            return p

def setup():
    """ Setup the application by setting and loading environment variables """
    path = os.path.join(get_path(), 'pm.env ')
    if os.path.exists(path):
        load_dotenv(path)
        return True
    master_password = input('Set Master Password: ')
    with open(path, 'w') as env_file:
        env_file.write(f'MASTER_PASSWORD={master_password}\n')
        key = Fernet.generate_key() #this is your "password"
        env_file.write(f'SECRET_KEY={key.decode()}\n')
        env_file.write(f'DEST={os.path.join(get_path(), "pm")}')
    return False

def reset_password(new_password):
    """ Reset the Master password """
    try: 
        if new_password is None:
            new_password = input('New Master Password: ')
        else:
            new_password = new_password[0]

        path = os.path.join(get_path(), 'pm.env ')

        with open(path, 'r') as env_file:
            new_env = f'MASTER_PASSWORD={new_password}\n'
            new_env += ''.join(env_file.readlines()[1:])

        with open(path, 'w') as env_file:
            env_file.write(new_env)

        return True
    except Exception as e:
        print(e)
        return False

def clear():
    """ Delets all existing records """
    try:
        os.remove(os.environ.get('DEST'))
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
        with open(os.environ.get('DEST'), 'rb') as file:
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
        
        with open(os.environ.get('DEST'), 'wb') as pwfile:
            pwfile.write(encoded_text)
        
        return True
    except Exception as e:
        return False

def display(passwords_loaded):
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

def save(passwords_loaded, account, username, password):
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
            if reset_password(args.password):
                print('Reset Success')
            else:
                print('Reset Error')
        elif args.clear:
            if clear():
                print('Clear Success')
            else:
                print('clear Error')
        elif args.display:
            display(passwords_loaded)
        elif args.save:
            save(passwords_loaded, args.account, args.username, args.password)
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

    parser.add_argument('-d', '--display', action='store_true',
                        default = None, help = 'Display all saved passwords') 

    parser.add_argument('-c', '--clear', action='store_true',
                        default = None, help = 'Clear the application (Delete all entries)') 

    parser.add_argument('-r', '--reset', action='store_true',
                        default = None, help = "Reset the application's Master Password") 

    parser.add_argument('-v', '--version', action='store_true',
                        default = None, help = 'Version') 

    args = parser.parse_args() 

    process_args(args, master_password, passwords_loaded)

if __name__ == "__main__": 
    # Setup the application
    if setup():
        # Global variables for encription and decription
        key = str.encode(os.environ.get('SECRET_KEY'))
        cipher_suite = Fernet(key)

        # Run the application
        main()
