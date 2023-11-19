from forex_python.converter import CurrencyRates
from math import ceil, floor
from pathlib import Path
from pprint import pprint
import pandas as pd
import sys

# setup
def setup(db_path: Path, file_type: str) -> pd.DataFrame:
    local_currency = "EUR"
    cr = CurrencyRates()
    df = pd.read_excel(db_path, engine=file_type)
    # print(df[["Name", "Price", "Currency"]])
    converted_to_local: list[float] = list()
    normalized_weights: list[float] = list()
    for price, currency in zip(df["Price"], df["Currency"]):
        if currency != local_currency:
            converted_to_local.append(round(cr.convert(currency, local_currency, price), 2))
        else:
            converted_to_local.append(price)
    # print(converted_to_local)
    df["Converted Price"] = converted_to_local

    max_price: float = max(df["Converted Price"])
    max_priority: int = df["Priority"].size
    for price, priority in zip(df["Converted Price"], df["Priority"]):
        normalized_weights.append((price / max_price) * (priority / max_priority))
    
    # print(normalized_weights)
    df["Weights"] = normalized_weights

    return df
# end setup

# main
def main() -> None:

    budget: float = float(sys.argv[1])

    # specific arguments should be "db.ods" and "odf"
    wishlist_df: pd.DataFrame = setup(Path(sys.argv[2]), sys.argv[3])
    total, selected_items = knapsack_dynamic_programming_df(budget, wishlist_df)

    # print(wishlist_df)
    print(f"main - knapsack's result: {total}")
    pprint(f"main - list of items: {selected_items}")
# end main

# chatGPT knapsack
def knapsack_dynamic_programming_df(budget, df):
    n = len(df)
    budget = int(budget * 100)  # Convert budget to cents to work with integers
    df["Converted Price"] = (df["Converted Price"] * 100).astype(int)  # Convert prices to cents

    dp = [[0] * (budget + 1) for _ in range(n + 1)]
    total_price = 0
    selected_items = []

    for i in range(1, n + 1):
        for w in range(budget + 1):
            if df.at[i - 1, "Converted Price"] <= w:
                dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - df.at[i - 1, "Converted Price"]] + df.at[i - 1, "Priority"])
            else:
                dp[i][w] = dp[i - 1][w]

    w, h = budget, n
    while w > 0 and h > 0:
        if dp[h][w] != dp[h - 1][w]:
            total_price += df.at[h - 1, "Converted Price"]
            selected_items.append((df.at[h - 1, "Name"], df.at[h - 1, "Link"]))
            w -= df.at[h - 1, "Converted Price"]
        h -= 1

    selected_items.reverse()

    return total_price / 100, selected_items  # Convert back to the original scale for readability

# end chatGPT knapsack

if __name__ == "__main__":
    main()
    
