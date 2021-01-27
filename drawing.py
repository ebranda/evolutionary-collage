"""
This module provides all of the functionality required to build
a drawing from a genome.

"""
import os
import math
import utils


# Settings

config_layout = "GridLayout" # "GridLayout" # or "PointLayout"
config_number_of_shapes = 9 # 9, 16, 25, 36, 49

# Scaling and rotation
config_shape_uniform_scale = 2.0
config_canvas_scale = 0.90 # Scale down drawing to create margins
config_snap_angles = [0, 90, 180, 270] #[0, 45, 90, 135, 180, 225, 270, 315] # If left empty, angles will be selected from 0-359. 
config_rotation_jitter = 10.0 # Degrees

# Rendering
hi_res_width = 1200



class PointLayout(object):
    '''Create shapes using a specified point on the canvas.
    '''
    params_per_shape = 4
        
    def shapes(self, catalog, params, canvas):
        shapes = []
        for p in utils.partition_list(params, self.params_per_shape):
            image = catalog.pick(p[0])
            x = p[1] * canvas.width
            y = p[2] * canvas.height
            rotation = get_angle(p[3])
            scale = get_uniform_scale_factor(canvas)
            s = Shape(image, x, y, rotation, scale)
            shapes.append(s)
        return shapes


class GridLayout(object):
    '''Create shapes using center points of grid cells.
    Assumes that the number of cells equals the number of shapes.
    '''
    params_per_shape = 2
    
    def shapes(self, catalog, params, canvas):
        shapes = []
        for p in utils.partition_list(params, self.params_per_shape):
            image = catalog.pick(p[0])
            rotation = get_angle(p[1])
            scale = get_uniform_scale_factor(canvas)
            s = Shape(image, 0, 0, rotation, scale)
            shapes.append(s)
        rows = cols = int(round(sqrt(len(shapes))))
        grid = utils.Grid(canvas.width, canvas.height, cols, rows)
        for i in range(min(len(shapes), len(grid.cells))):
            shapes[i].move_to(grid.cells[i].center)
        return shapes


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
    catalog = PartsCatalog(sketch)
    for s in layout.shapes(catalog, params, canvas):
        canvas.pushMatrix()
        canvas.translate(s.center.x, s.center.y)
        canvas.rotate(radians(s.rotation))
        canvas.translate(-s.center.x, -s.center.y)
        canvas.image(s.image, s.left, s.top, s.width, s.height)
        canvas.popMatrix()
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

def get_uniform_scale_factor(canvas):
    scale = canvas.width / float(hi_res_width) # Assume that images are scaled to hi-res version
    scale *= config_shape_uniform_scale
    return scale

def remap_normalized(val, minval, maxval):
    return val * (maxval - minval) + minval
    
def build_shapes_OBS(sketch, chromosome, canvas):
    '''Helper function to retrieve the layout function by name
    and invoke the function to obtain a list of shapes.'''
    layout_func = globals()[config_layout]
    return layout_func(sketch, chromosome, canvas)

 
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
    
    
class Shape(object):
    '''Encapsulate the functionality for one of the shapes
    that make up the drawing.
    '''
    def __init__(self, image, cx, cy, rotation=0.0, scale=1.0):
        self.image = image
        self.width = image.width * scale
        self.height = image.height * scale
        self.rotation = rotation
        self.center = utils.Point(cx, cy)
        
    def move_to(self, targetpt):
        self.center.move_to(targetpt)
        
    def scale_to(self, sketch, canvas):
        factor = canvas.width / float(sketch.width)
        self.scale(factor)
        
    def scale(self, factor):
        self.width *= factor
        self.height *= factor
    
    @property
    def left(self):
        return self.center.x - self.width/2
    
    @property 
    def top(self):
        return self.center.y - self.height/2


    
    
    
    
    
    
