'''
This is the main Processing sketch
'''

# Import the Python code modules (.py files) that we need
from modules import genetic as ga
from modules import drawing
from modules import utils
from modules import image_comparator as ic
import config


def setup():
    size(400, 400)
    utils.configure(drawing, config)
    utils.configure(ic, config)
    utils.configure(ga, config)
    ga.genome_size = drawing.genes_per_shape * drawing.number_of_shapes
    ga.phenotype_function = create_phenotype
    ga.fitness_function = compute_fitness
    utils.print_startup_messages(this)
    

def draw():
    if ga.finished(): return
    ga.evolve()
    fittest_drawing = ga.fittest_phenotype()
    image(fittest_drawing, 0, 0)
    if ga.fitness_changed():
        utils.save_low_res(this, ga)
    ic.draw_preview(this)
    

def mouseClicked():
    utils.save_hi_res(this, ga, drawing, createGraphics)
 
    
def keyPressed():
    if key == " ": 
        ic.toggle_preview()


def stop():
    utils.save_hi_res(this, ga, drawing, createGraphics)
    utils.create_report(this, config, ga)
    utils.print_shutdown_messages(this)


def create_phenotype(chromosome):
    drawing.render(this, chromosome)
    image = this.get() # Grab the current canvas as an image
    return image


def compute_fitness(phenotype):
    score = ic.compare(this, phenotype)
    return score
    
    
    
