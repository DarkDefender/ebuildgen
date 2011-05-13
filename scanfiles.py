import os
import glob

needed_hfiles = {}

def scandir(dir, filetype):
    files = []
    dirs = [f for f in os.listdir(dir)
        if os.path.isdir(os.path.join(dir, f))]
    for dir_path in dirs:
        files += scandir(dir + "/" + dir_path, filetype)
    return files + glob.glob(dir + "/*" + filetype)

print(scandir("/home/zed/Desktop/test/smw/", ".cpp"))
