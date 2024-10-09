import multiprocessing
import subprocess
from glob import glob
from os import cpu_count
from tqdm import tqdm
from pathlib import Path
import argparse

def unpack(pck,wem):
    pck_file = glob(f"{pck}/**/*.pck",recursive=True)
    for pcks in tqdm(pck_file,desc="正在解包音频..."):
        subprocess.run(f"./Tools/quickbms.exe -q -k ./Tools/wwise_pck_extractor.bms \"{pcks}\" \"{wem}\"",stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

def conv_wem(args):
    src, dst = args
    wav_name = Path(src).name.replace(".wem", ".wav")
    wav_dst = f"{dst}/{wav_name}"
    if not Path(wav_dst).exists():
        subprocess.run(f"./Tools/vgmstream-cli.exe -o \"{wav_dst}\" \"{src}\"",stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    

def conv_wem_to_wav(process_count, wem, wav):
    if process_count == 0:
        process_count = cpu_count()
    files = glob(f"{wem}/*.wem")
    file_count = len(files)

    with tqdm(total=file_count, desc="正在转码音频，请耐心等待完成...") as progress_bar:
        with multiprocessing.Pool(process_count) as pool:
            args = [(file, wav) for file in files]
            for result in pool.imap_unordered(conv_wem, args):
                progress_bar.update(1)

# 示例调用
if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("-p","--pck", type=str, help="pck文件夹路径", default="./Data/pcks")
    args.add_argument("-r","--wem", type=str, help="wem文件夹路径", default="./Data/raw")
    args.add_argument("-w","--wav", type=str, help="wav文件夹路径", default="./Data/wav")
    args.add_argument("-c","--process_count", type=int, default=0, help="进程数")
    args = args.parse_args()
    
    if not Path(args.pck).exists() or not Path(args.wem).exists():
        Path(args.wav).mkdir(parents=True, exist_ok=True)
        Path(args.wem).mkdir(parents=True, exist_ok=True)
    
    unpack(args.pck,args.wem)
    conv_wem_to_wav(args.process_count, args.wem, args.wav)
    tqdm.write(f"解包/转码完成！可在 {args.wav} 目录找到转码后的音频。")
    
