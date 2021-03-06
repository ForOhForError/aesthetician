#!python3

import json
import os.path
import sys
import argparse

import data_coding as code

# Specifies the layout of the data file
# Formatted as a dict of (name) -> tuple of (offset, length, function to encode, function to decode)
dat_file_spec = {
    "ancestry": (0x10, 1, code.ancestry_encode, code.ancestry_decode),
    "gender": (0x11, 1, code.gender_encode, code.gender_decode),
}

default_conf = os.path.join(
    os.path.expanduser("~"),
    '.aesthetician.conf'
)

charfile_name = "FFXIV_CHARA_{}.dat"

comment_offset = 48

def write_config(filename=default_conf, data=None):
    if data == None:
        print("Config file not found - writing new config file to ~/.aesthetician.conf")
        print("You will be prompted for the location of your local FFXIV files.")
        print("This is usually located at Documents -> My Games -> FINAL FANTASY XIV - A Realm Reborn")
        path = None
        found = False
        while path == None:
            try:
                path_input = input("Enter local FFXIV path: ")
            except KeyboardInterrupt:
                sys.exit(1)
            if os.path.exists(path_input):
                if os.path.exists(os.path.join(path_input,"FFXIV_BOOT.cfg")):
                    path = path_input
                else:
                    print("Given directory did not contain FFXIV_BOOT.cfg, path rejected")
        storage_path = None
        while storage_path == None:
            print("You will be prompted for a location for aesthetician to save files it manages (named character files, etc).")
            print("This location will be created if it does not already exist.")
            try:
                path_input = input("Enter storage path: ")
            except KeyboardInterrupt:
                sys.exit(1)
            if os.path.exists(path_input):
                if os.path.isdir(path_input):
                    storage_path = path_input
            else:
                try:
                    os.makedirs(path_input)
                    storage_path = path_input
                except os.error:
                    print("Director creation failed, exiting.")
                    sys.exit(1)

        data = {
            'xiv_path': path
        }
    with open(filename, "w") as json_file:
        json.dump(data, json_file, indent=4, sort_keys=True)

def load_conf(filename=default_conf):
    if os.path.exists(filename):
        if os.path.isfile(filename):
            with open(filename) as json_file:
                data = json.load(json_file)
                return data
        else:
            print("config file {} is a directory and cannot be read.".format(filename))
            sys.exit(1)
    else:
        write_config(filename)
        return load_conf(filename)

def get_attribute(data, attr):
    if attr in dat_file_spec:
        entry = dat_file_spec[attr]
        offset, length, enc, dec = entry
        segment = data[offset:offset+length]
        return dec(segment)

def get_appearance_comment(data):
    stringdata = data[comment_offset:]
    return stringdata.decode("utf8")

def aesthetic_action(func):
    func.aesthetic_action = True
    return func

def confirm(message='Are you sure (y/N): '):
    res = input(message)
    res = res.strip().lower()
    return len(res) > 0 and res.startswith('y')

def slot_type(x):
    x = int(x)
    if x < 1 or x > 40:
        raise argparse.ArgumentTypeError("Slot number must be between 1 and 40, inclusive")
    return x

class AestheticianCLI:
    """
    Class representing the CLI interface for aestheticican

    class methods with the `@aesthetic_action` decorator
    are executed from the CLI via `aesthetician [action]`
    """
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog='aesthetician',
            description='Character appearance manager for Final Fantasy XIV'
        )
        self.parser.add_argument('action', help='action to take (list | backup | restore)')

        self.config = load_conf()

    def run(self):
        args = self.parser.parse_args(sys.argv[1:2])

        if hasattr(self, args.action):
            action_call = getattr(self, args.action)
            if hasattr(action_call, 'aesthetic_action'):
                return action_call()
        print('Action {} not recognized'.format(args.action))
        self.parser.print_help()
        return 1

    def get_charfile_name_path(self, slot):
        num = str(slot).zfill(2)
        charname = charfile_name.format(num)
        charfile_path = os.path.join(self.config['xiv_path'],charname)
        return charname, charfile_path

    def get_storagefile_path(self, fname):
        storagefile_path = os.path.join(self.config['storage_path'],fname)
        return storagefile_path

    def charfile_exists(self, slot):
        charname, charfile_path = self.get_charfile_name_path(slot)
        return os.path.exists(charfile_path) and os.path.isfile(charfile_path)

    def get_slot_data(self, slot):
        if self.charfile_exists(slot):
            charname, charfile_path = self.get_charfile_name_path(slot)
            with open(charfile_path, "rb") as datafile:
                data = datafile.read()
            return data
        return None

    def write_slot_data(self, slot, data, force=False):
        slotname, filepath = self.get_charfile_name_path(slot)
        if os.path.exists(filepath) and (not force):
            if not confirm("Slot {} is already used. Overwrite? (y/N): ".format(slot)):
                print("write cancelled")
                return False
        with open(filepath, 'wb') as charfile:
            charfile.write(data)
        return True

    def get_storage_data(self, fname):
        storagefile = self.get_storagefile_path(fname)
        if os.path.exists(storagefile):
            with open(storagefile, "rb") as datafile:
                data = datafile.read()
            return data
        return None

    def write_storage_data(self, fname, data, force=False):
        filepath = self.get_storagefile_path(fname)
        if os.path.exists(filepath) and (not force):
            if not confirm("File {} already exists. Overwrite? (y/N): ".format(fname)):
                print("write cancelled")
                return False
        with open(filepath, 'wb') as charfile:
            charfile.write(data)
        return True



    @aesthetic_action
    def list(self):
        parser = argparse.ArgumentParser(
            prog='aesthetician list',
            description='list all character appearance data'
        )
        args = parser.parse_args(sys.argv[2:])

        print("--- FFXIV character appearance slots ---")
        for i in range(1,41):
            if self.charfile_exists(i):
                data = self.get_slot_data(i)
                comment = get_appearance_comment(data)
                clan = get_attribute(data, 'ancestry')
                gender = get_attribute(data, 'gender')
                print(i,'\t', gender, clan,'\t', comment)

        print("--- Aesthetician saved appearance data ---")
        storagepath = self.config['storage_path']
        datafiles = [f for f in os.listdir(storagepath) if os.path.isfile(os.path.join(storagepath, f))]
        for datafile in datafiles:
            data = self.get_storage_data(datafile)
            comment = get_appearance_comment(data)
            clan = get_attribute(data, 'ancestry')
            gender = get_attribute(data, 'gender')
            print(datafile,'\t', gender, clan,'\t', comment)
        return 0
    
    @aesthetic_action
    def backup(self):
        parser = argparse.ArgumentParser(
            prog="aesthetician backup",
            description="Backup character appearance from an appearance slot to aesthetician's storage directory"
        )
        parser.add_argument('slot', type=slot_type)
        parser.add_argument('filename')
        args = parser.parse_args(sys.argv[2:])
        data = self.get_slot_data(args.slot)
        if data == None:
            print("Slot is not occupied.")
            return 1
        self.write_storage_data(args.filename, data)
        return 0

    @aesthetic_action
    def restore(self):
        parser = argparse.ArgumentParser(
            prog="aesthetician restore",
            description="Restore a character appearance from aesthetician's storage directory to an appearance slot"
        )
        parser.add_argument('filename')
        parser.add_argument('slot', type=slot_type)
        args = parser.parse_args(sys.argv[2:])
        data = self.get_storage_data(args.filename)
        if data == None:
            print("Appearance file does not exist.")
            return 1
        self.write_slot_data(args.slot, data)
        return 0

def main():
    return AestheticianCLI().run()

if __name__ == "__main__":
    sys.exit(main())
