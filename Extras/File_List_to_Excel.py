import os
import pandas as pd

path = input("Filepath? >")

list = []

for (root, dirs, file) in os.walk(path):
    for f in file:
        print(f)
        list.append(os.path.join(root,f))

pd.DataFrame(list).to_excel(os.path.join(os.path.join(os.path.expanduser('~'), 'Downloads'),'FileListtoCSV.xlsx'), header=False, index=False)
