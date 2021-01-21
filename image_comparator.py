"""
This module provides functionality for comparing an input image
to a set of sample images and returing a similarity score.

"""

#add_library('opencv_processing')
#from gab.opencv import OpenCV # see https://github.com/atduskgreg/opencv-processing
import utils


# Default settings
config_strictness = 4 # 1-5
config_threshold = 230 # 0-255 higher value includes lighter grayscale values
config_preprocess_mode = "binary"
config_erode_binary = False


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
            img, pixels = img_preprocess(sketch, img, False)
            sample_images.append(img)
            samples.append(pixels)
    if not sample_images:
        print("WARNING: image_compare could not find any sample images. Make sure you have placed in them in the folder {}".format(samplespath))


def draw_preview(sketch):
    if not preview: return
    margin = 10
    x, y = margin, margin
    w, h = 50, 50
    sketch.tint(210, 230, 255)
    sketch.image(last_image, x, y, w, h)
    sketch.rect(x, y, w, h)
    for img in sample_images:
        x += w + margin
        sketch.image(img, x, y, w, h)
        sketch.rect(x, y, w, h)
    sketch.noTint()
    
    
def img_preprocess(sketch, pImg, erode_binary):
    sizes = [5, 9, 15, 25, 50]
    i = utils.constrain(int(round(config_strictness)), 1, len(sizes)) - 1
    img = pImg.copy()
    if img.width > img.height:
        img.resize(sizes[i], 0)
    else:
        img.resize(0, sizes[i])        
    if "config_preprocess_mode" in globals() and config_preprocess_mode == "binary":
        if erode_binary:
            img.filter(sketch.ERODE)
        img.filter(sketch.GRAY)
        img.filter(sketch.THRESHOLD, config_threshold/255.0)
    pixels = [sketch.brightness(p) for p in img.pixels]
    return img, pixels


def compare(sketch, pImg):
    ''' Compare an image to the set of sample images.
    
    This is the main public method of the comparator.
    Handles just-in-time initialization.
    '''
    if not samples:
        load_samples(sketch)
    global last_image # Remember it so we can draw a preview if desired
    last_image, imgpixels = img_preprocess(sketch, pImg, config_erode_binary)
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
    
