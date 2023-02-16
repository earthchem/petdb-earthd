import os
import shutil

def move_xls_files(src_dir, dst_dir):
    for subdir, dirs, files in os.walk(src_dir):
        for file in files:
            file_path = os.path.join(subdir, file)
            print(file_path)
            if file_path.endswith('.xls'):
                shutil.move(file_path, dst_dir)

src_dir = 'Y3Q4_earthd'
dst_dir = 'earthd_files'

move_xls_files(src_dir, dst_dir)
