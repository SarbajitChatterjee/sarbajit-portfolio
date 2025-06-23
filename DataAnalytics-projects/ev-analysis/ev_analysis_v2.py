import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

import geopandas as gpd

def qa_Check_NaNcells(df) :
    #QA on Data cleaning
    df_toCheck = df.isna().any().any()
    if df_toCheck :
        print("✅ Number of NaN: ", df.isna().sum())
        print("✅ Columns that has NaN: ", df.isna().sum()[df.isna().sum() > 0])

        return True
    else:
        return False
    

def plot_state_trends(df_long):
    # Plots EV registrations over time, one line per German state.
    
    # Parameters:
    # df_long (pd.DataFrame): Long‐format DataFrame with columns
    #     ['Region', 'State', 'Date', 'Stations']
    
    # Setting a clean, grid‐based style for readability
    sns.set(style="whitegrid")
    # Define the canvas size (in inches)
    fig, ax = plt.subplots(figsize=(12, 6))

    #    Reserve right 25% of figure for legend
    #    left=0.0, right=1.0 spans entire width.
    #    By moving right down to 0.75, axes fill 75% width.
    fig.subplots_adjust(left=0.05, right=0.75, top=0.90, bottom=0.15)

    # # Reserve margins exactly as shown by the sliders
    # fig.subplots_adjust(
    #     left=0.075,    # slider “left” = 0.075
    #     bottom=0.17,   # slider “bottom” = 0.17
    #     right=0.967,   # slider “right” = 0.967
    #     top=0.566,     # slider “top” = 0.566
    #     wspace=0.19,   # slider “wspace” = 0.19
    #     hspace=0.27    # slider “hspace” = 0.27
    # ) 

    # Draw the line plot
    sns.lineplot(
        data = df_long,
        x= "Date",
        y= "Stations",
        hue= "State", #separate colour for each line in different state
        estimator= "sum",
        ax=ax,
        linewidth=2,
        errorbar=None #turns off the shading around lines.
    )

    # Titles and Names
    # plt.title("Trends of Charging Stations by State (DE)", fontsize=16)
    # plt.xlabel("per Quarter by Year", fontsize=14)
    # plt.ylabel("Charging Stations", fontsize=14)

    ax.set_title("Trends of Charging Stations by State (DE)", fontsize=16, pad=15)
    ax.set_xlabel("per Quarter by Year", fontsize=14, labelpad=10)
    ax.set_ylabel("Charging Stations", fontsize=14, labelpad=10)

    # Legends
    ax.legend(
        title= "State",
        bbox_to_anchor = (1.02,2), #Just ooutside the axes
        loc = "upper right",
        ncol=1,
        frameon=True,
        borderaxespad = 0
    )

    #Render and display
    plt.tight_layout()
    plt.show()

def plot_country_heatmap(df_long, year, geojson_path, cmap="RdYlBu_r"):
    """
    Draws a choropleth map of Germany’s states, colored by total charging stations in `year`.

    Parameters:
    -----------
    df_long : pd.DataFrame
        Long-format DataFrame with columns ['Region','State','Date','Stations'].
    year : int
        The year to map (e.g., 2017 or 2025).
    geojson_path : str
        Path to a Germany-states GeoJSON file.
    cmap : str, optional
        A matplotlib colormap (red=high, blue=low). Defaults to "RdYlBu_r".
    """
    
    gdf = gpd.read_file(geojson_path)

    #Sum station counts per state for the specified year
    df_year=(
        df_long[df_long["Date"].dt.year == year]
        .groupby("State")["Stations"]
        .sum()
        .reset_index()
    )


# Step 1: Load CSV without headers at all
df_raw = pd.read_csv("Raw Data.csv", encoding="ISO-8859-1", header=None)

print(df_raw.head(3))

# STEP 2: Capture first two rows separately
row_main = df_raw.iloc[0]  # Kreise, Bundesland, date...
row_sub = df_raw.iloc[1]   # NaN, NaN, NLP, SLP, gesamt...

# Forward fill missing dates in row_main (in-place!)
row_main = row_main.ffill()

# Step 3: Create new merged headers
final_columns=[]

for i in range(len(row_main)):
    if i == 0:
        final_columns.append("Region")
    elif i == 1:
        final_columns.append("State")
    elif str(row_sub[i]).strip().lower() == "gesamt":
        merged = f"{str(row_main[i]).strip()}_gesamt"
        final_columns.append(merged)
    else:
        final_columns.append(None)  # Make the NLP/SLP or anything else column name as 'None', which will be dropped later

# Step 4: Drop the header rows from data
df_data = df_raw.drop(index=[0, 1]).reset_index(drop=True)

#Set new columns
df_data.columns = final_columns

#Step 5: Drop all the columns which has Nan or None. 
#So basically notna() identifies only columns wih meaningful name and are then copied into the main data frame leaving the actual None Nan columns into abyss
df_data = df_data.loc[:,df_data.columns.notna()]

#print(df_data.head(3))

#Fixing cells which has Nan to 0
ev_cols = df_data.columns[2:]
df_data[ev_cols] = df_data[ev_cols].fillna(0)


#Select all columns from index 2 onward (excluding Region and State)
col_to_convert = df_data.columns[2:]

#Step 6: Convert the columns now to numeric
for col in col_to_convert:
    df_data[col] = pd.to_numeric(df_data[col], errors='coerce')

#Confirm Data check
print("✅ Final Columns (after conversion):")
print(df_data.columns[:10])

print("✅ Data Preview:")
print(df_data.head(2))

# Optional: check data types
print("✅ Column Data Types:")
print(df_data.dtypes[:])

#Step 7: Transition Data from Long to Wide format (Transpose it for betting graph plotting)
df_long = pd.melt(
    df_data,
    id_vars=["Region","State"],
    var_name="Date", #Original column names will go here
    value_name="Stations" #basically chooses which value will go here with the var_name declared above

)

#To change the date from 01-01-207_gesamt to 01-01-2017.
df_long["Date"] = df_long["Date"].str.replace("_gesamt", "", regex=False)

#Now converting that same column to dateTime format
df_long["Date"] = pd.to_datetime(df_long["Date"], dayfirst=True, errors="coerce")
#Final check to also have the new EV column in numeric or Int64
df_long["Stations"] = pd.to_numeric(df_long["Stations"], errors="coerce")

print(df_long.tail(3))
print(df_long.dtypes)

df_long.to_csv("cleaned_EV_charging_stations_germany.csv",index=False, encoding="ISO-8859-1")

#Now that the data is cleaned, help in plotting the data using a function that you can define it.
#Should be trend graph, heatmap(with a scrollbar based on the year or dropdown box), geographical map with 2017 and 2025
#Can find a new data that captures the per capita of people using Stations and then finding the proportion of EV chargers 50 kms. Point zero will be a city in  region and then go farther into rural region. --. For each representation they should be ran through a method.


# Plots EV registrations over time, one line per German state.
plot_state_trends(df_long)