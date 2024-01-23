import shutil
import os
name="Test1.txt"
shutil.move(os.path.join(os.path.join(os.path.expanduser('~'), 'downloads'),name),os.path.join(r"Z:\Youngs",name))
