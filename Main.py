import pandas as pd
import numpy as np

ministries_budget=pd.read_excel(r"C:\Users\suraj\Documents\suraj doc\Ministry_Wise_Budget_2024-25.xlsx")
ministries_expense= pd.read_excel(r"C:\Users\suraj\Documents\suraj doc\Ministry_Wise_Actual_Expenditure.xlsx")


ministries_budget.drop("FY_2022-23_Actuals", axis=1, inplace=True)
ministries_budget.drop("FY_2023-24_Revised",axis =1 , inplace = True)
ministries_expense.rename(columns={"FY_2024-25_Budget_Estimate":"Net allocation"},inplace= True)
print(ministries_expense)


cag_reports = pd.read_excel(r"C:\Users\suraj\Documents\suraj doc\CAG_Report_Audit_Underutilization_Trimmed.xlsx")
cag_reports.rename(columns={"Grant Number & Ministry/Department":"Departments"},inplace=True)
cag_reports["Departments"] = (
    cag_reports["Departments"]
    .astype(str)
    .str.replace("Grant No.", "", regex=True)
    .str.replace(r"\d+", "", regex=True)
    .str.replace(" - ", "", regex=True)
    .str.strip()
)
