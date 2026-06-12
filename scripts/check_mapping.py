import openpyxl
wb = openpyxl.load_workbook("E:/Codex Workspace/04_projects/\u9879\u76ee\u6587\u6863/\u4f18\u5316\u540eexcel\u914d\u7f6e\u8868/\u7acb\u5373\u9065\u63a7\u6307\u4ee4\u914d\u7f6e\u8868.xlsx")
ws2 = wb["\u679a\u4e3e\u503c\u6620\u5c04\u8868"]
for r in ws2.iter_rows(min_row=2, values_only=True):
    print(f"{r[0]:<10} {str(r[1]):<25} {str(r[2]):<22} {str(r[3]):<8} {str(r[4]):<20}")
