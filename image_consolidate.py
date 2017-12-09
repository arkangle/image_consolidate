#!/usr/bin/python3
from PIL import Image
import sys
import shutil
import os
import subprocess
import json
import pathlib
import time
from argparse import ArgumentParser

def exe(cmd):
    process = subprocess.run(cmd,stdout=subprocess.PIPE)
    output = process.stdout.decode('utf-8')
    return output

class Image:
    def __init__(self, dest_base, filename):
        self.src_filename = filename
        self.dest_base = dest_base
        self.extension = self.ext(self.src_filename)
        self.sha_sum = self.sha256(self.src_filename)
        self.exif = self.exif(self.src_filename)
        self.created_date = self.created(self.exif)

    def exif(self, filename):
        cmd = ["exiftool", "-json", filename]
        output = exe(cmd)
        output_json = json.loads(output)
        return output_json[0]

    def created(self, exif):
        created = "0000:00:00 00:00:00"
        if "CreateDate" in exif:
            created = exif["CreateDate"]
        elif "DateCreated" in exif:
            created = exif["DateCreated"]
        return created.split(" ")[0].split(":")

    def ext(self, filename):
        return pathlib.Path(filename).suffix

    def sha256(self, filename):
        cmd = ["sha256sum", filename]
        output = exe(cmd)
        split = output.split()
        return split[0]

    def dest_filename(self):
        return "%s/%s/%s/%s-%s-%s-%s%s" % (self.dest_base, self.created_date[0], self.created_date[1], self.created_date[0], self.created_date[1], self.created_date[2], self.sha_sum, self

    def dest_dir(self):
        return "%s/%s/%s" % (self.dest_base, self.created_date[0], self.created_date[1])

    def do_copy(self):
        shutil.copyfile(self.src_filename, self.dest_filename())

    def isImage(self):
        return not "Error" in self.exif

    def copy(self):
        if self.isImage():
            if not os.path.exists(self.dest_dir()):
                os.makedirs(self.dest_dir())
            if os.path.exists(self.dest_filename()):
                print("Destination exists!: ", self.dest_filename())
            else:
                print("Copy %s to %s " % (self.src_filename, self.dest_filename()))
                self.do_copy()
        else:
            print("NOT image: ", self.src_filename)


if __name__ == "__main__":
    parser = ArgumentParser(description='Copy Images/Movies based on exif')
    parser.add_argument('--source', '-s', required=True, help='Source Directory')
    parser.add_argument('--destination', '-d', required=True, help='Destination Directory')
    args = parser.parse_args()

    source_dir = args.source
    destination_dir = args.destination

    for dirpath, dirnames, files in os.walk(source_dir):
        for name in files:
            source_file = "%s/%s" % (dirpath, name)
            image = Image(destination_dir, source_file)
            image.copy()

