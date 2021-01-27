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
        print("Click anywhere in the canvas window to save a high resolution image at any time.")
        print("Press spacebar to toggle preview of processed images.")
    

def draw():
    if testmode:
        frameRate(1)
        drawing = ga.random_phenotype()
        image(drawing, 0, 0)
    else:
        if ga.finished(): return
        drawing = ga.fittest_phenotype()
        image(drawing, 0, 0)
        if ga.fitness_changed():
            utils.save_low_res(this, ga)
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
    utils.save_hi_res(this, ga, drawing, createGraphics)
 
    
def keyPressed():
    if key == " ": 
        ic.toggle_preview() # Use spacebar to toggle fitness drawings on/off


# Processing calls this function automatically when the program stops
def stop():
    if not testmode:
        utils.save_hi_res(this, ga, drawing, createGraphics)
        utils.create_report(this, drawing, ga, ic)
        print("All output was saved to <{}>.".format(utils.run_dir_path(this)))
    print("Exit.")
    
    
