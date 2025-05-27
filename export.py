import pandas as pd
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['companies']
collection = db['info']


cursor = collection.find({})

df = pd.DataFrame()

for doc in cursor:
    df = df._append(doc, ignore_index=True)


columns = ['Tên công ty', 'Mã số thuế', 'Website', 'Email', 'Điện thoại']
df = df.reindex(columns=columns)


df.fillna('', inplace=True)


header_format = {
    'align': 'center',
    'valign': 'vcenter',
    'bold': True,
    'text_wrap': True,
    'border': 1
}

data_format = {
    'align': 'center',
    'valign': 'vcenter',
    'text_wrap': True,
    'border': 1
}


with pd.ExcelWriter('company_info.xlsx', engine='xlsxwriter') as writer:
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, workbook.add_format(header_format))

    for row_num in range(1, len(df) + 1):
        for col_num, value in enumerate(df.iloc[row_num - 1]):
            worksheet.write(row_num, col_num, value, workbook.add_format(data_format))

    for i, col in enumerate(df.columns):
        max_len = df[col].astype(str).map(len).max()
        worksheet.set_column(i, i, max_len + 2)

    for i in range(len(df) + 1):
        worksheet.set_row(i, 30)

print("Excel file 'company_info.xlsx' has been created with centered text, space between columns, and space between rows.")
