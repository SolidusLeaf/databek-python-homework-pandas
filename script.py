import pandas as pd
import datetime as dt
from pathlib import Path
# Load the dataset
def check_data_types_and_duplicates(df):
    """
    This function checks the data types of the dataset and identifies any duplicates.
    Used for the first time to check the data types and duplicates in the dataset.
    Mostly read-only, possible to drop duplicates if found. The function also checks for missing values in the dataset.
    """
    print("\n"+"="*60)
    print("Data Types of the Dataset:")
    print(df.dtypes)
    
    input("\nPress Enter to continue...") 
    print("="*30)
    print("First 5 rows of the dataset:\n")
    print(df.head(5))
    print("\n"+"*"*30)
    print("If data types are not correct, you can use the convert_simple_types() "+
    "or convert_datetime() functions to convert them.")
    input("\nPress Enter to continue...")
    print("="*30)
    print("Checking for missing values in the dataset:\n")
    columns=df.columns
    for column in columns:
        if df[column].isnull().sum() > 0:
            print(f"Column '{column}' has {df[column].isnull().sum()} missing values.")
        else:
            print(f"Column '{column}' has no missing values.")
    input("\nPress Enter to continue...")

 
  
    print("="*30)
    duplicates = df.duplicated()
    if duplicates.sum() > 0:
        print("Duplicates found in the dataset.")
        print("Number of duplicates: ", duplicates.sum())
        show_duplicates=df[duplicates]
        print("Duplicates:\n " + str(show_duplicates))
        print("Do you want to drop duplicates? (y/n): ")
        while True:
            answer=input().lower()
            if (answer == 'y'):
                    df.drop_duplicates(inplace=True)
                    print("Duplicates dropped.")
                    print("Proof of duplicates dropped:\n")

                    print(df[df.duplicated()])
                    
                    print("="*60)
                    break
            elif (answer == 'n'):
                    print("Duplicates not dropped.")
                    print("="*60)
                    break
            else:
                    print("Invalid input. Please enter 'y' or 'n': ")
    else:
        print("No duplicates found in the dataset.")
        print("="*60)
    
    input("\nPress Enter to continue...")
    
def convert_simple_types(df, columns_name, new_type):
    """Convert a column to a new data type.
    Do not use this function for datetime conversion, use convert_datetime() instead.
    """
    for column in columns_name:
        df[column] = df[column].astype(new_type)
    return df


def convert_datetime(df, column_name, dformat="%Y-%m-%d %H:%M:%S"):
    """Convert a column to datetime format."""
    df[column_name] = pd.to_datetime(
        df[column_name].str.strip(),
        format=dformat,
        errors="coerce",
    )
    return df


def check_columns_numeric(df, columns):
    """Check if specified columns are numeric."""
    for column in columns:
        if not pd.api.types.is_numeric_dtype(df[column]):
            print(f"Column '{column}' is not numeric.")
            print("Would you like to convert it to numeric? (y/n): ")
            while True:
                answer = input().lower()
                if answer == 'y':
                    df = convert_columns_to_numeric(df, [column])
                    print(f"Column '{column}' converted to numeric.")
                    break
                elif answer == 'n':
                    print(f"Column '{column}' not converted.")
                    break
                else:
                    print("Invalid input. Please enter 'y' or 'n': ")
        else:
            print(f"Column '{column}' is numeric.")
    print("="*60)


def check_is_datetime(df, column_name, dformat="%Y-%m-%d %H:%M:%S"):
    try:
        pd.to_datetime(df[column_name], format=dformat, errors='raise')
        print(f"Column '{column_name}' is in datetime format.")
    except ValueError:
        print(f"Column '{column_name}' is not in datetime format.")
        print("Would you like to convert it to datetime? (y/n): ")
        while True:
            answer = input().lower()
            if answer == 'y':
                df = convert_datetime(df, column_name, dformat)
                print(f"Column '{column_name}' converted to datetime.")
                break
            elif answer == 'n':
                print(f"Column '{column_name}' not converted.")
                break
            else:
                print("Invalid input. Please enter 'y' or 'n': ")


def convert_columns_to_numeric(df, columns):
    """Convert specified columns to numeric, coercing errors to NaN."""
    for column in columns:
        df[column] = pd.to_numeric(df[column], errors='coerce')
    return df

def drop_missing_values(df):
    """Drop rows with missing values in the dataset."""
    df.dropna(inplace=True)
    return df

def drop_incorrect_date(df, column_name, dformat="%Y-%m-%d %H:%M:%S"):
    """Drop rows with incorrect date format in the specified column."""
    today = dt.datetime.now()
    df[column_name] = pd.to_datetime(df[column_name], format=dformat, errors='coerce')
    df = df[df[column_name].notnull() & (df[column_name] <= today)]
    return df

DATA_PATH = Path(__file__).parent / "orders.csv"
data = pd.read_csv(DATA_PATH)
check_data_types_and_duplicates(data)
check_columns_numeric(data, ['order_id', 'customer_id', 'amount'])
check_is_datetime(data, 'created_at')
filtered_data = drop_missing_values(data)
filtered_data = drop_incorrect_date(filtered_data, 'created_at')
convert_simple_types(filtered_data, ['order_id', 'customer_id'], 'int')
check_data_types_and_duplicates(filtered_data)
# The filtered_data DataFrame now contains the cleaned dataset with correct data types,
# no duplicates, and no missing values. You can proceed with further analysis or save 
# the cleaned dataset to a new CSV file if needed.
per_customer = (
    # Group the filtered data by customer_id and month, and calculate 
    # the total revenue for each group including negative amounts (returns).
    filtered_data.groupby(["customer_id", filtered_data["created_at"].dt.to_period("M").rename("month")])["amount"]
         .agg(revenue="sum")
         .reset_index()
         .sort_values("revenue", ascending=False)
)
print(per_customer)

# Filter the per_customer DataFrame to include only customers with positive revenue
per_customer_profit = per_customer[per_customer["revenue"] > 0]

print(per_customer_profit)
