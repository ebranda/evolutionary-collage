class Settings(object):
    def attribute_names(self):
        return self.__dict__.keys()
app = Settings()
drawing = Settings()
ga = Settings()
ic = Settings()

app.version = "0.41"

#### DON'T CHANGE ANYTHING ABOVE THIS LINE ####


# All of these are required
app.testmode = False
app.autosave_fittest_only = True
app.data_folder_name = None

# Now optionally override any module settings you wish to customize.
drawing.config_layout = "GridLayout" 
drawing.config_number_of_parts = 25
drawing.config_part_uniform_scale = 0.9
drawing.config_canvas_scale = 0.85
drawing.config_disable_rotation = False
drawing.config_snap_angles = []
drawing.config_rotation_jitter = 0.0
drawing.config_crop_to_cell = False
drawing.config_nudge_factor_max = 0.0
ic.config_strictness = 4
ic.config_preprocess_mode = "gray"


'''
GUIDE TO SETTINGS

The module settins above are a useful starting point, but you can 
delete or comment out any lines you don't need. 
Refer to the respective module files to see the default values.
Refer to the module files for parameters not included below,
but you probably won't need to touch those. Remember, you can
always visit the GitHub repository to retrieve the original
version of this file if you make changes that break anything. 
https://github.com/ebranda/evolutionary-collage/blob/main/settings.py

app.testmode
Set to False to explore the solution space and True to run the solver

app.autosave_fittest_only
Set to True to save a high-res image of only the fittest scheme (generally, leave it at True)

app.data_folder_name
Optional. Set to the name of a folder in [sketch]/data to organize your sketch into subprojects

drawing.config_layout
Specifies the layout to use ("GridLayout" or "PointLayout")

drawing.config_number_of_parts
For grid layout, use 9, 16, 25, 36, 49, 64, 81 (i.e. squares of integers)

drawing.config_part_uniform_scale
Scale the parts before they are placed on the canvas.

drawing.config_canvas_scale
Scale down the entire drawing to create margins

drawing.config_disable_rotation
Set to True to disable rotation or set to False to enable rotation

drawing.config_snap_angles
Set to [], or [0, 90, 180, 270] or any other set of angles. If left empty, angles will be selected from 0-359. 

drawing.config_rotation_jitter
Degrees of random rotation for each part after it is placed. Set to 0 to disable jitter rotation.

drawing.config_crop_to_cell
Set to True to crop parts to grid cells or False to allow parts to overflow grid cell boundaries

drawing.config_nudge_factor_max
A multiple of the grid cell dimension. Set to 0 to disable nudge and keep parts in center of cells.

ic.config_strictness
1-5, with 5 being the most accurate representation of the comparator image. Use only the highest value you need.

ic.config_preprocess_mode
"gray" for grayscale comparators, "binary" for pure black and white, or "color" for color comparators.

'''


