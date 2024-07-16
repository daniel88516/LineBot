# pyinstaller --onefile --windowed --add-data "C:/Python38/tkdnd;tkdnd" csv轉換.py
# pyinstaller --onefile --windowed --add-data "your_path_to_python_tkdnd" your_script_name.py
import pandas as pd
import os
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
# 定義欄位對應關係
column_mapping = {
    'gender': ['gender', 'gen', 'isMale', 'sex'],
    'age': ['age', 'age', 'years'],
    'bmi': ['bmi', 'bidymassindex'],
    'hba1c_level': ['hba1c', 'HbA1c_Level', 'hba1c_level'],
    'blood_glucose_level': ['bloodglucose', 'bloodsugar', 'bloodglucoselevel', 'blood_glucose_level']
}

def process_file(file_path):
    # 讀取輸入的檔案
    df = pd.read_csv(file_path)
    # 標題都轉換成小寫, 去掉空格
    df = df.rename(columns=lambda x: x.lower().strip())
    # 紀錄篩選過後的資料
    filtered_df = pd.DataFrame()

    # 篩選然後重新命名欄位
    # standardName 'gender'
    # possibleNames = ['gender', 'gen', 'isMale', 'sex']
    for standardName, possibleNames in column_mapping.items():
        for possibleName in possibleNames:
            # 如果有出現在 possibleNames 當中, 加入到 dataFrame 當中
            if possibleName in df.columns:
                filtered_df[standardName] = df[possibleName]
                break

    # 將包含 None 的列去除
    filtered_df = filtered_df.dropna()
    
    dir_name, base_name = os.path.split(file_path)
    # 重新命名成 convert_<檔案名稱>
    output_file = os.path.join(dir_name, f'convert_{base_name}')
    # 轉換成 csv 檔案
    filtered_df.to_csv(output_file, index=False)
    print(f'檔案已儲存:{output_file}')

def drop(event):
    file_path = event.data
    # 去除拖曳之後, 操作系統自動新增的括號
    if file_path.startswith('{') and file_path.endswith('}'):
        file_path = file_path[1:-1]
    process_file(file_path)

root = TkinterDnD.Tk()
root.title('CSV 檔案轉換')
root.geometry('400x200')

label = tk.Label(root, text = "拖放 CSV 檔案以轉換", padx = 10, pady = 10)
label.pack(expand = True, fill = tk.BOTH)

root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', drop)

root.mainloop()