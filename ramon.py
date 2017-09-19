import os
import hashlib

FILE_UNKNOWN = "FILE_UNKNOWN"

def sha256_checksum(filename, block_size=65536):
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()

def discover():
    for dirName, subdirList, fileList in os.walk("/home/chirality/testing", topdown=False):
        for filename in fileList:
            full_path = os.path.join(dirName, filename)
            file_extension = str.upper(os.path.splitext(full_path)[1][1:])

            process_file = True
            argsNew = True
            argsBaseline = False
            if process_file:
                file_hash = sha256_checksum(full_path)

                file_info = dict()
                file_info["path"] = full_path
                file_info["sha256"] = file_hash

                status = FILE_UNKNOWN

                if status == FILE_UNKNOWN:
                    print file_info

                elif status == FILE_KNOWN_TOUCHED:
                    if not args.baseline:
                        print file_info #FILE_KNOWN_TOUCHED

                elif status == FILE_KNOWN_UNTOUCHED:
                    pass

discover()
