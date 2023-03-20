import os
import struct
import tkinter as tk
from tkinter import filedialog

# create tkinter root window and hide it
root = tk.Tk()
root.withdraw()

# prompt user for input file
inf_path = filedialog.askopenfilename(title="Select INF file", filetypes=[("INF files", "*.inf")])

# automatically set WAD file path
wad_path = os.path.splitext(inf_path)[0] + ".wad"

# create output folder with the name of the INF file
output_folder = os.path.splitext(inf_path)[0]
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# open input files
with open(inf_path, "rb") as f_inf:
    with open(wad_path, "rb") as f_wad:
        file_size = os.path.getsize(inf_path)
        entries = file_size // 24
        for rip in range(entries):
            offset = struct.unpack("<L", f_inf.read(4))[0]
            offset *= 0x800
            size = struct.unpack("<L", f_inf.read(4))[0]
            name = f_inf.read(0x10).decode("utf-8").rstrip("\0")
            f_wad.seek(offset)
            data = f_wad.read(size)
            ext = os.path.splitext(name)[1]
            output_path = os.path.join(output_folder, os.path.splitext(name)[0] + ext)
            with open(output_path, "wb") as out_file:
                out_file.write(data)

# print info for users
print(f"All files extracted from {os.path.basename(inf_path)} and saved in {output_folder}.")
