import genetic as ga
import drawing
import utils
import image_comparator as ic
import settings as config


def setup():
    size(400, 400)
    utils.configure(drawing, config.drawing)
    utils.configure(ga, config.ga)
    utils.configure(ic, config.ic)
    drawing.initialize()
    ga.initialize(drawing.num_params(), create_phenotype, compute_fitness)
    if config.app.testmode:
        print("Exploring the space of random solutions...")
    else:
        print("Starting run {}".format(utils.run_number(this)))
        print("Press spacebar to toggle preview of processed images.")
        utils.create_report(this, drawing, ga, ic)
        utils.copy_input_images(this)


def draw():
    if utils.is_paused(): return
    if config.app.testmode:
        frameRate(1)
        image(ga.random_phenotype(), 0, 0)
    else:
        if ga.finished(): return
        image(ga.fittest_phenotype(), 0, 0)
        utils.autosave(this, ga, drawing, config.app.autosave_fittest_only)
        ga.evolve()
        ic.draw_preview(this)


# Convert a list of numbers (genes) to a drawing image.
def create_phenotype(chromosome):
    drawing.render(this, chromosome)
    image = this.get() # Grab the current canvas as an image
    return image


# Return a fitness score for a given drawing image.
def compute_fitness(phenotype):
    score = ic.compare(this, phenotype)
    return score
 
    
def keyPressed():
    if key == " ": 
        ic.toggle_preview() # Use spacebar to toggle fitness images on/off

    
# Java calls this function automatically when the program stops
def stop():
    if not config.app.testmode:
        print("All output was saved to <{}>.".format(utils.run_dir_path(this)))
    print("Exit.")


# Try loading the optional fitness.py module in case the
# project wants to define a its own fitness function.
try: 
    import fitness
    if hasattr(fitness, "compute_fitness"):
        compute_fitness = fitness.compute_fitness # Replace the default fitness function
except: 
    pass # No module or function found so just use default function in the current module
    
