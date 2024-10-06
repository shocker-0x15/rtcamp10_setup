import sys
import os
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

def run():
    submission_dir = Path(sys.argv[1])
    result_dir = Path(sys.argv[2])
    dir_to_place = Path(sys.argv[3]) if sys.argv[3] != "-" else Path.home()
    time_limit = 256 + 10
    # time_limit = 30 + 10

    # pwsh = 'powershell'
    # Powershell 7以降を導入した場合
    pwsh = 'pwsh'

    if not submission_dir.exists():
        print('Submission directory does not exist.')
        return -1

    dir_to_place.mkdir(parents=True, exist_ok=True)

    result_dir.mkdir(parents=True, exist_ok=True)

    img_regex = re.compile(r'.*\d\d\d\.(png|jpg|jpeg)')



    errors = {}
    for entry in submission_dir.iterdir():
        if not entry.is_file():
            continue

        misc_msg = ''

        # zipをホームディレクトリに展開。
        with zipfile.ZipFile(entry, 'r') as zip_ref:
            ext_files = zip_ref.namelist()
            root_dir_name = os.path.commonprefix(ext_files)
            if root_dir_name == '' or '/' not in root_dir_name:
                root_dir_name = entry.stem
                zip_ref.extractall(dir_to_place / root_dir_name)
            else:
                zip_ref.extractall(dir_to_place)

        working_dir = dir_to_place / root_dir_name
        old_dir = chdir(working_dir)

        # fpsを読み取る。
        if (working_dir / 'fps.txt').exists():
            try:
                with open('fps.txt', 'r') as f:
                    line = f.readline().strip()
                    fps = int(line)
            except:
                try:
                    with open('fps.txt', 'r', encoding='utf-16') as f:
                        line = f.readline().strip()
                        fps = int(line)
                except:
                    misc_msg += 'failed to read fps.txt\n'
                    fps = 60
        else:
            misc_msg += 'fps.txt: not found\n'
            fps = 60

        dst_dir = result_dir / entry.stem
        dst_dir.mkdir(exist_ok=True)
        dst_local_others_dir = dst_dir / 'local_others'
        dst_local_others_dir.mkdir(exist_ok=True)
        img_dir = result_dir / ('_images_' + entry.stem)
        img_dir.mkdir(exist_ok=True)

        # スライドのコピー。
        deck_files = []
        deck_files += working_dir.glob('*.pdf')
        deck_files += working_dir.glob('*.pptx')
        for deck_file in deck_files:
            shutil.copy2(deck_file, dst_dir)

        def get_local_file_list(dir):
            return set([file.name for file in dir.iterdir() if file.is_file()])

        # レンダリング実行前のファイルリストを生成。
        org_files = []
        for file in ext_files:
            if not file.endswith('/') and len(Path(file).parts) == 2:
                org_files.append(Path(file).name)
        org_files = set(org_files)

        # requirements.txtに従ってパッケージインストール。
        if 'requirements.txt' in org_files:
            cmd = ['pip', 'install', '-r', 'requirements.txt']
            run_command(cmd)

        # ローカルマシンの現在時刻を取得。
        start_time = time.time()

        # レンダリング実行。
        cmd = [pwsh, '-ExecutionPolicy', 'Bypass', '-File', './run.ps1']
        # cmd = ['./run.sh']
        stderr = None
        try:
            output = run_command(cmd, timeout=time_limit)
            stdout = output.stdout
            stderr = output.stderr
        except subprocess.CalledProcessError as e:
            stdout = e.stdout
            stderr = e.stderr
        except Exception as e:
            if e.stdout:
                stdout = e.stdout
            if e.stderr:
                stderr = e.stderr

        # 標準出力とエラー出力を書き出す。
        if stdout:
            with open(dst_dir / 'stdout.log', 'w', encoding=encoding) as f:
                f.write(stdout)
        if stderr:
            with open(dst_dir / 'stderr.log', 'w', encoding=encoding) as f:
                f.write(stderr)

        # ローカルマシンのレンダリング実行後のファイルリストを取得。
        files = get_local_file_list(working_dir)
        new_files = files - org_files

        # ローカルマシンで出力された画像をコピー。
        for file in new_files:
            src_file = working_dir / file
            if img_regex.match(file):
                if (src_file.stat().st_mtime - start_time) < time_limit:
                    shutil.copy2(src_file, img_dir)
            else:
                shutil.copy2(src_file, dst_local_others_dir)

        # 連番画像における欠落事故防止のため名前でソートしたのち改めて連番化する。
        ext = None
        img_list = []
        for file in img_dir.iterdir():
            if file.is_file() and ext is None:
                ext = file.suffix
            img_list.append(str(file))
        img_list.sort()
        for idx, file in enumerate(img_list):
            old_name = Path(file)
            new_name = old_name.with_name(f'input_{idx:03}{ext}')
            if new_name.exists():
                new_name.unlink()
            old_name.rename(new_name)

        if len(img_list) > 1:
            try:
                # 動画作成。
                cmd = ['ffmpeg']
                # Opitions for input
                cmd += ['-framerate', str(fps), '-i', f'{img_dir}\\input_%03d{ext}']
                # Options for output
                cmd += ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', f'{dst_dir}\\result.mp4']
                run_command(cmd)
            except Exception as e:
                misc_msg += 'ffmpeg error.\n'
        elif len(img_list) == 1:
            shutil.copy2(img_dir / f'input_{idx:03}{ext}', f'{dst_dir}\\result{ext}')
        else:
            misc_msg += 'No images.\n'
        
        with open(dst_dir / 'misc.txt', 'w') as f:
            f.write(misc_msg)

        chdir(old_dir)

        shutil.rmtree(working_dir)

    return 0

if __name__ == '__main__':
    try:
        run()
    except Exception as e:
        print(e)
