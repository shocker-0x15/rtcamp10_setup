import sys
import os
import io
import shutil
from pathlib import Path
import glob
import time
import re
import subprocess
import zipfile

def chdir(dst):
    oldDir = os.getcwd()
    os.chdir(dst)
    return oldDir

encoding='cp932'

def run_command(cmd, timeout=None):
    print(' '.join(cmd))
    return subprocess.run(
        cmd, check=True, timeout=timeout, capture_output=True, text=True,
        encoding=encoding)

renderer_infos = {
    "submission_filename": ("name", "renderer_name", "cpu/gpu"),
}

def run():
    submission_dir = Path(sys.argv[1])
    images_root_dir = Path(sys.argv[2])
    pix_fmt = sys.argv[3]

    if not submission_dir.exists():
        print('Submission directory does not exist.')
        return -1
    if not images_root_dir.exists():
        print('Images Root directory does not exist.')
        return -1

    img_regex = re.compile(r'.*\d\d\d\.(png|jpg|jpeg)')



    # サブミッション名からフレームレート値へのマップを作成。
    fps_list = {}
    for entry in submission_dir.iterdir():
        if not entry.is_file():
            continue

        fps = 0
        with zipfile.ZipFile(entry, 'r') as zip_ref:
            ext_files = zip_ref.namelist()
            fps_file = next((file for file in ext_files if Path(file).name == 'fps.txt'), None)
            if fps_file:
                try:
                    with zip_ref.open(fps_file, 'r') as file:
                        txt = io.TextIOWrapper(file)
                        line = txt.readline().strip()
                        fps = int(line)
                except:
                    try:
                        with zip_ref.open(fps_file, 'r') as file:
                            txt = io.TextIOWrapper(file, encoding='utf-16')
                            line = txt.readline().strip()
                            fps = int(line)
                    except Exception as e:
                        print('failed to read fps.txt')
                        print(e)
                        fps = 30

        fps_list[entry.stem] = fps

    # 指定されたフレームレートで動画をエンコード。
    for submission_name, fps in fps_list.items():
        images_dir = images_root_dir / ('_images_' + submission_name)
        renderer_info = renderer_infos[submission_name]
        file_name = renderer_info[1].replace(' ', '_') + \
            '__' + renderer_info[0].replace(' ', '_') + \
            '__' + renderer_info[2]

        for file in images_dir.iterdir():
            if file.is_file():
                first_file = file
                break
        ext = first_file.suffix

        if fps != 0:
            try:
                # 動画作成。
                cmd = ['ffmpeg', '-y']
                # cmd += ['-stream_loop', '2'] # 3回繰り返し
                # Opitions for input
                cmd += ['-framerate', str(fps), '-i', f'{images_dir}\\input_%03d{ext}']
                # Options for output
                cmd += ['-c:v', 'libx264', '-pix_fmt', pix_fmt, '-crf', '12', f'{images_root_dir}\\{file_name}.mp4']
                run_command(cmd)
            except Exception as e:
                print(f'{submission_name} failed.')
        else:
            shutil.copy2(first_file, f'{images_root_dir}\\{file_name}{ext}')

    return 0

if __name__ == '__main__':
    try:
        run()
    except Exception as e:
        print(e)
