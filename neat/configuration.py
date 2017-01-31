import toml
config = None

def getGlobalConfig():
    return config

def loadConfig(filename):
    global config
    config = toml.load(filename)
    return config
