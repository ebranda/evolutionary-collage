class Settings(object):
    def attribute_names(self):
        return self.__dict__.keys()
app = Settings()
drawing = Settings()
ga = Settings()
ic = Settings()
#### DON'T CHANGE ANYTHING ABOVE THIS LINE. ####


### Settings ###

# App
app.testmode = False # Set this to True to explore the solution space or False to run the solver.
app.autosave_fittest_only = True # Set to True to save only the fittest image per run, or False to save one image for each fitness improvement
app.data_folder_name = None # Optional. Set to the name of a folder in [sketch]/data to organize your sketch into subprojects

# Drawing layout
drawing.config_layout = "GridLayout" # "GridLayout" # or "PointLayout" 
drawing.config_number_of_parts = 49 # For grid, use 9, 16, 25, 36, 49, 64, 81

# Drawing scaling
drawing.config_part_uniform_scale = 0.9
drawing.config_canvas_scale = 0.85 # Scale down drawing to create margins

# Rotation
drawing.config_disable_rotation = False
drawing.config_snap_angles = [] #[0, 90, 180, 270] #[0, 45, 90, 135, 180, 225, 270, 315] # If left empty, angles will be selected from 0-359. 
drawing.config_rotation_jitter = 0.0 # Degrees - set to 0 to disable

# Settings specific to GridLayout
drawing.config_crop_to_cell = False # Crops any part that overflows the grid cell dimensions
drawing.config_nudge_factor_max = 0.0 # A multiple of the grid cell dimension. Set to 0 to disable nudge and keep parts in center of cells.

