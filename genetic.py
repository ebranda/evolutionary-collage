"""
This module provides an implementation of a genetic algorithm.

"""
import random
import time
import math
import utils


# Settings
config_mutation_rate = 0.08
config_fitness_decimal_places = 2
max_stagnant_generations = 50
update_interval = 10
verbose = False

# Callback functions
phenotype_function = None
fitness_function = None


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
        self.generation_number = 0
        self.stagnant_count = 0
        self.high_score = None
        self.start_time = time.time()
        self.end_time = None
        self.fitness_changed = True
        self.fittest = None
        self.max_gens = max_stagnant_generations
        
    def update(self, population):
        self.generation_number += 1
        self.fitness_changed = False
        fittest = max(population, key=lambda ind: ind.fitness)
        if fittest.fitness > self.high_score:
            self.high_score = fittest.fitness
            self.fitness_changed = True
            self.fittest = fittest
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


class Evolver(object):
    
    def __init__(self):
        self.population = []
        self.state = EvolverState()
    
    def initialize(self, genomesize, phenotype_func, fitness_func, popsize=None):
        ''' Initialize the population and evolver state.'''
        if self.initialized: return
        self.phenotype_function = phenotype_func
        self.fitness_function = fitness_func
        if popsize is None:
            popsize = int(round(genomesize * 1.5)) # Or 1.75 is better in general
        self.population = [Individual().randomize(genomesize) for i in range(popsize)]
        self.matingpool = []
        self.update_population()
        
    @property
    def initialized(self):
        return len(self.population) > 0
        
    def evolve(self):
        ''' Evolve a generation. This is the main heartbeat 
        of the evolver. Call it from a loop.
        '''
        if not self.initialized:
            raise RuntimeError("ERROR: Evolver.evolve() called before Evolver has been initialized")
        
        # Make sure the search is not over
        if self.state.finished: return
    
        # Replace the current population with its children
        newgen = []
        for i in range(len(self.population)):
            parent1 = random.choice(self.matingpool)
            parent2 = random.choice(self.matingpool)
            child = parent1.breed_with(parent2, config_mutation_rate)
            newgen.append(child)
        self.population = newgen
        self.update_population()
    
        # Update evolver state
        self.state.update(self.population)
        msg = "Generation={0:04d} Fitness={1}".format(self.state.generation_number, self.state.high_score)
        if verbose and (self.state.is_first_gen or self.state.generation_number % update_interval == 0):
            print("Current state: {}".format(msg))
        if self.state.fitness_changed:
            print("Fitter solution found [{}]...".format(msg))
        if self.state.finished: 
            print("No fitter solution found after {} unchanged generations. Stopping search.".format(self.state.stagnant_count))
            self.state.end()
            
    def update_population(self):
        for ind in self.population:
            ind.update(self.phenotype_function, self.fitness_function)
        # Cache the fittest individual
        for ind in self.population:
            if self.state.fittest is None or ind.fitter_than(self.state.fittest):
                self.state.fittest = ind
        # Build the mating pool of fittest individuals for the next generation
        ranked = sorted(self.population, key=lambda ind: ind.fitness)
        # Use the rank position squared as the mating probability
        # Divide by the population size to more reasonable value.
        probabilities = [int(round(((r + 1) ** 2) / float(len(self.population)))) for r in range(len(ranked))]
        self.matingpool = []
        for ind, prob in zip(ranked, probabilities):
            self.matingpool.extend([ind] * prob)
        
    
evolver = Evolver()

def initialize(genome_size, phenotype_func, fitness_func):
    evolver.initialize(genome_size, phenotype_func, fitness_func)
    
def evolve():
    evolver.evolve()

def finished():
    return evolver.state.finished
    
def fittest():
    return evolver.state.fittest

def fittest_phenotype():
    return fittest().phenotype
    
def random_phenotype():
    return random.choice(evolver.population).phenotype

def high_score():
    return evolver.population.fittest.fitness

def fitness_changed():
    return evolver.state.fitness_changed

def generation_number():
    return evolver.state.generation_number
        
