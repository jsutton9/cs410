class Game:
    def __init__(self):
        self.title = None
        self.author = None
        self.rooms = {}
        self.kinds = {}
        self.things = {}
        self.everyTurn = []
        self.whenPlayBegins = []
        self.insteadRules = {}
        self.afterRules = {}
        self.understand = {}
        self.lastRoom = None
        self.turn = 0
        self.directions = {"east": "west", "west": "east", "north": "south", "south": "north", "up": "down", "down": "up", "inside": "outside", "outside": "inside"}
        self.currentRoom = None
        self.inventory = []

        thing = Kind("thing", None)
        self.kinds["thing"] = thing
        self.kinds["person"] = Kind("person", thing)

        self.understand["taking"] = "take"
        self.understand["eating"] = "eat"
        self.understand["looking"] = "look"
        self.understand["quitting"] = "quit"
        self.understand["in"] = "inside"
        self.understand["out"] = "outside"
        self.understand["i"] = "inventory"
        self.understand["q"] = "quit"
        self.understand["l"] = "look"

class Room:
    def __init__(self):
        self.name = None
        self.description = None
        self.contents = []
        self.adjacent = {}

    def describe(self):
        words = self.name.split(' ')
        for i in xrange(len(words)):
            words[i] = words[i][0].upper() + words[i][1:]
        ret = ' '.join(words)
        if self.description != None:
            ret += "\n"+self.description
        if self.contents:
            named = []
            unnamed = {}
            for thing in self.contents:
                if thing.name == None:
                    if thing.kind.name in unnamed:
                        unnamed[thing.kind.name] += 1
                    else:
                        unnamed[thing.kind.name] = 1
            ret += "\n"
            for name in named:
                ret += "\nYou can see " + name + " here."
            for name in unnamed:
                ret += "\nYou can see "
                if unnamed[name] == 1:
                    if name[0] in ["a", "e", "i", "o", "u"]:
                        ret += "an " + name + " here."
                    else:
                        ret += "a " + name + " here."
                else:
                    ret += str(unnamed[name]) + " " + plural(name) + " here."
        return ret

    def getThing(self, name):
        for thing in self.contents:
            if thing.name==name or thing.name==None and thing.kind.name==name:
                return thing
        return None

class Kind:
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        if parent != None:
            self.qualities = parent.qualities.copy()
        else:
            self.qualities = {}
        self.lastReferenced = None

    def setQuality(self, quality, value):
        self.qualities[quality] = value

class Thing:
    def __init__(self, kind, turn=0):
        self.name = None
        self.kind = kind
        self.location = None
        self.qualities = kind.qualities.copy()
        self.lastChanged = {q: turn for q in self.qualities}
        self.contents = []

    def setQuality(self, quality, value, turn=0):
        if quality not in self.qualities or self.qualities[quality] != value:
            self.lastChanged[quality] = turn
        self.qualities[quality] = value

    def getThing(self, name):
        for thing in self.contents:
            if thing.name==name or thing.name==None and thing.kind.name==name:
                return thing
        return None

    def describe(self):
        if self.name != None:
            ret = self.name
        elif name[0] in ['a', 'e', 'i', 'o', 'u']:
            ret = "An " + self.kind.name
        else:
            ret = "A " + self.kind.name
        if self.contents:
            named = []
            unnamed = {}
            for thing in self.contents:
                if thing.name == None:
                    if thing.kind.name in unnamed:
                        unnamed[thing.kind.name] += 1
                    else:
                        unnamed[thing.kind.name] = 1
            ret += " with"
            for name in named:
                ret += name
            for name in unnamed:
                if unnamed[name] == 1:
                    ret += "\n  a " + name
                else:
                    ret += str(number) + " " + plural(name)
        return ret

def plural(word):
    if word[-1] in ['s', 'z', 'o'] or word[-2:] in ['sh', 'ch']:
        return word + "es"
    elif word[-1] == 'y' and word[-2] not in ['a', 'e', 'i', 'o', 'u']:
        return word[:-1] + "ies"
    else:
        return word + "s"

def singular(word):
    if word[-3:] == "ies":
        return word[:-3] + "y"
    elif word[-3:] in ["ses", "zes", "oes"] or word[-4:] in ["shes", "ches"]:
        return word[:-2]
    elif word[-1:] == "s" and word[-2:-1] != "s":
        return word[:-1]
    else:
        return word
