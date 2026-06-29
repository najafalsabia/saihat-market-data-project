import pandas as pd

df1 = pd.read_csv("saihat_google_maps_dataset1.csv")
df2 = pd.read_csv("saihat_google_maps_dataset2.csv")

merged_df = pd.concat([df1, df2], ignore_index=True)

merged_df.to_csv("saihat_google_maps_dataset.csv", index=False)

print(f"{len(merged_df)}")