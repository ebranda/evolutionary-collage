"""
This module provides all of the functionality required to build
a drawing from a genome.

"""
import os
import math
import utils
import settings as config


### Default Settings - Don't change these here. Instead, change them in the settings.py file ###

config_layout = "GridLayout" # "GridLayout" # or "PointLayout" 
config_number_of_parts = 25 # 9, 16, 25, 36, 49, 64, 81
config_part_uniform_scale = 1.1
config_part_scale_min = 1.0 # Set min and max to 1.0 to disable scaling of parts using genome
config_part_scale_max = 1.0
config_canvas_scale = 0.90 # Scale down drawing to create margins
config_disable_rotation = False
config_snap_angles = [] #[0, 90, 180, 270] #[0, 45, 90, 135, 180, 225, 270, 315] # If left empty, angles will be selected from 0-359. 
config_rotation_jitter = 0.0 # Degrees, 0.0 to 20.0  - set to 0.0 to disable jitter
config_sort_parts_by_filename = False

# Settings specific to GridLayout
config_crop_to_cell = False # Crops any part that overflows the grid cell dimensions
config_nudge_factor_max = 0.0 # A multiple of the grid cell dimension. Set to 0 to disable nudge and keep parts in center of cells.
config_render_grid = False # Specify whether you want to preview the grid
config_number_of_columns = None

# Rendering
hi_res_width = 1200


class Part(object):
    
    def __init__(self, canvas, catalog, image_param, scale_param=None):
        self.image, self.z_order, self.filename = catalog.pick(image_param)
        imgscale = canvas.width / float(hi_res_width) # Assume that images are scaled to hi-res version
        imgscale *= config_part_uniform_scale
        if scale_param is not None:
            partscale = utils.remap(scale_param, config_part_scale_min, config_part_scale_max)
            imgscale *= partscale
        self.w = self.image.width * imgscale 
        self.h = self.image.height * imgscale
    
    def set_rotation(self, param, snap_angles, jitter):
        angles = snap_angles if snap_angles else range(359)
        i = utils.normalized_value_to_index(param, angles)
        angle = angles[i]
        angle = utils.jitter(angle, jitter)
        self.rotation = angle
    
    def set_position(self, cx, cy):
        self.cx = cx
        self.cy = cy
        self.x = self.cx - self.w / 2.0
        self.y = self.cy - self.h / 2.0
        
    def render(self, canvas):
        canvas.pushMatrix()
        canvas.translate(self.cx, self.cy)
        canvas.rotate(radians(self.rotation))
        canvas.translate(-self.cx, -self.cy)
        canvas.image(self.image, self.x, self.y, self.w, self.h)
        canvas.popMatrix()
        
        
class PointLayout(object):
    '''Create parts using a specified point on the canvas.
    '''
    def initialize(self):
        '''Initialize after module load so config variables are not bound at load time.'''
        self.params_per_part = 5
        if config_disable_rotation:
            self.params_per_part -= 1
        self.scale_disabled = config_part_scale_min == config_part_scale_max
        if self.scale_disabled:
            self.params_per_part -= 1
    
    def build_parts(self, catalog, params, canvas):
        parts = []
        for partparams in params:
            p = list(partparams) # Make a copy so we can remove items from front of list until empty
            scale = None if self.scale_disabled else p.pop(0)
            part = Part(canvas, catalog, p.pop(0), scale)
            cx = p.pop(0) * canvas.width
            cy = p.pop(0) * canvas.height
            part.set_position(cx, cy)
            rotation_angle = 0 if config_disable_rotation else p.pop(0)
            part.set_rotation(rotation_angle, config_snap_angles, config_rotation_jitter)
            parts.append(part)
        parts = sort_z(parts)
        return parts
    
    def render(self, sketch, catalog, params, canvas):
        for part in self.build_parts(catalog, params, canvas):
            part.render(canvas)
            

class GridLayout(object):
    '''Create parts using center points of grid cells.
    Assumes that the number of cells equals the number of parts.
    '''
    def initialize(self):
        '''Initialize after module load so config variables are not bound at load time.'''
        self.params_per_part = 3
        if config_disable_rotation:
            self.params_per_part -= 1
        self.scale_disabled = config_part_scale_min == config_part_scale_max
        if self.scale_disabled:
            self.params_per_part -= 1
        if config_nudge_factor_max > 0:
            self.params_per_part += 2
        
    def build_parts(self, catalog, params, canvas):
        if config_number_of_columns is None:
            rows = cols = int(math.ceil(sqrt(len(params))))
        else:
            cols = config_number_of_columns
            rows = max(1, int(math.ceil(len(params) / float(cols))))
        self.grid = utils.Grid(canvas.width, canvas.height, cols, rows)
        parts = []
        for i in range(min(len(params), len(self.grid.cells))):
            p = list(params[i]) # Make a copy so we can remove items from front of list until empty
            cell = self.grid.cells[i]
            scale = None if self.scale_disabled else p.pop(0)
            part = Part(canvas, catalog, p.pop(0), scale)
            nudge_x, nudge_y = self._get_nudge(cell, p)
            if config_crop_to_cell:
                cx, cy = cell.width / 2.0, cell.height / 2.0
            else:
                cx, cy = cell.cx, cell.cy
            part.set_position(cx + nudge_x, cy + nudge_y)
            rotation_angle = 0 if config_disable_rotation else p.pop(0)
            part.set_rotation(rotation_angle, config_snap_angles, config_rotation_jitter)
            parts.append(part)
        if not config_crop_to_cell:
            parts = sort_z(parts)
        return parts
            
    def render(self, sketch, catalog, params, canvas):
        parts = self.build_parts(catalog, params, canvas)
        if config_render_grid:
            self._render_grid(sketch)
        for i in range(min(len(parts), len(self.grid.cells))):
            cell = self.grid.cells[i]
            part = parts[i]
            if config_crop_to_cell:
                graphics = utils.GraphicsBuffer(sketch.createGraphics, cell.width, cell.height)
                graphics = sketch.createGraphics(int(cell.width), int(cell.height))
                graphics.beginDraw()
                graphics.clear()
                target = graphics
            else:
                target = canvas
            part.render(target)
            if config_crop_to_cell:
                graphics.endDraw()
                canvas.image(graphics, cell.left, cell.top)
            
    def _get_nudge(self, cell, params):
        if not config_nudge_factor_max > 0:
            return 0, 0
        nudge_max_x = cell.width * config_nudge_factor_max
        nudge_max_y = cell.height * config_nudge_factor_max
        nudge_x = params.pop(0) * nudge_max_x * 2 - nudge_max_x
        nudge_y = params.pop(0) * nudge_max_y * 2 - nudge_max_y
        return nudge_x, nudge_y
        
    def _render_grid(self, sketch):
        c1 = color(255,0,0,100)
        c2 = color(0,0,255,100)
        colors = [c1, c2, c1]
        for cell in self.grid.cells:
            color_idx = cell.col % 2 + cell.row % 2
            sketch.fill(colors[color_idx])
            sketch.rect(cell.left, cell.top, cell.width, cell.height)
            sketch.noFill()
    
    
def render(sketch, params, canvas=None):
    '''Create the drawing, using parts provided
    by the specified layout object. 
    '''
    if canvas is None: 
        canvas = sketch # If no canvas was provided then use the sketch
    canvas.background(255)
    try: 
        draw_background(params, canvas)
    except Exception: 
        pass
    canvas.noFill()
    canvas.pushMatrix()
    canvas.scale(config_canvas_scale)
    marginx = canvas.width * (1.0-config_canvas_scale) / 2.0
    marginy = canvas.height * (1.0-config_canvas_scale) / 2.0
    canvas.translate(marginx, marginy)
    partsparams = utils.partition_list(params, layout.params_per_part)
    catalog = PartsCatalog(sketch)
    layout.render(sketch, catalog, partsparams, canvas)
    canvas.popMatrix()


def initialize():
    global layout
    layout = globals()[config_layout]()
    layout.initialize()
    
layout = None



###################################################################
# Everything below this point is utility
# code for helping build the drawing
###################################################################

def num_params():
    return layout.params_per_part * config_number_of_parts


def remap_normalized(val, minval, maxval):
    return val * (maxval - minval) + minval
    

def sort_z(parts):
    return utils.sort_by_key(parts, [part.z_order for part in parts])

 
class PartsCatalog(object):
    '''Encapsulate a catalog of parts.
    '''
    # Enforce a singleton pattern
    _instance = None
    def __new__(cls, sketch):
        if cls._instance is None:
            inst = super(PartsCatalog, cls).__new__(cls)
            inst.parts = []
            inst.folder_name = "parts"
            folderpath = utils.app_data_path(sketch, inst.folder_name)
            inst.folder_path = folderpath
            inst.filenames = utils.listfiles(folderpath, fullpath=False)
            for filepath in utils.listfiles(folderpath, fullpath=True):
                img = sketch.loadImage(filepath)
                if img is not None:
                    inst.parts.append(img)
            inst.sort(sketch)
            cls._instance = inst
        return cls._instance
    
    def sort(self, sketch):
        if config_sort_parts_by_filename:
            self.parts = utils.sort_by_key(self.parts, self.filenames)
            self.filenames = utils.sort_by_key(self.filenames, self.filenames)
        else:
            sizes = []
            for img in self.parts:
                sizes.append(len([1 for p in img.pixels if sketch.alpha(p) > 0]))
            self.parts = utils.sort_by_key(self.parts, sizes, reverse=True)
            self.filenames = utils.sort_by_key(self.filenames, sizes, reverse=True)
                
    def pick(self, idx_normalized):
        if not self.parts:
            raise RuntimeError("{} module: No parts in catalog. Did you put images in the {} folder?".format(__name__, self.folder_path))
        i = utils.normalized_value_to_index(idx_normalized, self.parts)
        #print idx_normalized, i
        return self.parts[i], i, self.filenames[i]


# Try loading the optional background.py module in case the
# project wants to draw anything on the canvas before the 
# drawing render.
try: 
    import background
    if hasattr(background, "draw"):
        global draw_background
        draw_background = background.draw
except: 
    pass # Do nothing



    
    
    
    
    
    
