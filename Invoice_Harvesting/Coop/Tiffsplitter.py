import tifftools
import os

def split_tiff_by_page(file_path,filename,output):
    info = tifftools.read_tiff(os.path.join(file_path,filename,))
    for i, ifd in enumerate(info['ifds']):
        output_path = f"{os.path.join(output,filename)}_{i}.tif"
        tifftools.write_tiff(ifd, output_path)

def listdir_nohidden(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f

def all_images(image_folder,output):
    image_folder_list=[item for item in os.listdir(image_folder) if ".tif" in item or ".TIF" in item]
    for i in image_folder_list:
        try:
            split_tiff_by_page(image_folder,i,output)
        except:
            None

all_images(r'W:\Audit\Pladis\Invoice Images\EmailStagingBay\CoOp',r'W:\Audit\Pladis\Invoice Images\EmailStagingBay\CoOp\to split')
