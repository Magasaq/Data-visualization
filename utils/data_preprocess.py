import pandas as pd

def load_and_clean_data():
    df = pd.read_csv("melb_data.csv")

    # Drop rows with missing target variable
    df.dropna(subset=["Price"], inplace=True)

    # Drop high-missing or uninformative columns
    df.drop(columns=["Address", "BuildingArea", "YearBuilt", "CouncilArea"], errors="ignore", inplace=True)

    # Fill remaining missing values
    df.fillna(df.median(numeric_only=True), inplace=True)

    # Convert Date column to datetime
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)

    return df
