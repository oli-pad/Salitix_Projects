import os
import shutil

# Get Directories to delete out of

directory_path = 'w:/Audit'
folders = [f.name for f in os.scandir(directory_path) if f.is_dir()]
print(folders)

# for folder in folders:
#     folder_path = f"W:\\Audit\\{folder}\\Invoice Images\\ImageStagingBay"
#     if os.path.exists(folder_path):
#         subfolders = [f.name for f in os.scandir(folder_path) if f.is_dir()]
#         print(f"Subfolders in {folder_path}: {subfolders}")

#         for subfolder in subfolders:
#             subfolder_path = os.path.join(folder_path, subfolder)
#             for root, dirs, files in os.walk(subfolder_path):
#                 for file in files:
#                     file_path = os.path.join(root, file)
#                     os.remove(file_path)
#                 for dir in dirs:
#                     dir_path = os.path.join(root, dir)
#                     shutil.rmtree(dir_path)