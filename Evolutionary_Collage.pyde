import genetic as ga
import drawing
import utils
import image_comparator as ic

testmode = False # Set this to True to explore the solution space or False to run the solver.


def setup():
    size(400, 400)
    ga.phenotype_function = create_phenotype
    ga.fitness_function = compute_fitness
    ga.initialize(drawing.num_params())
    if testmode:
        print("Exploring the space of random solutions...")
    else:
        print("Starting run {}".format(utils.run_number(this)))
        print("Press spacebar to toggle preview of processed images.")
        utils.create_report(this, drawing, ga, ic)
        utils.copy_input_images(this)
    

def draw():
    if utils.is_paused(): return
    if testmode:
        frameRate(1)
        image(ga.random_phenotype(), 0, 0)
    else:
        if ga.finished(): return
        image(ga.fittest_phenotype(), 0, 0)
        if ga.fitness_changed():
            utils.save_hi_res(this, ga, drawing, createGraphics)
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


def mouseClicked():
    utils.toggle_paused()
    if utils.is_paused(): 
        print("Paused program. Click in the window again to unpause.")
 
    
def keyPressed():
    if key == " ": 
        ic.toggle_preview() # Use spacebar to toggle fitness images on/off


# Processing calls this function automatically when the program stops
def stop():
    if not testmode:
        print("All output was saved to <{}>.".format(utils.run_dir_path(this)))
    print("Exit.")
    
    
