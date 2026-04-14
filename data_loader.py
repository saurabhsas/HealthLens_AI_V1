import pandas as pd

def load_data(file_path):

    df = pd.read_csv(file_path)

    # Standardize column names
    df.columns = df.columns.str.upper()

    # Create derived columns (safe mapping)
    df["MED_COST"] = df.get("MEDICAL_PAID", 0)
    df["RX_COST"] = df.get("RX_PAID", 0)
    df["TOTAL_COST"] = df.get("PAID", 0)

    return df