#
# NetworkPool
# 

class NetworkPool():
    def __init__(self, nNetworks, initialNetwork):
        self.pool = {0: [initialNetwork.copy() for n in range(nNetworks)]}

    def run(inputs, fitnessFunction):
        for species, networks in self.pool.items():
            for network in networks:
                for input in inputs:
                    output = network.runWith(input)
                    fitness = fitnessFunction(input, output)
