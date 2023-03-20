# Import necessary libraries
import os
import struct
import tkinter as tk
from tkinter import filedialog

# Create a GUI for selecting the input file
root = tk.Tk()
root.withdraw()
print("Please select the folder containing the files to be packed.")
folder_path = filedialog.askdirectory()

# Create a list of files to be packed
file_list = []
for file_name in os.listdir(folder_path):
    if os.path.isfile(os.path.join(folder_path, file_name)):
        file_list.append(file_name)

# Create a GUI for selecting the input .WAD file
root = tk.Tk()
root.withdraw()
print("Please select the input .WAD file.")
file_path = filedialog.askopenfilename()

# Define the file paths for the input INF and WAD files and the output WAD file
INF_FILE = file_path[:-4] + ".INF"
PACK_FILE = file_path
OUTPUT_FILE = PACK_FILE[:-4] + "_NEW.WAD"

# Create a list to store the offset and size information for each file
file_info = []

# Open the INF file for reading and get the number of entries
with open(INF_FILE, "rb") as f_inf:
    file_size = os.path.getsize(INF_FILE)
    num_entries = file_size // 24

    # Loop over each entry and store the offset and size information
    for i in range(num_entries):
        offset = struct.unpack("<L", f_inf.read(4))[0]
        offset *= 0x800
        size = struct.unpack("<L", f_inf.read(4))[0]
        # Read the name of the file and decode it as a UTF-8 string
        name = f_inf.read(0x10).decode("utf-8").rstrip("\0")
        file_info.append((name, offset, size))

# Open the output file for writing
with open(OUTPUT_FILE, "wb") as f_out:

    # Loop over each file in the list and write its contents to the output file
    for name, offset, size in file_info:
        if name in file_list:
            with open(os.path.join(folder_path, name), "rb") as f_in:
                data = f_in.read()
                f_out.seek(offset)
                f_out.write(data)

# Update the INF file with the new offset and size information
with open(INF_FILE, "wb") as f_inf:
    for name, offset, size in file_info:
        offset //= 0x800
        f_inf.write(struct.pack("<L", offset))
        f_inf.write(struct.pack("<L", size))
        # Encode the name of the file as a byte string and pad it with null bytes
        name_bytes = name.encode("utf-8")
        name_bytes += b"\0" * (0x10 - len(name_bytes))
        f_inf.write(name_bytes)

# Print a message indicating the operation is complete
print("Operation complete. The new file is located at " + OUTPUT_FILE + ".")
