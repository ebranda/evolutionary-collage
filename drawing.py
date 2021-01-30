"""
This module provides all of the functionality required to build
a drawing from a genome.

"""
import os
import math
import utils


### Settings ###

# Layout
config_layout = "GridLayout" # "GridLayout" # or "PointLayout" # TODO test PointLayout
config_number_of_shapes = 25 # 9, 16, 25, 36, 49

# Scaling
config_shape_uniform_scale = 0.605 - 0.2
config_canvas_scale = 0.90 # Scale down drawing to create margins

# Rotation
config_disable_rotation = False
config_snap_angles = [0, 90, 180, 270] #[0, 45, 90, 135, 180, 225, 270, 315] # If left empty, angles will be selected from 0-359. 
config_rotation_jitter = 10.0 # Degrees - set to 0 to disable

# Grid layout
config_crop_to_cell = True
config_nudge_max_factor = 0.3 # A multiple of the grid cell dimension. Set to 0 to disable nudge and keep parts in center of cells.
render_grid = False

# Rendering
hi_res_width = 1200


class PointLayout(object):
    '''Create shapes using a specified point on the canvas.
    '''
    params_per_shape = 4
    if config_disable_rotation:
        params_per_shape -= 1
        
    def render(self, sketch, params, canvas):
        shapesparams = utils.partition_list(params, self.params_per_shape)
        for params in shapesparams:
            params = list(params) # Make a copy so we can remove items from front of list until empty
            image = PartsCatalog(sketch).pick(params.pop(0))
            cx = params.pop(0) * canvas.width
            cy = params.pop(0) * canvas.height
            rotation = 0 if config_disable_rotation else get_angle(params.pop(0))
            shape_w, shape_h = get_shape_size(image, canvas)
            canvas.pushMatrix()
            canvas.translate(cx, cy)
            canvas.rotate(radians(rotation))
            canvas.translate(-cx, -cy)
            x = cx - shape_w / 2.0
            y = cy - shape_h / 2.0
            canvas.image(image, x, y, shape_w, shape_h)
            canvas.popMatrix()


class GridLayout(object):
    '''Create shapes using center points of grid cells.
    Assumes that the number of cells equals the number of shapes.
    '''
    params_per_shape = 2
    if config_disable_rotation:
        params_per_shape -= 1
    if config_nudge_max_factor > 0:
        params_per_shape += 2
    
    def render(self, sketch, params, canvas):
        shapesparams = utils.partition_list(params, self.params_per_shape)
        rows = cols = int(round(sqrt(len(shapesparams))))
        grid = utils.Grid(canvas.width, canvas.height, cols, rows)
        if render_grid:
            self._render_grid(sketch, grid)
        for i in range(min(len(shapesparams), len(grid.cells))):
            params = list(shapesparams[i]) # Make a copy so we can remove items from front of list until empty
            cell = grid.cells[i]
            image = PartsCatalog(sketch).pick(params.pop(0))
            rotation = 0 if config_disable_rotation else get_angle(params.pop(0))
            nudge_x, nudge_y = self._get_nudge(cell, params)
            shape_w, shape_h = get_shape_size(image, canvas)
            if config_crop_to_cell:
                graphics = utils.GraphicsBuffer(sketch.createGraphics, cell.width, cell.height)
                graphics.beginDraw()
                graphics.clear()
                target = graphics
                cx = cell.width / 2.0
                cy = cell.height / 2.0
            else:
                target = canvas
                cx = cell.cx
                cy = cell.cy
            target.pushMatrix()
            target.translate(cx, cy)
            target.rotate(radians(rotation))
            target.translate(-cx, -cy)
            x = cx - shape_w / 2.0 + nudge_x
            y = cy - shape_h / 2.0 + nudge_y
            target.image(image, x, y, shape_w, shape_h)
            target.popMatrix()
            if config_crop_to_cell:
                graphics.endDraw()
                canvas.image(graphics, cell.left, cell.top)
        
    def _get_nudge(self, cell, params):
        if not params:
            return 0, 0
        nudge_max_x = cell.width * config_nudge_max_factor
        nudge_max_y = cell.height * config_nudge_max_factor
        nudge_x = params.pop(0) * nudge_max_x * 2 - nudge_max_x
        nudge_y = params.pop(0) * nudge_max_y * 2 - nudge_max_y
        return nudge_x, nudge_y
        
    def _render_grid(self, sketch, grid):
        for i in range(len(grid.cells)):
            cell = grid.cells[i]
            sketch.fill(color(255,0,0,100) if i % 2 else color(0,0,255,100))
            sketch.rect(cell.left, cell.top, cell.width, cell.height)
            sketch.noFill()
    
    
def render(sketch, params, canvas=None):
    '''Create the drawing, using shapes provided
    by the specified layout object. 
    '''
    if canvas is None: 
        canvas = sketch # If no canvas was provided then use the sketch
    canvas.background(255)
    noFill()
    canvas.pushMatrix()
    canvas.scale(config_canvas_scale)
    marginx = canvas.width * (1.0-config_canvas_scale) / 2.0
    marginy = canvas.height * (1.0-config_canvas_scale) / 2.0
    canvas.translate(marginx, marginy)
    layout.render(sketch, params, canvas)
    canvas.popMatrix()


layout = globals()[config_layout]()




###################################################################
# Everything below this point is utility
# code for helping build the drawing
###################################################################

def num_params():
    return layout.params_per_shape * config_number_of_shapes

def get_angle(i_normalized):
    angles = config_snap_angles if config_snap_angles else range(359)
    i = utils.normalized_value_to_index(i_normalized, angles)
    angle = angles[i]
    if "config_rotation_jitter" in globals():
        angle = utils.jitter(angle, config_rotation_jitter)
    return angle

def get_shape_size(image, canvas):
    imgscale = canvas.width / float(hi_res_width) # Assume that images are scaled to hi-res version
    imgscale *= config_shape_uniform_scale
    shape_w = image.width * imgscale 
    shape_h = image.height * imgscale
    return shape_w, shape_h

def remap_normalized(val, minval, maxval):
    return val * (maxval - minval) + minval

 
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
            folderpath = sketch.dataPath(inst.folder_name)
            for filepath in utils.listfiles(folderpath, fullpath=True):
                img = sketch.loadImage(filepath)
                if img is not None:
                    inst.parts.append(img)
            cls._instance = inst
        return cls._instance
                
    def pick(self, idx_normalized):
        if not self.parts:
            raise RuntimeError("{} module: No parts in catalog. Did you put images in the {} folder?".format(__name__, self.folder_name))
        i = utils.normalized_value_to_index(idx_normalized, self.parts)
        #print idx_normalized, i
        return self.parts[i]
    
    



    
    
    
    
    
    
