"""
This module provides all of the functionality required to build
a drawing from a genome.

"""
import os
import math
import utils


# Default settings
layout = "build_shapes_point"
genes_per_shape = 4
number_of_shapes = 25
shape_uniform_scale = 0.9
shape_min_scale = 0.8
shape_max_scale = 1.2
parts_folder_name = "parts"
hi_res_width = 1200


def render(sketch, chromosome, canvas=None):
    '''Draw a set of shapes to a given graphics canvas.
    This is the main rendering function. It uses the 
    function specified in the layout_function_name attribute
    for building the actual shapes from a given chromosome.
    '''
    if canvas is None: 
        canvas = sketch # If no canvas was provided then use the sketch
    shapes = build_shapes(sketch, chromosome, canvas)
    canvas.background(255)
    noFill()
    for s in shapes:
        canvas.pushMatrix()
        canvas.translate(s.center.x, s.center.y)
        canvas.rotate(radians(s.rotation))
        canvas.translate(-s.center.x, -s.center.y)
        canvas.image(s.image, s.left, s.top, s.width, s.height)
        canvas.popMatrix()
        
        
def build_shapes_point(sketch, chromosome, canvas):
    '''Create shapes using a specified point on the canvas.
    gene[0] is image part number
    gene[1],gene[2] are x,y position
    gene[3] is rotation
    gene[4] is scale (optional)
    '''
    catalog = PartsCatalog(sketch, parts_folder_name)
    shapes_genes = utils.partition_list(chromosome, genes_per_shape)
    shapes = []
    for genes in shapes_genes:
        image = catalog.pick(genes[0])
        x = genes[1] * canvas.width
        y = genes[2] * canvas.height
        rotation = genes[3] * 360
        scale = get_uniform_scale_factor(canvas)
        if len(genes) > 4:
            scale *= genes[4] * (shape_max_scale - shape_min_scale) + shape_min_scale
        s = Shape(image, x, y, rotation, scale)
        shapes.append(s)
    return shapes


def build_shapes_grid(sketch, chromosome, canvas):
    '''Create shapes using center points of grid cells.
    Assumes that the number of cells equals the number of shapes.
    gene[0] is image part number
    gene[1] is rotation
    gene[2] is scale (optional)
    '''
    rows = 5
    cols = 5
    grid = utils.Grid(canvas.width, canvas.height, cols, rows)
    catalog = PartsCatalog(sketch, parts_folder_name)
    shapes_genes = utils.partition_list(chromosome, genes_per_shape)
    shapes = []
    for genes in shapes_genes:
        image = catalog.pick(genes[0])
        angles = [0, 90, 180, 270]
        rotation = angles[utils.normalized_value_to_index(genes[1], angles)]
        rotation = utils.jitter(rotation, 10.0)
        scale = get_uniform_scale_factor(canvas)
        if len(genes) > 2:
            scale *= genes[2] * (shape_max_scale - shape_min_scale) + shape_min_scale
        s = Shape(image, 0, 0, rotation, scale)
        shapes.append(s)
    for i in range(min(len(shapes), len(grid.cells))):
        shapes[i].move_to(grid.cells[i].center)
    return shapes




###################################################################
# Everything below this point is utility
# code for helping build the drawing
###################################################################


def get_uniform_scale_factor(canvas):
    scale = canvas.width / float(hi_res_width) # Assume that images are scaled to hi-res version
    scale *= shape_uniform_scale
    return scale
        
    
def build_shapes(sketch, chromosome, canvas):
    '''Helper function to retrieve the layout function by name
    and invoke the function to obtain a list of shapes.'''
    layout_func = globals()[layout]
    return layout_func(sketch, chromosome, canvas)

 
class PartsCatalog(object):
    '''Encapsulate a catalog of parts.
    '''
    # Enforce a singleton pattern
    _instance = None
    def __new__(cls, sketch, parts_folder_name):
        if cls._instance is None:
            inst = super(PartsCatalog, cls).__new__(cls)
            inst.parts = []
            folderpath = sketch.dataPath(parts_folder_name)
            for filepath in utils.listfiles(folderpath, fullpath=True):
                img = sketch.loadImage(filepath)
                if img is not None:
                    inst.parts.append(img)
            cls._instance = inst
        return cls._instance
                
    def pick(self, idx_normalized):
        if not self.parts:
            raise RuntimeError("{} module: No parts in catalog. Did you put images in the {} folder?".format(__name__, parts_folder_name))
        i = utils.normalized_value_to_index(idx_normalized, self.parts)
        #print idx_normalized, i
        return self.parts[i]
    
    
class Shape(object):
    '''Encapsulate the functionality for one of the shapes
    that make up the drawing.
    '''
    def __init__(self, image, cx, cy, rotation, scale):
        self.image = image
        self.width = image.width * scale
        self.height = image.height * scale
        self.rotation = rotation
        self.center = utils.Point(cx, cy)
        
    def move_to(self, targetpt):
        self.center.move_to(targetpt)
        
    def scale_to(self, sketch, canvas):
        factor = canvas.width / float(sketch.width)
        self.width *= factor
        self.height *= factor
    
    @property
    def left(self):
        return self.center.x - self.width/2
    
    @property 
    def top(self):
        return self.center.y - self.height/2


    
    
    
    
    
    
