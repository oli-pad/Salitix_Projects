import os

def delete_files(source_folder, target_folder):
    for filename in os.listdir(source_folder):
        print(f"Processing file: {filename}")
        source_path = os.path.join(source_folder, filename)
        target_path = os.path.join(target_folder, filename)

        if os.path.isfile(target_path):
            os.remove(target_path)
            print(f"Deleted file: {target_path}")
        
        if os.path.isfile(source_path):
            os.remove(source_path)
            print(f"Deleted file: {source_path}")

# Usage example
source_folder = r"W:\Audit\Maxxium\Invoice Images\ImageStagingBay\Tesco\Incorrect"
target_folder = r"W:\Audit\Maxxium\Invoice Images"
delete_files(source_folder, target_folder)
