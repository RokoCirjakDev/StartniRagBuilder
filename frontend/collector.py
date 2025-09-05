import os
import shutil

def move_file_to_collector(src_path):

    collector_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../collector"))
    os.makedirs(collector_dir, exist_ok=True)
    file_name = os.path.basename(src_path)
    dst_path = os.path.join(collector_dir, file_name)
    shutil.move(src_path, dst_path)
    return dst_path