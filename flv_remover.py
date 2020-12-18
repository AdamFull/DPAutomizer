import os
import shutil
import subprocess
from pathlib import Path

output_dir = "/Output"
target_path = ""
optres_dir_name = ""
bBuildAmazon = False
optres_dir_amazon_name = ""
optmov_dir_name = ""

android_res_ver = 1
android_pack_name = ""

bRebuildAll = True

executable_dir = os.path.dirname(os.path.abspath(__file__))

locs = {"EN" : "res/data", "FR" : "res/data_fr/data", "DE" : "res/data_de/data",
 "JP" : "res/data_jp/data", "RU" : "res/data_ru/data", "CZ" : "res/data_cz/data",
  "NL" : "res/data_nl/data", "GER" : "res/data_de/data", "CS" : "res/data_cs/data"}

def forceMergeFlatDir(srcDir, dstDir):
    if not os.path.exists(dstDir):
        os.makedirs(dstDir)
    for item in os.listdir(srcDir):
        srcFile = os.path.join(srcDir, item)
        dstFile = os.path.join(dstDir, item)
        forceCopyFile(srcFile, dstFile)

def forceCopyFile (sfile, dfile):
    if os.path.isfile(sfile):
        shutil.copy2(sfile, dfile)

def isAFlatDir(sDir):
    for item in os.listdir(sDir):
        sItem = os.path.join(sDir, item)
        if os.path.isdir(sItem):
            return False
    return True


def copyTree(src, dst):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isfile(s):
            if not os.path.exists(dst):
                os.makedirs(dst)
            forceCopyFile(s,d)
        if os.path.isdir(s):
            isRecursive = not isAFlatDir(s)
            if isRecursive:
                copyTree(s, d)
            else:
                forceMergeFlatDir(s, d)


def main():
    global bRebuildAll

    target_path = input("Type target path: ")
    output_dir = input("Type output folder (Default /Output/): ") or os.path.join(executable_dir, "Output")
    output_dir = os.path.abspath(output_dir)
    optres_dir_name = input("Type optimized resource folder name (Default opt_res): ") or "opt_res"
    bBuildAmazon = ("Yes" == input("Do you want to build amazon resources? (Default No): ")) or False
    if bBuildAmazon:
        optres_dir_amazon_name = input("Type optimized amazon resources folder name (Default opt_res): ") or "opt_res"
    else:
        optres_dir_amazon_name = optres_dir_name
    optmov_dir_name = input("Type optimized movies folder name (Default None): ") or ""
    android_res_ver = int(input("Type pack version for android (Default 1): ") or "1")
    android_pack_name = input("Type pack name for android (Default XXX): ") or "XXX"

    print(f"Creating output folder {output_dir}, and copying resources.")

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    else:
        bRebuildAll = input("Resources already exist. Do you want rebuild them? (Default No): ") or "No"
        if bRebuildAll == "Yes":
            shutil.rmtree(output_dir)

    if bRebuildAll == "Yes":
        for dirr in os.listdir(target_path):
            if dirr in locs.keys():
                dir_from = os.path.join(target_path, dirr + "/Data")
                dir_to = os.path.join(output_dir, locs[dirr])
                if dirr == "EN":
                    copyTree(dir_from, dir_to)
                else:
                    print("Working on folder: %s" % dirr)
                    subprocess.Popen(["DiffAndCopy.exe", f"testDir={dir_from}",  f"base_dir={os.path.join(target_path, 'EN/Data')}", f"copy_dir={dir_to}"]).wait()

        print(f"Walking on path: {output_dir}")

        for root, dirs, files in os.walk(output_dir):
            for file in files:
                filepath = os.path.join(root, file)
                if Path(filepath).suffix == ".flv" or Path(filepath).suffix == ".tmp":
                    os.remove(filepath)
                    print(f"Deleting {filepath}")

        if optres_dir_name != optres_dir_amazon_name:
            print("Dublicating amazon folder")
            amazon_res_path = os.path.join(output_dir, "res_amaz")
            google_res_path = os.path.join(output_dir, "res")
            print(amazon_res_path, google_res_path)
            copyTree(google_res_path, amazon_res_path)
            
            print("Copying optimized resources for amazon")
            opt_res_path = os.path.join(target_path, optres_dir_amazon_name)
            for folder in os.listdir(opt_res_path):
                full_cur_path = os.path.join(opt_res_path, folder)
                if folder == "data_en":
                    copyTree(os.path.join(full_cur_path, "data"), os.path.join(output_dir, "res_amaz/data"))
                else:
                    copyTree(os.path.join(full_cur_path, "data"), os.path.join(output_dir, f"res_amaz/{folder}"))

    
        print("Copying optimized resources")
        opt_res_path = os.path.join(target_path, optres_dir_name)
        for folder in os.listdir(opt_res_path):
            full_cur_path = os.path.join(opt_res_path, folder)
            if folder == "data_en":
                copyTree(os.path.join(full_cur_path, "data"), os.path.join(output_dir, "res/data"))
            else:
                copyTree(os.path.join(full_cur_path, "data"), os.path.join(output_dir, f"res/{folder}"))

        if optmov_dir_name:
            print("Copying optimized movies")
            opt_mov_path = os.path.join(target_path, optmov_dir_name)
            for folder in os.listdir(opt_mov_path):
                full_cur_path = os.path.join(opt_mov_path, folder)
                if folder == "data_en":
                    copyTree(os.path.join(full_cur_path, "data"), os.path.join(output_dir, "res/data"))
                else:
                    copyTree(os.path.join(full_cur_path, "data"), os.path.join(output_dir, f"res/{folder}"))


    print("Packing for android")
    android_output = os.path.join(output_dir, "Android")
    os.mkdir(android_output)
    output_pack_path = os.path.join(android_output, f"main.{android_res_ver}.com.dominigames.{android_pack_name}.obb")
    input_pack_path = os.path.join(output_dir, 'res')
    subprocess.Popen(["dominiPacker.exe", f"in={input_pack_path}", f"out={output_pack_path}", "single_pack=1", "npot_type=0"]).wait()

    if bBuildAmazon:
        print("Packing for amazon")
        amazon_output = os.path.join(output_dir, "Amazon")
        os.mkdir(amazon_output)
        if optres_dir_name == optres_dir_amazon_name:
            subprocess.Popen(["dominiPacker.exe", f"in={os.path.join(output_dir, 'res')}", f"out={os.path.join(amazon_output, '1024.pak')}", "max_block_size=10000000", "npot_type=0", "target=android"]).wait()
        else:
            subprocess.Popen(["dominiPacker.exe", f"in={os.path.join(output_dir, 'res_amaz')}", f"out={os.path.join(amazon_output, '1024.pak')}", "max_block_size=10000000", "npot_type=0", "target=android"]).wait()
    
    print(f"Done, Saved in {output_dir}")

if __name__ == "__main__":
    main()