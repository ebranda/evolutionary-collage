"""
This module provides an implementation of a genetic algorithm.

"""
import random
import time
import math
import utils


# Settings
config_mutation_rate = 0.08
config_fitness_decimal_places = 4
max_stagnant_generations = 1000
update_interval = 10
verbose = False

# Callback functions
phenotype_function = None
fitness_function = None
fitness_changed_callback = None


class Population(object):
    
    def __init__(self):
        self.individuals = []
        self.matingpool = []
        self.fittest = None
        
    def update(self, individuals, phenotype_function, fitness_function):
        self.individuals = []
        for i, ind in enumerate(individuals):
            ind.update(phenotype_function, fitness_function)
            self.individuals.append(ind)
        # Cache the fittest individual
        for ind in self.individuals:
            if self.fittest is None or ind.fitter_than(self.fittest):
                self.fittest = ind
        # Build the mating pool of fittest individuals for the next generation
        ranked = sorted(self.individuals, key=lambda ind: ind.fitness)
        # Use the rank position squared as the mating probability
        # Divide by the population size to more reasonable value.
        probabilities = [int(round(((r + 1) ** 2) / float(len(self.individuals)))) for r in range(len(ranked))]
        self.matingpool = []
        for ind, prob in zip(ranked, probabilities):
            self.matingpool.extend([ind] * prob)
    
    def random_parents(self):
        parent1 = random.choice(self.matingpool)
        parent2 = random.choice(self.matingpool)
        return parent1, parent2
        
    @property
    def initialized(self):
        return len(self.individuals) > 0


class Individual:

    def __init__(self, genes=None):
        self.genes = genes
        self.phenotype = None
        self.fitness = None
        
    def randomize(self, genome_size):
        self.genes = [random.random() for g in range(genome_size)]
        return self
        
    def update(self, phenotype_func, fitness_func):
        self.phenotype = phenotype_func(self.genes)
        score = fitness_func(self.phenotype)
        self.fitness = round(score, config_fitness_decimal_places) # Round so we don't waste time on trivial fitness changes
        
    def fitter_than(self, other):
        return self.fitness > other.fitness
        
    def breed_with(self, other, mutationrate):
        # Crossover
        genomelength = len(self.genes)
        midpoint = int(random.randint(0, genomelength-1))
        childgenes = [self.genes[i] if i > midpoint else other.genes[i] for i in range(genomelength)]
        # Mutate
        if random.random() < mutationrate:
            childgenes[random.randint(0, genomelength-1)] = random.random()
        return Individual(childgenes)
    

class EvolverState(object):
    
    def __init__(self):
        self.reset()
        self.max_gens = 0
        self.fitness_changed = False
    
    def reset(self):
        self.generation_number = 0
        self.stagnant_count = 0
        self.high_score = None
        self.start_time = time.time()
        self.end_time = None
    
    def new_generation(self, population):
        self.generation_number += 1
        self.fitness_changed = False
        newfittest = population.fittest
        if newfittest.fitness > self.high_score:
            self.high_score = newfittest.fitness
            self.fitness_changed = True
            self.stagnant_count = 0
        else:
            self.stagnant_count += 1
    
    def end(self):
        self.end_time = time.time()
        
    @property
    def finished(self):
        return self.stagnant_count >= self.max_gens and self.generation_number > 0
        
    @property
    def is_first_gen(self):
        return self.generation_number == 1
    
    @property
    def elapsed(self):
        if not self.end_time:
            self.end_time = time.time()
        return self.end_time - self.start_time


population = Population()
state = EvolverState()

def initialize(genome_size):
    ''' Initialize the population and evolver state.'''
    if population.initialized: return
    popsize = int(round(genome_size * 1.5)) # Or 1.75 is better in general
    utils.validate_set("phenotype_function", phenotype_function)
    utils.validate_set("fitness_function", fitness_function)
    firstgen = [Individual().randomize(genome_size) for i in range(popsize)]
    population.update(firstgen, phenotype_function, fitness_function)
    state.max_gens = max_stagnant_generations

def evolve():
    ''' Evolve a generation.
    
    This is the main heartbeat of the evolver. Call it from a loop.
    '''
    # Check initialized
    if not population.initialized:
        raise RuntimeError("ERROR: You must call initialize() on the genetic module before calling evolve()")
        
    # Make sure the search is not over
    if state.finished: return
    
    # Replace the current population with its children
    newgen = []
    for i in range(len(population.individuals)):
        parent1, parent2 = population.random_parents()
        child = parent1.breed_with(parent2, config_mutation_rate)
        newgen.append(child)
    population.update(newgen, phenotype_function, fitness_function)
    
    # Update evolver state
    state.new_generation(population)
    if verbose and (state.is_first_gen or state.generation_number % update_interval == 0):
        print("Current state: {}".format(get_progress_message()))
    if fitness_changed():
        print("Fitter solution found [{}]...".format(get_progress_message()))
    if state.finished: 
        print("No fitter solution found after {} unchanged generations. Stopping search.".format(state.stagnant_count))
        state.end()

    
def get_progress_message():
    return "Generation={0:04d} Fitness={1}".format(state.generation_number, state.high_score)

def finished():
    return state.finished
    
def fittest():
    return population.fittest

def fittest_phenotype():
    return fittest().phenotype
    
def random_phenotype():
    return random.choice(population.individuals).phenotype

def high_score():
    return population.fittest.fitness

def fitness_changed():
    return state.fitness_changed

def generation_number():
    return state.generation_number
        
