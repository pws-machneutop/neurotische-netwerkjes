import random
from . import configuration

SPECIES_ID = 1

class Species():
    def __init__(self):
        global SPECIES_ID
        SPECIES_ID += 1
        self.config = configuration.getGlobalConfig()
        self.id = SPECIES_ID
        self.genomes = []
        self.topFitness = 0.0
        self.averageFitness = 0.0
        self.staleness = 0

    def calculateAverageFitness(self):
        total = 0

        for genome in self.genomes:
            total = total + genome.globalRank

        self.averageFitness = total / len(self.genomes)

    def sortGenomes(self):
        self.genomes.sort(key=lambda genome: genome.fitness, reverse=True)
