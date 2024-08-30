# +-------------------------------------------------------------------------------------------------
# Author:cfolkers
# Ministry, Division, Branch: WLRS, GeoBC, GSS
# Created Date: 20240718
# Updated Date: 
# Description: tool to take the provincial grid, create a def query based on distance from fire perimeter, add provincial grid to mxd and apply def query
# +-------------------------------------------------------------------------------------------------

#variables and set up
# +-------------------------------------------------------------------------------------------------
import arcpy 
import os
from datetime import datetime
arcpy.env.overwriteoutput=True
fire_number = arcpy.GetParameterAsText(0)
map_lyr =  arcpy.GetParameterAsText(5) # reaplces lines ~81
grid=arcpy.GetParameterAsText(1)
x_col = arcpy.GetParameterAsText(2)  # set to drop down menu of fields if possible?
y_col = arcpy.GetParameterAsText(3)  # set to drop down menu of fields if possible?
distance_from_fire = arcpy.GetParameterAsText(4)  # meters

#static var 
base_url = r'FireSeasonWork' #must be changed in order to work on GTS
#get current year
current_year = str(datetime.now().year)
#get fire zone
fire_prefix = fire_number[:2]

#determine fire center for path
fc = fire_number[:1].upper()
if fc == 'C':
    fc = 'Cariboo'
elif fc == 'V':
    fc = 'Coastal'
elif fc == 'K':
    fc = 'Kamloops'
elif fc == 'R':
    fc = 'NorthWest'
elif fc == 'G':
    fc = 'PrinceGeorge'
elif fc == 'N':
    fc = 'SouthEast'
#create path to fire poly from fire number
fire_poly_path = os.path.join(base_url, current_year, fc, fire_prefix, fire_number, 'Data', "{}.gdb".format(fire_number), "FirePolygon")
fire_gdb_path = os.path.join(base_url, current_year, fc, fire_prefix, fire_number, 'Data', "{}.gdb".format(fire_number))
# Functions
# +-------------------------------------------------------------------------------------------------

#function to get unique values from table for grid cell refs
def unique_values(table, field):
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted(set(row[0] for row in cursor))

#function to fomart def query for grid cells
def write_query(grid_layer, fire_poly, distance, xcol, ycol):
    #would not work in py2 without make feature layer
    arcpy.MakeFeatureLayer_management(grid_layer, "grid_lyr")
    grid_sel = arcpy.management.SelectLayerByLocation(in_layer="grid_lyr", overlap_type='WITHIN_A_DISTANCE', select_features=fire_poly, search_distance=distance)
    unique_x = unique_values(grid_sel, xcol)
    unique_x = [str(x) for x in unique_x]
    unique_y = unique_values(grid_sel, ycol)
    unique_y = [str(y) for y in unique_y] 

    q = "{} IN {} AND {} IN {}".format(x_col, unique_x, y_col, unique_y)

    q = q.replace('[', '(')
    q = q.replace(']', ')')
    q=str(q)
    arcpy.management.Delete("grid_lyr")
    return q

# Run it 
# +-------------------------------------------------------------------------------------------------
#py2 sooo slowww
#make def query for grids
if arcpy.Exists(grid):
    grid_def_query = write_query(grid, fire_poly_path, distance_from_fire, x_col, y_col)
else:
    arcpy.AddMessage('layer does not exist')
    exit()

#get mxd up and rippin
mxd = arcpy.mapping.MapDocument("CURRENT")
#get lyr from mxd
if map_lyr =='': 
    lyr =  arcpy.mapping.ListLayers(mxd, '*FireGridPolygon*')[0]
# Replace the data source
else: 
    lyr=(arcpy.mapping.Layer(map_lyr))

# arcpy.AddMessage(lyr.name())

grid_dir=os.path.dirname(grid)
grid_base=os.path.basename(grid)

# arcpy.env.overwriteoutput=True
# arcpy.env.workspace = fire_gdb_path

lyr.replaceDataSource(grid_dir,'FILEGDB_WORKSPACE', grid_base, True)
#change def query
lyr.definitionQuery = grid_def_query
mxd.save()
