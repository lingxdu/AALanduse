import arcpy
import pandas as pd
import numpy as np

# Set the workspace to the folder where the shapefile is stored
arcpy.env.workspace = r"D:\ArcGIS\Projects\finalproject"

# Specify the land use shapefile
shapefile = r"D:\ArcGIS\Projects\finalproject\AA_LandUse\AA_LandUse.shp"

# Create a list of unique land use types in the shapefile
land_use_types = []
with arcpy.da.SearchCursor(shapefile, ["LANDUSE"]) as cursor:
    for row in cursor:
        if row[0] not in land_use_types:
            land_use_types.append(row[0])

# Create a dictionary to store the area of each land use type
land_use_areas = {type: 0 for type in land_use_types}

# Calculate the area of each land use type
with arcpy.da.SearchCursor(shapefile, ["LANDUSE", "SHAPE@AREA"]) as cursor:
    for row in cursor:
        land_use_areas[row[0]] += row[1]

# Create a pandas DataFrame from the dictionary
df = pd.DataFrame(land_use_areas.items(), columns=["Land Use Type", "Area"])

# Calculate the total area of the region
total_area = df["Area"].sum()

# Calculate the percentage of each land use type
df["Percentage"] = df["Area"] / total_area * 100

# Round the percentage to two decimal places and convert it to float
df["Percentage"] = np.round(df["Percentage"], 2)

# Add a new field to the attribute table to store the percentage
arcpy.AddField_management(shapefile, "PERCENTAGE", "FLOAT")

# Update the attribute table with the calculated percentage
with arcpy.da.UpdateCursor(shapefile, ["LANDUSE", "PERCENTAGE"]) as cursor:
    for row in cursor:
        row[1] = df[df["Land Use Type"] == row[0]]["Percentage"].values[0]
        cursor.updateRow(row)


# Sort the results in descending order of percentage
df.sort_values("Percentage", ascending=False, inplace=True)

# Save the results to a CSV file
df.to_csv("land_use_percentage.csv", index=False)
