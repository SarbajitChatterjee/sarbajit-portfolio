import pandas as pd

#Read the CSV and have the encodings to accept the german umlauts
df = pd.read_csv("Raw Data.csv", encoding="ISO-8859-1")#, header=1)
df_backup =  df

print(df.head(3))

#to show a preview
#print(df.head(3))

#Replace column headers with the values from the first data row (thereby removing the "unnamed" columns)
df.columns = df.iloc[0] #--> Displays only the filled values in that row
#dropping the first row once we have remobed the unnamed columns and replaced it with the new headers
df = df.drop(df.index[0])

df = df.reset_index(drop=True)



# Strip leading/trailing whitespace (optional but safe)
df.columns = df.columns.str.strip()

#Renaming the first two columns for clarity.
df = df.rename(columns={
    df.columns[0]: "Region",
    df.columns[1]: "State"
})

print(df.head(3))

# Keep only columns that contain 'gesamt' in their name (case-insensitive),
# plus the first two columns: Region and State
#df_clean = df.loc[:, df.columns.str.contains("gesamt|Region|State", case=False)]

#print ("\nCleaned version:\n",print(df_clean.columns[:10],df_clean.head(2)))
