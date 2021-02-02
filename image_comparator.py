"""
This module provides functionality for comparing an input image
to a set of sample images and returing a similarity score.

"""

#add_library('opencv_processing')
#from gab.opencv import OpenCV # see https://github.com/atduskgreg/opencv-processing
import utils


# Default settings - Don't change these here. Instead, change them in the settings.py file.
config_strictness = 4 # 1-5
config_preprocess_mode = "gray" # "binary" or "gray" or "color"
config_threshold = 230 # 0-255 higher value includes lighter grayscale values
config_erode_binary = False
preview_size = 100

sample_images = []
samples = []
last_image = None
preview = False


def toggle_preview():
    global preview
    preview = not preview


def load_samples(sketch):
    samplespath = sketch.dataPath("comparator_samples")
    for filepath in utils.listfiles(samplespath, fullpath=True):
        img = sketch.loadImage(filepath)
        if img is not None:
            img, pixels = img_preprocess(sketch, img, True)
            sample_images.append(img)
            samples.append(pixels)
    if not sample_images:
        print("WARNING: image_compare could not find any sample images. Make sure you have placed in them in the folder {}".format(samplespath))


def draw_preview(sketch):
    if not preview: return
    sketch.fill(255, 150)
    sketch.rect(0, 0, sketch.width, sketch.height)
    sketch.noFill()
    margin = 10
    x, y = margin, margin
    w = h = preview_size
    sketch.tint(210, 230, 255)
    sketch.image(last_image, x, y, w, h)
    sketch.rect(x, y, w, h)
    for img in sample_images:
        x += w + margin
        sketch.image(img, x, y, w, h)
        sketch.rect(x, y, w, h)
    sketch.noTint()
    
    
def img_preprocess(sketch, pImg, is_sample=False):
    sizes = [5, 9, 15, 25, 50]
    i = utils.constrain(int(round(config_strictness)), 1, len(sizes)) - 1
    img = pImg.copy()
    if img.width > img.height:
        img.resize(sizes[i], 0)
    else:
        img.resize(0, sizes[i])        
    if config_preprocess_mode == "color":
        pixels = [sketch.hue(p) for p in img.pixels]
        if is_sample:
            mean = sum(pixels) / len(pixels)
            grayscale = sum(1 if p == mean else 0 for p in pixels)
            if grayscale:
                print("WARNING: config_preprocess_mode is set to color but your comparator image appears to be grayscale.")
                print("   You should change that setting to 'gray' or you will get unpredictable fitness results.") 
    elif config_preprocess_mode == "gray":
        img.filter(sketch.GRAY)
        pixels = [sketch.brightness(p) for p in img.pixels]
    elif config_preprocess_mode == "binary":
        if config_erode_binary:
            img.filter(sketch.ERODE)
        img.filter(sketch.GRAY)
        img.filter(sketch.THRESHOLD, config_threshold/255.0)
        pixels = [sketch.brightness(p) for p in img.pixels]
    else:
        raise ValueError("Illegal value for config_preprocess_mode <{}>".format(config_preprocess_mode))
    return img, pixels


def compare(sketch, pImg):
    ''' Compare an image to the set of sample images.
    
    This is the main public method of the comparator.
    Handles just-in-time initialization.
    '''
    if not samples:
        load_samples(sketch)
    global last_image # Remember it so we can draw a preview if desired
    last_image, imgpixels = img_preprocess(sketch, pImg)
    overall_score = 0.0
    num_pixels = len(imgpixels)
    for samplepixels in samples:
        score = 0.0
        for i in range(num_pixels):
            score += 1.0 - (abs(samplepixels[i] - imgpixels[i]) / 255.0)
        score /= num_pixels # Mean error for all pixel comparisions for this sample
        overall_score += score
    overall_score /= len(samples) # Mean error for all sample comparisons
    return overall_score


def pixel_score(px1, px2):
    score = 0
    for i in range(len(px1)):
        score += 1.0 - (abs(px1[i] - px2[i]) / 255.0)
    return score / float(len(px1))
    
    
def to_rgb(sketch, px):
    return [px >> 16 & 0xFF, px >> 8 & 0xFF, px & 0xFF, sketch.alpha(px)]
