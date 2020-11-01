# HOW SCRIPT WORKS:
# 1. Place input csv files from Pennies into root directory of repository
# 2. Run script from that root directory
# 3. Let the parsing happen!

import pandas as pd
import os
import datetime

# Folder path of input CSV files
folderPath = os.getcwd()

# Output DataFrames
jouExpenses = pd.DataFrame(columns=["category", "item", "JOU", "datetime"])
dansExpenses = pd.DataFrame(columns=["category", "item", "cost", "datetime"])
johnsExpenses = pd.DataFrame(columns=["category", "item", "cost", "datetime"])

# LOOP THROUGH EVERY CSV FILE
for csvFile in os.listdir(folderPath):
    # Skips files in folder that aren't .csv files
    if not csvFile.endswith(".csv"):
        continue

    # Use csv file to create DataFrame
    expenses_cols = ["date", "time", "item", "cost", "income", "balanceDay", "balancePeriod"]
    expenses = pd.read_csv(os.path.join(folderPath, csvFile), names=expenses_cols, header=0, thousands=",") # <= Added thousands for parsing large numbers

    # Parse CSV file title to get category name & budget
    csvFileSplit = csvFile.split("-")
    descriptionSplit = csvFileSplit[0].split(" ")
    category = descriptionSplit[0]
    budget = float(descriptionSplit[1][1:]) / 2
    
    # Add datetime column & category column
    expenses["datetime"] = expenses["date"] + " " + expenses["time"]
    expenses["datetime"] = pd.to_datetime(expenses["datetime"], yearfirst=True, format="%Y-%m-%d %H:%M %p")
    expenses.insert(0, "category", category)

    # Convert cost to negative (to reflect loss)
    expenses["cost"] = -expenses["cost"]
    # Move income to cost column if it's not empty
    expenses["cost"] = expenses["income"].where(expenses["income"].notnull(), expenses["cost"])

    # Delete unnecessary columns
    expenses.drop(["date", "time", "income", "balanceDay", "balancePeriod"], axis=1, inplace=True)
    
    # Create empty lists
    today = datetime.datetime.today()
    startOfLastMonth = today.replace(month=today.month-1, day=1, hour=0, minute=0, second=0, microsecond=0)
    budgetBumpRow = [category, "BUDGET BUMP", budget, startOfLastMonth.strftime("%Y-%m-%d %H:%M %p")]
    
    dansItems = [budgetBumpRow]
    johnsItems = [budgetBumpRow]
    jouItems = []
    
    # Loop through every row of DataFrame and parse data into one of the 3 lists above
    for index, row in expenses.iterrows():
        # Case 1: Dan bought on his own
        if str(row["item"]).startswith("D ") and str(row["item"]).endswith(" D"):
            dansItem = []
            for cell in row:
                dansItem.append(cell)
            dansItems.append(dansItem)

        # Case 2: John bought on his own
        if str(row["item"]).startswith("J ") and str(row["item"]).endswith(" J"):
            johnsItem = []
            for cell in row:
                johnsItem.append(cell)
            johnsItems.append(johnsItem)

        # Case 3: Dan bought for both
        if str(row["item"]).startswith("D ") and str(row["item"]).endswith(" JD"):
            dansItem = []
            johnsItem = []
            jouItem = []
            splitCost = row["cost"] / 2
            row["cost"] = splitCost
            for cell in row:
                dansItem.append(cell)
                johnsItem.append(cell)
                jouItem.append(cell)
            dansItems.append(dansItem)
            johnsItems.append(johnsItem)
            jouItems.append(jouItem)
            
        # Case 4: John bought for both
        if str(row["item"]).startswith("J ") and str(row["item"]).endswith(" JD"):
            dansItem = []
            johnsItem = []
            jouItem = []
            splitCost = row["cost"] / 2
            row["cost"] = splitCost
            for cell in row:
                dansItem.append(cell)
                johnsItem.append(cell)
                jouItem.append(cell)
            jouItem[2] = -jouItem[2] # because I owe John now
            dansItems.append(dansItem)
            johnsItems.append(johnsItem)
            jouItems.append(jouItem)

        # Case 5: We bought separate but it's one entry
        if str(row["item"]).startswith("JD ") and str(row["item"]).endswith(" JD"):
            dansItem = []
            johnsItem = []
            splitCost = row["cost"] / 2
            row["cost"] = splitCost
            for cell in row:
                dansItem.append(cell)
                johnsItem.append(cell)
            dansItems.append(dansItem)
            johnsItems.append(johnsItem)
        
        # Case 6: Dan bought for John
        if str(row["item"]).startswith("D ") and str(row["item"]).endswith(" J"):
            johnsItem = []
            jouItem = []
            for cell in row:
                johnsItem.append(cell)
                jouItem.append(cell)
            johnsItems.append(johnsItem)
            jouItems.append(jouItem)
        
        # Case 7: John bought for Dan
        if str(row["item"]).startswith("J ") and str(row["item"]).endswith(" D"):
            dansItem = []
            jouItem = []
            for cell in row:
                dansItem.append(cell)
                jouItem.append(cell)
            jouItem[2] = -jouItem[2] # because I owe John now
            dansItems.append(dansItem)
            jouItems.append(jouItem)

    # Create DataFrame out of lists
    jouItems = pd.DataFrame(jouItems, columns=["category", "item", "JOU", "datetime"])
    jouItems["JOU"] = -jouItems["JOU"] # Because positives are easier to read
    dansItems = pd.DataFrame(dansItems, columns=["category", "item", "cost", "datetime"])
    johnsItems = pd.DataFrame(johnsItems, columns=["category", "item", "cost", "datetime"])
    # Append new DataFrames to output DataFrames
    jouExpenses = jouExpenses.append(jouItems, ignore_index=True, sort=False)
    dansExpenses = dansExpenses.append(dansItems, ignore_index=True, sort=False)
    johnsExpenses = johnsExpenses.append(johnsItems, ignore_index=True, sort=False)
    # Sorts output DataFrames by category and then datetime
    jouExpenses.sort_values(["category", "datetime"])
    dansExpenses.sort_values(["category", "datetime"])

# Turn output DataFrames into CSV files
jouExpenses.to_csv(os.path.join(folderPath, "jouExpenses.csv"), encoding="utf-8")
dansExpenses.to_csv(os.path.join(folderPath, "dansExpenses.csv"), encoding="utf-8")
johnsExpenses.to_csv(os.path.join(folderPath, "johnsExpenses.csv"), encoding="utf-8")

print("Files have been successfully parsed!\nLook for jouExpenses.csv, dansExpenses.csv, and johnsExpenses.csv in your root directory")