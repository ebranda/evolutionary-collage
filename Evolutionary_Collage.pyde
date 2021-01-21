# Import the Python code modules (.py files) that we need
import genetic as ga
import drawing
import utils
import image_comparator as ic
import config


def setup():
    size(400, 400)
    ga.phenotype_function = create_phenotype
    ga.fitness_function = compute_fitness
    genome_size = drawing.config_genes_per_shape * drawing.config_number_of_shapes
    ga.initialize(genome_size)
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
    utils.create_report(this, drawing, ga, ic)
    utils.print_shutdown_messages(this)


def create_phenotype(chromosome):
    drawing.render(this, chromosome)
    image = this.get() # Grab the current canvas as an image
    return image


def compute_fitness(phenotype):
    score = ic.compare(this, phenotype)
    return score
    
    
    
