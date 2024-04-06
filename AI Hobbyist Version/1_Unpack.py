import os,subprocess,argparse
from glob import glob
from tqdm import  tqdm
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('-p','--pck',type=str,help='pck文件目录',default="./Data/pcks")
parser.add_argument('-r','--wem',type=str,help='wem输出目录',default="./Data/raw")
parser.add_argument('-w','--wav',type=str,help='wav输出目录',default="./Data/wav")
args = parser.parse_args()

pck_path = args.pck
wem_path = args.wem
wav_path = args.wav

if not os.path.exists(wem_path):
    Path(wem_path).mkdir(parents=True)
if not os.path.exists(wav_path):
    Path(wav_path).mkdir(parents=True)

def unpack(pck,wem):
    pck_file = glob(f"{pck}/**/*.pck",recursive=True)
    for pcks in tqdm(pck_file,desc="正在解包音频..."):
        subprocess.run(f"./Tools/quickbms.exe -q -k ./Tools/wwise_pck_extractor.bms \"{pcks}\" \"{wem}\"",stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    
def to_wav(wem,wav):
    wem_file = glob(f"{wem}/**/*.wem",recursive=True)
    for wems in tqdm(wem_file,desc="正在转码音频，请耐心等待完成..."):
        wav_name = os.path.basename(wems).replace(".wem",".wav")
        subprocess.run(f"./Tools/vgmstream-cli.exe -o \"{wav}/{wav_name}\" \"{wems}\"",stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    tqdm.write(f"解包/转码完成！可在 {wav} 目录找到转码后的音频。")
        
unpack(pck_path,wem_path)
to_wav(wem_path,wav_path)