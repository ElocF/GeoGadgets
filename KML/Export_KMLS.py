import arcpy
import os
import re

# Define the workspace and feature class
workspace = r"Path/to/GDB"
#featureclass in gdb
feature_class = "South_East_Mountain_Pass_Road_Rehab"
#unique col used for nameing and to get unique features
name_col= "your unique name column"
#output location for kmls
output_folder = r"Path/to/Output/Folder"

# Define a regular expression pattern for invalid characters (e.g., any character that's not a word character or space)
invalid_chars_pattern = r'[^\w\s]'

arcpy.env.workspace = workspace

# Create a search cursor to iterate through each polygon in the feature class
with arcpy.da.SearchCursor(feature_class, ["OID@", "SHAPE@", name_col]) as cursor:
    for row in cursor:
        oid = row[0]
        polygon = row[1]
        out_name= row[2]

        # Replace any invalid characters with a space
        out_name_cleaned = re.sub(invalid_chars_pattern, ' ', out_name)
        # Define the output KML file path
        kml_output = os.path.join(output_folder, f"{out_name_cleaned}.kml")
        
        if os.path.exists(kml_output):
            print(f"File {kml_output} already exists, skipping...")
            continue  # Skip to the next polygon

        
        # Create a feature layer for the current polygon
        where_clause = f"OBJECTID = {oid}"
        layer_name = out_name
        
        
        arcpy.MakeFeatureLayer_management(feature_class, layer_name, where_clause)

        # Define the output KML file path
        kml_output = os.path.join(output_folder, f"{out_name_cleaned}.kml")

        # Export the feature layer to KML
        arcpy.LayerToKML_conversion(layer_name, kml_output)

        # Delete the feature layer to free up memory
        arcpy.Delete_management(layer_name)

print("Export completed.")