import pandas as pd
import configparser

data = None

# Load spreadsheet from the config file
config = configparser.ConfigParser()
config.read('config.ini')

sheet_url = config['spreadsheet']['url']

# Read the sheet into a DataFrame
data = pd.read_csv(sheet_url)

# Display the entire DataFrame
#print(data)

# Rows to extracts from the spreadsheet
n = int(config['spreadsheet']['start'])
m = int(config['spreadsheet']['finish'])

def generate_sheet(n, m):
    
    sheet = {}
    keys = []

    for pair in get_crypto_pairs(n, m):
        keys.append(pair)
    
    for i in range(len(keys)):
        pair = keys[i]
        p25 = list(get_25pourcents(n, m))[i] # List to convert the generator / yield
        p50 = list(get_50pourcents(n, m))[i]
        p75 = list(get_75pourcents(n, m))[i]
        p100 = list(get_100pourcents(n, m))[i]
        sheet[pair] = [p25, p50,p75, p100]
    return sheet


def get_crypto_pairs(start_row, end_row):
    for row in range(start_row, end_row + 1):
        # Convert USD from the Excel to USDT
        if data.iloc[row, 1] == "USD":
            value = f"{data.iloc[row, 1]}T"
        else:
            value = f"{data.iloc[row, 1]}"
        #print(value)
        yield value  # Yielding the value instead of returning it, so you can handle multiple values if needed.

def get_25pourcents(start_row, end_row):
    for row in range(start_row, end_row + 1):
        value = f"{data.iloc[row, 6]}"
        #print(value)
        yield value  # Yielding the value instead of returning it, so you can handle multiple values if needed.

def get_50pourcents(start_row, end_row):
    for row in range(start_row, end_row + 1):
        value = f"{data.iloc[row, 7]}"
        #print(value)
        yield value  # Yielding the value instead of returning it, so you can handle multiple values if needed.

def get_75pourcents(start_row, end_row):
    for row in range(start_row, end_row + 1):
        value = f"{data.iloc[row, 8]}"
        #print(value)
        yield value  # Yielding the value instead of returning it, so you can handle multiple values if needed.

def get_100pourcents(start_row, end_row):
    for row in range(start_row, end_row + 1):
        value = f"{data.iloc[row, 5]}"
        #print(value)
        yield value  # Yielding the value instead of returning it, so you can handle multiple values if needed.


#generate_sheet(n, m)