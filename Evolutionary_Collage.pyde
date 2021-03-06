import genetic as ga
import drawing
import utils
import image_comparator as ic
import settings as config

config.version = "0.47"


def setup():
    size(appwidth, appheight)
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
        utils.create_report(this, config, drawing, ga, ic)
        utils.copy_input_images(this)
        global fr
        fr = utils.FrameRateRegulator(this)


def draw():
    if utils.is_paused(): return
    if config.app.testmode:
        frameRate(0.5)
        image(ga.random_phenotype(), 0, 0)
    else:
        if ga.finished(): return
        if config.app.regulate_frame_rate:
            fr.start_draw()
        image(ga.fittest_phenotype(), 0, 0)
        utils.autosave(this, ga, drawing, config.app.autosave_fittest_only)
        if ga.fitness_changed():
            fittest_callback(this, ga)
        ga.evolve()
        ic.draw_preview(this)
        if config.app.regulate_frame_rate:
            fr.end_draw(frameRate)


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

# Clicking in the window will pause the script
def mouseClicked(e):
    utils.toggle_paused()
    if utils.is_paused():
        print "Paused the script. Click again to resume."
    else:
        print "Resumed the script. Click again to pause."
 
   
# Java calls this function automatically when the program stops
def stop():
    if not config.app.testmode:
        print("All output was saved to <{}>.".format(utils.run_dir_path(this)))
    print("Exit.")

# This function can be overwritten by the fitness.py module
# It is called after each evolution that produces a fitter solution.
def fittest_callback(sketch, ga):
    pass

    
# Try loading the optional fitness module in case the
# project wants to define a its own fitness function.
try: 
    import fitness
    if hasattr(fitness, "compute_fitness"):
        compute_fitness = fitness.compute_fitness # Replace the default fitness function
    else:
        print("No compute_fitness() function found in fitness.py... using default.") 
    if hasattr(fitness, "fittest_callback"):
        fittest_callback = fitness.fittest_callback # Replace the default callback function
except Exception as e:
    print("No custom fitness function found... using default compute_fitness().") 
    print("{}".format(e))

# Try loading the optional adminsettings module in case the
# project wants to override any settings in settings.py
try:
    import adminsettings
    adminsettings.override(config)
except:
    pass

appwidth = config.width if hasattr(config, "width") else 400
appheight = config.height if hasattr(config, "height") else 400

    
