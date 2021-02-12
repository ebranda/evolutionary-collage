"""
This module provides various utility functions.
"""

# Generic Python imports
import pickle
import os
import math
import time
import random
from distutils.dir_util import copy_tree
import shutil
import settings as config


def autosave(sketch, ga, drawing, fittestonly):
    if not ga.fitness_changed(): return
    save_hi_res(sketch, ga, drawing, fittestonly)
    
    
def save_low_res(sketch, ga):
    '''Save a snapshot of the current canvas.'''
    runs = RunManager(sketch)
    create_folder(runs.run_dir_path)
    filename = "generation-{0:04d}.png".format(ga.generation_number())
    filepath = os.path.join(run_output_path(sketch), filename)
    image = sketch.get()
    image.save(filepath)


def save_hi_res(sketch, ga, drawing, replace=False):
    '''Render and save a hi-res version of the fittest solution.'''
    runs = RunManager(sketch)
    create_folder(runs.run_dir_path)
    w = drawing.hi_res_width
    h = sketch.height * drawing.hi_res_width / sketch.width
    canvas = GraphicsBuffer(sketch.createGraphics, w, h)
    canvas.beginDraw()
    drawing.render(sketch, ga.fittest().genes, canvas)
    canvas.endDraw()
    filename = "generation-{0:04d}-hi-res.png".format(ga.generation_number())
    outputdir = run_output_path(sketch)
    if replace and os.path.isdir(outputdir):
        delete_contents(outputdir)
    filepath = os.path.join(outputdir, filename)
    canvas.save(filepath)
    #print("Saved hi-res image of fittest in generation {}".format(ga.generation_number()))
    

def create_report(sketch, drawing, ga, ic):
    runs = RunManager(sketch)
    create_folder(runs.run_dir_path)
    copy_file_to(os.path.join(sketch.sketchPath(), "adminsettings.py"), os.path.join(run_dir_path(sketch)))
    copy_file_to(os.path.join(sketch.sketchPath(), "settings.py"), os.path.join(run_dir_path(sketch)))
    

def create_report_OBS(sketch, drawing, ga, ic):
    runs = RunManager(sketch)
    create_folder(runs.run_dir_path)
    lines = []
    def add_config(obj, lines):
        for attr in dir(obj):
            if not attr.startswith("config_"): continue
            lines.append("{} = {}".format(attr, getattr(obj, attr)))
    def underline(lines):
        #lines.append("".join(["-"] * len(lines[-1]) * 2))
        lines.append("".join(["-"] * 45))
    lines.append("Module settings: drawing")
    underline(lines)
    add_config(drawing, lines)
    lines.append("\n\nModule settings: genetic")
    underline(lines)
    add_config(ga, lines)
    lines.append("\n\nModule settings: image_comparator")
    underline(lines)
    add_config(ic, lines)
    #lines.append("\n\nRuntime Stats")
    #underline(lines)
    #lines.append("Number of generations evolved: {}".format(ga.state.generation_number))
    #lines.append("Run time: {}".format(time_str(ga.state.elapsed)))
    filepath = os.path.join(runs.run_dir_path, "report.txt")
    write_strings_to_file(filepath, lines)
    

def copy_input_images(sketch):
    copy_folder_to(app_data_path(sketch, "parts"), os.path.join(run_dir_path(sketch), "inputs", "parts"))
    copy_folder_to(app_data_path(sketch, "comparator_samples"), os.path.join(run_dir_path(sketch), "inputs", "comparator_samples"))


def app_data_path(sketch, subfolder):
    if hasattr(config.app, "data_folder_name") and config.app.data_folder_name is not None:
        return os.path.join(sketch.dataPath(config.app.data_folder_name), subfolder)
    else:
        return sketch.dataPath(subfolder)


def run_output_path(sketch):
    return os.path.join(RunManager(sketch).run_dir_path, "output")


def run_dir_path(sketch):
    return RunManager(sketch).run_dir_path


def run_number(sketch):
    return RunManager(sketch).run_number


def toggle_paused():
    global paused
    if not is_paused():
        paused = True
    else:
        paused = False
        

def is_paused():
    return "paused" in globals() and paused
    
    
class RunManager(object):
    # Enforce a singleton pattern
    _instance = None
    def __new__(cls, sketch):
        if cls._instance is None:
            inst = super(RunManager, cls).__new__(cls)
            inst.runs_base_path = app_data_path(sketch, "runs")
            try: 
                os.mkdir(inst.runs_base_path)
            except:
                pass
            runnumbers = sorted([int(fn.split("-")[1].lstrip("0")) for fn in listfiles(inst.runs_base_path)])
            prevrun = runnumbers[-1] if runnumbers else 0
            inst.run_number = prevrun + 1
            folder_name = "run-{0:04d}".format(inst.run_number)
            inst.run_dir_path = os.path.join(inst.runs_base_path, folder_name)
            cls._instance = inst
        return cls._instance


#####################################################################
# Fitness helpers
#####################################################################


def score_density(grays, threshld, targetdensity):
    thresholded = threshold(grays, threshld)
    targetcount = targetdensity * len(grays)
    densityscore = score_occurrences(thresholded, 0, targetcount)
    return densityscore

def score_gray_levels(values, target):
    error = abs(mean(values) - target) / max(target, 255-target)
    return 1.0 - error
    
def threshold(values, threshold):
    return [0.0 if v < threshold else 255.0 for v in values]
   
def score_occurrences(values, targetvalue, targetcount):
    count = 0
    for v in values:
        if v == targetvalue:
            count += 1
    error = abs(count-targetcount) / float(max(targetcount, len(values)-targetcount))
    return 1.0 - error

def score_symmetry(matrix):
    score = 0
    for row in matrix:
        left, right = split_list(row)
        right.reverse()
        rowscore = 0
        for i in range(len(left)):
            colscore = 1.0 - abs(left[i] - right[i]) / 255.0
            rowscore += colscore
        score += rowscore / float(len(left))
    return (score / float(len(matrix))) ** 2
    
def score_target(val, targetval, minval=0.0, maxval=1.0):
    error = abs(val - targetval)
    errornormalized = error / float(max(targetval-minval, maxval-targetval))
    return 1.0 - errornormalized
    
  

#####################################################################
# Processing-specific helpers
#####################################################################


def extract_pixel_values(pimg, samplesize, mode="gray", threshold=128, normalized=False):
    img = pimg.copy() # Create a copy before resizing so we preserve the original
    img.resize(samplesize, samplesize)
    n = 255.0 if normalized else 1.0
    if mode == "gray":
        return [brightness(pixel)/n for pixel in img.pixels]
    if mode == "color":
        return [hue(pixel)/n for pixel in img.pixels]
    if mode == "binary":
        img.filter(GRAY)
        img.filter(THRESHOLD, threshold/255.0)
        return [brightness(pixel)/n for pixel in img.pixels]
    if mode == "color":
        vals = []
        for pixel in img.pixels:
            r = red(pixel)
            g = green(pixel)
            b = blue(pixel)
            avg = mean([r, g, b])
            vals.append(avg/n)
        return vals
        

class GraphicsBuffer(object):
    # Enforce a singleton pattern that allows only one instance
    # per width+height pair to be created.
    _instances = {}
    def __new__(cls, createGraphics, canvas_width, canvas_height):
        w = int(math.ceil(canvas_width))
        h = int(math.ceil(canvas_height))
        key = "{}_{}".format(w, h)
        if key not in cls._instances:
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
    
    def __init__(self, sketch, samplesize=5, tolerance=1.5):
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
                new_frame_rate = round(1.0 / new_frameduration, 4)
                self.sketch.frameRate(new_frame_rate)
                print("Automatically adjusted sketch frame rate to {} fps".format(new_frame_rate))
                
                
#####################################################################
# Generic Python helpers
#####################################################################

def coerce_list(obj):
    if type(obj) is list:
        return obj
    if type(obj) is tuple:
        return list(tuple)
    return [obj]

def configure(obj, config):
    for attr in config.attribute_names():
        setattr(obj, attr, getattr(config, attr))
        
def filepath(*args):
    return os.path.sep.join(args)
    
    
def delete_contents(directory):
    for f in os.listdir(directory):
        os.remove(os.path.join(directory, f))


def copy_folder_to(folderpath, targetdir):
    copy_tree(folderpath, targetdir)


def copy_file_to(filepath, targetdir):
    if os.path.isfile(filepath):
        shutil.copy(filepath, targetdir)


def remap(valuetoscale, minallowed, maxallowed, minold=0.0, maxold=1.0):
    return (maxallowed - minallowed) * (valuetoscale - minold) / (maxold - minold) + minallowed


class Grid(object):
    def __init__(self, width, height, cols, rows):
        self.cells = []
        self.width = width
        self.height = height
        self.cell_dim_x = float(width) / cols
        self.cell_dim_y = float(height) / rows
        for r in range(rows):
            top = height * float(r) / rows
            for c in range(cols):
                left = width * float(c) / cols
                self.cells.append(GridCell(left, top, self.cell_dim_x, self.cell_dim_y, r, c))
                
class GridCell(object):
    def __init__(self, left, top, width, height, row, col):
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.row = row
        self.col = col
        self.center = Point(self.left + self.width / 2.0, self.top + self.height / 2.0)
        self.top_left = Point(self.left, self.top)
        self.bottom_right = Point(self.left + self.width, self.top + self.height)
    
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
        
    def move(self, tx, ty):
        self.x += tx
        self.y += ty
    
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


def split_list(values, cullaxis=True):
    left = values[:len(values)/2]
    right = values[len(values)/2:]
    if cullaxis and len(right) > len(left):
        right.pop(0)
    return left, right
    

def flip_matrix(twodlist):
    return [list(subarray) for subarray in zip(*twodlist)]
    


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
    
def mean(data):
    """Return the sample arithmetic mean of data."""
    n = len(data)
    if n < 1:
        raise ValueError('mean requires at least one data point')
    return sum(data)/float(n)

def _ss(data):
    """Return sum of square deviations of sequence data."""
    c = mean(data)
    ss = sum((x-c)**2 for x in data)
    return ss

def stddev(data, ddof=0):
    """Calculates the population standard deviation
    by default; specify ddof=1 to compute the sample
    standard deviation."""
    n = len(data)
    if n < 2:
        raise ValueError('variance requires at least two data points')
    ss = _ss(data)
    pvar = ss/(n-ddof)
    return pvar**0.5
