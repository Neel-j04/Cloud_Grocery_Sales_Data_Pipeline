import boto3
import pandas as pd

s3 = boto3.client(
    "s3",
    aws_access_key_id="AKIASZ2U7A32ZBBXACXS",
    aws_secret_access_key="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",
    region_name="us-east-1"
)

# response = s3.list_buckets()

# for bucket in response["Buckets"]:
#     print(bucket["Name"])

obj = s3.get_object(
    Bucket="neel-orders-data-lake",
    Key="orders.csv.csv"
)

df = pd.read_csv(obj["Body"])

print("\n========== DATASET SHAPE ==========\n")
print(df.shape)

print("\n========== DATASET INFO ==========\n")
print(df.info())

print("\n========== NULL VALUES ==========\n")
print(
    df.isnull()
      .sum()
      .sort_values(ascending=False)
      .head(20)
)

print("\n========== DESCRIPTIVE STATS ==========\n")
print(df.describe())

print("\n========== FIRST 20 COLUMNS ==========\n")
print(df.columns[:20])

print("\n========== LAST 20 COLUMNS ==========\n")
print(df.columns[-20:])

# TRANSFORM 1 : DAY NAME
day_map = {
    0: "Sunday",
    1: "Monday",
    2: "Tuesday",
    3: "Wednesday",
    4: "Thursday",
    5: "Friday",
    6: "Saturday"
}

df["day_name"] = df["order_dow"].map(day_map)

# TRANSFORM 2 : IDENTIFY PRODUCT COLUMNS
meta_cols = [
    "order_id",
    "order_dow",
    "order_hour_of_day",
    "days_since_prior_order"
]

product_cols = [
    col
    for col in df.columns
    if col not in meta_cols
]

# Remove newly created column
product_cols = [
    col
    for col in product_cols
    if col != "day_name"
]

# TRANSFORM 3 : TOTAL ITEMS PURCHASED
df["total_items"] = df[product_cols].sum(axis=1)

print("\n========== TOTAL ITEMS ==========\n")
print(
    df[
        [
            "order_id",
            "day_name",
            "total_items"
        ]
    ].head()
)

# TRANSFORM 4 : TOP PRODUCT CATEGORIES
category_sales = (
    df[product_cols]
    .sum()
    .sort_values(ascending=False)
)

print("\n========== TOP 20 PRODUCT CATEGORIES ==========\n")
print(category_sales.head(20))

# TRANSFORM 5 : ORDERS BY DAY
print("\n========== ORDERS BY DAY ==========\n")
print(df["day_name"].value_counts())

# TRANSFORM 6 : ORDERS BY HOUR
print("\n========== ORDERS BY HOUR ==========\n")
print(
    df["order_hour_of_day"]
    .value_counts()
    .sort_index()
)

# TRANSFORM 7 : DUPLICATES
print("\n========== DUPLICATES ==========\n")
print(df.duplicated().sum())

# TRANSFORM 8 : CLEAN COLUMN NAMES
df.columns = (
    df.columns
      .str.strip()
      .str.lower()
      .str.replace(" ", "_")
      .str.replace("-", "_")
)

print("\n========== CLEANED COLUMNS ==========\n")
print(df.columns.tolist())

# EXPORT DATA
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://postgres:Neel2004@localhost:5432/Project_2"
)

df.to_sql(
    "orders",
    engine,
    if_exists="replace",
    index=False
)