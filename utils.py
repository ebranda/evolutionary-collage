"""
This module provides various utility functions.
"""

# Generic Python imports
import pickle
import os
import math
import time
import random
    
    
def save_low_res(sketch, ga):
    '''Save a snapshot of the current canvas.'''
    runs = RunManager(sketch)
    create_folder(runs.run_dir_path)
    filename = "generation-{0:04d}.png".format(ga.generation_number())
    filepath = os.path.join(runs.run_dir_path, filename)
    image = sketch.get()
    image.save(filepath)


def save_hi_res(sketch, ga, drawing, createGraphics):
    '''Render and save a hi-res version of the fittest solution.'''
    runs = RunManager(sketch)
    create_folder(runs.run_dir_path)
    w = drawing.hi_res_width
    h = sketch.height * drawing.hi_res_width / sketch.width
    canvas = GraphicsBuffer(createGraphics, w, h)
    canvas.beginDraw()
    drawing.render(sketch, ga.fittest().genes, canvas)
    canvas.endDraw()
    filename = "generation-{0:04d}-hi-res.png".format(ga.generation_number())
    filepath = os.path.join(runs.run_dir_path, filename)
    canvas.save(filepath)
    print("Saved hi-res image of fittest in generation {}".format(ga.generation_number()))
    

def create_report(sketch, drawing, ga, ic):
    def underline(lines):
        #lines.append("".join(["-"] * len(lines[-1]) * 2))
        lines.append("".join(["-"] * 45))
    runs = RunManager(sketch)
    create_folder(runs.run_dir_path)
    lines = []
    def add_config(obj, lines):
        for attr in dir(obj):
            if not attr.startswith("config_"): continue
            lines.append("{} = {}".format(attr, getattr(obj, attr)))
    lines.append("Module settings: drawing")
    underline(lines)
    add_config(drawing, lines)
    lines.append("\n\nModule settings: genetic")
    underline(lines)
    add_config(ga, lines)
    lines.append("\n\nModule settings: image_comparator")
    underline(lines)
    add_config(ic, lines)
    lines.append("\n\nRuntime Stats")
    underline(lines)
    lines.append("Number of generations evolved: {}".format(ga.state.generation_number))
    lines.append("Run time: {}".format(time_str(ga.state.elapsed)))
    filepath = os.path.join(runs.run_dir_path, "report.txt")
    write_strings_to_file(filepath, lines)
    

def run_dir_path(sketch):
    return RunManager(sketch).run_dir_path


def run_number(sketch):
    return RunManager(sketch).run_number
    
    
class RunManager(object):
    # Enforce a singleton pattern
    _instance = None
    def __new__(cls, sketch):
        if cls._instance is None:
            inst = super(RunManager, cls).__new__(cls)
            inst.runs_base_path = sketch.dataPath("runs")
            runnumbers = sorted([int(fn.split("-")[1].lstrip("0")) for fn in listfiles(inst.runs_base_path)])
            prevrun = runnumbers[-1] if runnumbers else 0
            inst.run_number = prevrun + 1
            folder_name = "run-{0:04d}".format(inst.run_number)
            inst.run_dir_path = os.path.join(inst.runs_base_path, folder_name)
            cls._instance = inst
        return cls._instance

        

#####################################################################
# Processing-specific helpers
#####################################################################


class GraphicsBuffer(object):
    # Enforce a singleton pattern that allows only one instance
    # per width+height pair to be created.
    _instances = {}
    def __new__(cls, createGraphics, canvas_width, canvas_height):
        key = "{}_{}".format(canvas_width, canvas_height)
        if key not in cls._instances:
            w = int(round(canvas_width))
            h = int(round(canvas_height))
            cls._instances[key] = createGraphics(w, h)
        return cls._instances[key]


class FrameRateRegulator(object):
    """
    Automatically adjust the frame rate of a Processing sketch
    to minimize CPU hogging. The call to end_draw() will check
    the current sketch frameRate and adjust accordingly so that
    there is some CPU headroom.

    Usage:

    fr = utils.FrameRateRegulator(this)

    def draw():
        fr.start_draw()
        # Do your drawing here
        fr.end_draw(frameRate)
    """
    
    # Enforce a singleton pattern
    _instance = None
    def __new__(cls, sketch):
        if cls._instance is None:
            cls._instance = super(FrameRateRegulator, cls).__new__(cls)
            cls._instance.duration_history = []
            cls._instance.starttime = time.time()
        return cls._instance
    
    def __init__(self, sketch, samplesize=10, tolerance=1.5):
        self.sketch = sketch
        self.sample_size = samplesize
        self.tolerance = tolerance
        
    def start_draw(self):
        self.starttime = time.time()
    
    # We need to pass in the frameRate value because Python doesn't allow the 
    # sketch to use the same name for frameRate function and frameRate variable.
    def end_draw(self, frameRate): 
        endtime = time.time()
        elapsed = endtime - self.starttime
        self.duration_history.append(elapsed)
        if len(self.duration_history) > self.sample_size:
            mean_duration = sum(self.duration_history) / len(self.duration_history)
            self.duration_history = []
            current_frameduration = 1.0 / frameRate
            if current_frameduration < mean_duration:
                new_frameduration = mean_duration * self.tolerance
                new_frame_rate = round(1.0 / new_frameduration, 1)
                self.sketch.frameRate(new_frame_rate)
                print("Automatically adjusted sketch frame rate to {} fps".format(new_frame_rate))
                
                
                
#####################################################################
# Generic Python helpers
#####################################################################


def remap(valuetoscale, minallowed, maxallowed, minold, maxold):
    return (maxallowed - minallowed) * (valuetoscale - minold) / (maxold - minold) + minallowed


class Grid(object):
    def __init__(self, width, height, cols, rows):
        self.cells = []
        self.width = width
        self.height = height
        cell_width = float(width) / cols
        cell_height = float(height) / rows
        for r in range(rows):
            top = height * float(r) / rows
            for c in range(cols):
                left = width * float(c) / cols
                self.cells.append(GridCell(left, top, cell_width, cell_height))
                
class GridCell(object):
    def __init__(self, left, top, width, height):
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.center = Point(self.left + self.width / 2.0, self.top + self.height / 2.0)
    
    @property
    def cx(self):
        return self.center.x
        
    @property
    def cy(self):
        return self.center.y

        
class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def distance_to(self, other):
        return math.sqrt((self.x-other.x)**2 + (self.y-other.y)**2)
        
    def move_to(self, target):
        self.x = target.x
        self.y = target.y
    
    def __repr__(self):
        return "<Point>[{},{}]".format(self.x, self.y)
        
        
def inspect(obj):
    for key in dir(obj):
        val = getattr(obj, key)
        print("{} {}".format(key, type(vawl)))


class Timer(object):
    def __init__(self):
        self.reset()
    def start(self):
        self.reset()
    def elapsed(self):
        return time.time() - self.starttime
    def reset(self):
        self.starttime = time.time()
        
            
def jitter(val, max_amount):
    return val + max_amount * (random.random() - 0.5)
    

def euclidean_distance(x1, y1, x2, y2):
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)


def sort_by_key(list_to_sort, keys, reverse=False):
    return [item[0] for item in sorted(zip(list_to_sort, keys), key = lambda x: x[1], reverse=reverse)]
    

def get_function_by_name(parent, name):
    return getattr(parent, name)


def normalized_value_to_index(val, thelist):
    return int(math.floor(min(val, 0.9999999) * len(thelist)))
    
    
def constrain(value, minimum, maximum):
    return max(minimum, min(value, maximum))
    

def partition_list(inputList, chunkSize):
    return [inputList[i:i+chunkSize] for i in range(0, len(inputList), chunkSize)]


def listfiles(parent_path, sorted=True, exclude_dotfiles=True, fullpath=False):
    try:
        files = os.listdir(parent_path)
    except:
        return []
    if exclude_dotfiles:
        files = [f for f in files if not f.startswith(".")]
    if sorted:
        files.sort()
    if fullpath:
        files = [os.path.join(parent_path, f) for f in files]
    return files


def write_strings_to_file(filepath, strings):
    f = open(filepath, 'w')
    for line in strings:
         f.write(line)
         f.write('\n')
    f.close()
    

def isinteger(var):
    try:
        int(var)
        return True
    except:
        return False


def isnumeric(var):
    try:
        float(var)
        return True
    except:
        return False
    

def get_attributes(obj, names=None):
    attributes = {}
    for var in dir(obj):
        if names and (var not in names): continue
        settings[var] = getattr(obj, var)
    return attributes

def validate_set(name, val):
    if not val: raise ValueError("Variable {} has not been set.".format(name))

    
def create_folder(path):
    try:
        os.mkdir(path)
    except:
        pass
        

def save_object(path, obj):
    if not obj: return
    f = open(path, 'wb')
    pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
    f.close()
    

def load_object(path):
    f = open(path, 'rb')
    obj = pickle.load(f)
    f.close()
    return obj


def time_str(secs):
    mins = int(round(secs)) / 60
    secs = round(secs - (mins * 60))
    return "{} min {} sec".format(mins, secs)
