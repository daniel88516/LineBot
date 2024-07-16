import pandas as pd

# 定義欄位對應關係
column_mapping = {
    'gender': ['gender', 'gen', 'isMale', 'sex'],
    'age': ['age', 'age', 'years'],
    'bmi': ['bmi', 'bidymassindex'],
    'hba1c_level': ['hba1c', 'HbA1c_Level', 'hba1c_level'],
    'blood_glucose_level': ['bloodglucose', 'bloodsugar', 'bloodglucoselevel', 'blood_glucose_level']
}

# 輸入輸出 .csv 檔案
input_file = '10k.csv'
output_file = 'output.csv'

# 讀取 csv 檔案
df = pd.read_csv(input_file)

# 標題都轉換成小寫
df = df.rename(columns=str.lower)

# 篩選結果
filtered_df = pd.DataFrame()

# 篩選並重新命名欄位
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
# 轉換成 csv 檔案
filtered_df.to_csv(output_file, index=False)
