'''
Hide My Shit
Copyright (c) 2011-2022 Khaled El-Morshedy
@elmoiv
'''
import os
from random import randint
from shutil import move, rmtree
from cryptography.fernet import Fernet

HASH_FILE = 'setup.exe'
join = os.path.join

def encrypt_path(_path, key):
    encryptor = Fernet(key)
    return encryptor.encrypt(_path.encode()).decode()

def decrypt_path(_path, key):
    decryptor = Fernet(key)
    return decryptor.decrypt(_path.encode()).decode()

def get_all_files(_path):
    return [
        join(folder, _file)
            for folder, _, files in os.walk(_path)
                for _file in files
        ]

def create_file_list(path_list, file_path):
    path_and_bins = []
    encrypt_key = Fernet.generate_key()
    with open(file_path, 'wb') as out:
        size = 1024 * 1024 * randint(3, 10) + randint(500, 1024) * 1024
        out.truncate(size)

        # First line has key
        data = [*(encrypt_key.decode() + '\n')]

        # Rest are encrypted paths
        for n, p in enumerate(path_list, 1):
            enc_path = encrypt_path(f'{p}*data-{n}.bin', encrypt_key)
            path_and_bins.append([p, f'data-{n}.bin'])
            data += [*(enc_path + '\n')]
        
        data = [i + '\0' * randint(3, 7) for i in data]
        # print(data)
        out.seek(randint(500, 1024))
        out.write(''.join(data).encode())
    return path_and_bins

def get_file_list(json_path):
    json = open(json_path, 'rb').read().decode()
    lines = json.replace('\0', '').strip('\n').split('\n')
    encrypt_key = lines.pop(0)
    return [decrypt_path(line, encrypt_key) for line in lines]

def remove_treed_paths(paths: list, main_dir):
    for src, dst in paths:
        move(src, join(main_dir, dst))

    for p in os.listdir(main_dir):
        tgt_dir = join(main_dir, p)
        if os.path.isdir(tgt_dir):
            rmtree(tgt_dir)

def restore_treed_paths(main_dir, json_path):
    data = get_file_list(json_path)
    
    try:
        os.remove(json_path)
    except:
        pass

    for _path_dat in data:
        _path, databin_name = _path_dat.split('*')
        
        # Create treed dirs
        dir_name = os.path.dirname(_path)
        os.makedirs(dir_name, exist_ok=True)
        
        # Move untreed file to original treed path
        src = join(main_dir, databin_name)
        dst = _path
        move(src, dst)
    

if __name__ == '__main__':
    print('''
██   ██ ██ ██████  ███████     ███    ███ ██    ██     ███████ ██   ██ ██ ████████ 
██   ██ ██ ██   ██ ██          ████  ████  ██  ██      ██      ██   ██ ██    ██    
███████ ██ ██   ██ █████       ██ ████ ██   ████       ███████ ███████ ██    ██    
██   ██ ██ ██   ██ ██          ██  ██  ██    ██             ██ ██   ██ ██    ██    
██   ██ ██ ██████  ███████     ██      ██    ██        ███████ ██   ██ ██    ██    

                                 by: elmoiv
                                                                                   ''')
    TARGET_DIR = input('Enter folder path: ')
    hash_path = join(TARGET_DIR, HASH_FILE)
    if os.path.exists(hash_path):
        restore_treed_paths(TARGET_DIR, hash_path)
    else:
        files = get_all_files(TARGET_DIR)
        paths_and_bins = create_file_list(files, hash_path)
        remove_treed_paths(paths_and_bins, TARGET_DIR)
