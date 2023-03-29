import os
import struct
import shutil
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
NEW_INF_FILE = PACK_FILE[:-4] + "_NEW.INF"

# Copy the original INF file to the new one
shutil.copy(INF_FILE, NEW_INF_FILE)

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

# Create a list to store the updated offset values
updated_offsets = []

# Create a list to store the modified file information
modified_files = []

# Open the output file again for reading and writing
with open(OUTPUT_FILE, "wb") as f_out:
    f_out.truncate(os.path.getsize(PACK_FILE))
    index = 0  # initialize index
    end_offset = 0
    for i, (name, offset, size) in enumerate(file_info):
        if name in file_list:
            with open(os.path.join(folder_path, name), "rb") as f_in:
                data = f_in.read()
                f_out.seek(offset)
                f_out.write(data)
                # Update the offset to reflect the new location in the output file
                new_offset = f_out.tell() // 0x800
                # Store the updated offset value in the list
                updated_offsets.append(new_offset)
                # Update the size value in the file_info list to match the original size
                file_info[index] = (name, offset, len(data))
                index += 1  # increment index
                end_offset = new_offset
                print(f"File {name} written at offset {offset}, new offset: {new_offset}, size: {len(data)}")
                
                # Check if the current file overlaps with the next file
                if i < len(file_info) - 1:
                    cur_end_offset = offset + len(data)
                    next_start_offset = file_info[i+1][1]
                    if cur_end_offset > next_start_offset:
                        # Adjust the start offset of the next file to the next multiple of 0x800
                        next_start_offset = ((cur_end_offset // 0x800) + 1) * 0x800
                        file_info[i+1] = (file_info[i+1][0], next_start_offset, file_info[i+1][2])
                        if i+1 < len(updated_offsets):
                         updated_offsets[i+1] = next_start_offset // 0x800
                        else:
                         updated_offsets.append(next_start_offset // 0x800)
                         print(f"File {file_info[i+1][0]} moved to offset {updated_offsets[i+1] * 0x800}")
        else:
            # If the file is not in the file_list, add its original offset value to the list
            updated_offsets.append(offset // 0x800)
            index += 1
            
    # Check if end offset is valid
    file_size = os.path.getsize(OUTPUT_FILE)
    if (end_offset + 1) * 0x800 > file_size:
        print("End offset is invalid")
        
# Open the original WAD file and read its contents into a bytes object
    with open(PACK_FILE, "rb") as f_in:
        original_data = f_in.read()

# Open the output WAD file and read its contents into
    with open(OUTPUT_FILE, "rb") as f_out:
        new_data = f_out.read()

    #Compare the original and new data to find the offsets of any modified files
    for name, offset, size in file_info:
        if name in file_list:
            original_file = original_data[offset:offset+size]
new_offset = new_data.find(original_file)
if new_offset != offset:
        modified_files.append((name, new_offset))

#Open the new INF file for writing
with open(NEW_INF_FILE, "wb") as f_inf:
        index = 0
        # Compare the original and new data to find the offsets of any modified files
for name, offset, size in file_info:
    if name in file_list:
        original_file = original_data[offset:offset+size]
        new_offset = new_data.find(original_file)
        if new_offset != offset:
            modified_files.append((name, new_offset))

with open(NEW_INF_FILE, "wb") as f_inf:
    for name, offset, size in file_info:
        if name in file_list:
            # Calculate the new offset for modified files
            if modified_files and (name, offset) in modified_files:
                offset = new_offset
            # Get the new size of the modified file
            new_size = len(open(os.path.join(folder_path, name), "rb").read())
        else:
            new_size = size
        # Write the updated offset and size to the INF file
        f_inf.write(struct.pack("<L", offset // 0x800))
        f_inf.write(struct.pack("<L", new_size))
        # Encode the name of the file as a byte string and pad it with null bytes
        name_bytes = name.encode("utf-8")
        name_bytes += b"\0" * (0x10 - len(name_bytes))
        f_inf.write(name_bytes)


print("File packing complete.")
