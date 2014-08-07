import sys
import pickle
from ply import lex, yacc
from informClasses import *



##### LEX RULES #####

tokens = ("GO", "TAKE", "EAT", "INSPECT", "TO", "WORD", "DIRECTION", "NUMBER", "LOOK", "QUIT", "AT", "INVENTORY", "DROP")

reserved = {"go": "GO", "take": "TAKE", "eat": "EAT", "inspect": "INSPECT", "to": "TO", "the": "ARTICLE", "a": "ARTICLE", "an": "ARTICLE", "look": "LOOK", "quit": "QUIT", "at": "AT", "inventory": "INVENTORY", "drop": "DROP"}

numbers = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20}

def t_NUMBER(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

def t_WORD(t):
    r'[^\ \t\n]+'
    t.value = t.value.lower()
    if t.value in reserved:
        t.type = reserved[t.value]
    elif t.value in numbers:
        t.type = "NUMBER"
        t.value = numbers[t.value]
    elif t.value in game.directions:
        t.type = "DIRECTION"
    if t.type == "ARTICLE":
        return
    return t

t_ignore_SPACE = r'[ \t]+'



##### YACC RULES #####

def p_command_go(t):
    '''command : GO DIRECTION'''
    if t[2] in game.currentRoom.adjacent:
        game.currentRoom = game.currentRoom.adjacent[t[2]]
        print game.currentRoom.describe()
    else:
        print "You cannot go that way."

def p_command_direction(t):
    '''command : DIRECTION'''
    if t[1] in game.currentRoom.adjacent:
        game.currentRoom = game.currentRoom.adjacent[t[1]]
        print game.currentRoom.describe()
    else:
        print "You cannot go that way."

def p_command_goto(t):
    '''command : GO TO words'''
    roomName = t[len(t)-1]
    if roomName in game.understand:
        roomName = game.understand[roomName]
    adjacent = game.currentRoom.adjacent
    if roomName not in game.rooms:
        print "There is no such room."
    else:
        moved = False
        for direction in adjacent:
            if adjacent[direction].name == roomName:
                game.currentRoom = adjacent[direction]
                print game.currentRoom.describe()
                moved = True
                break
        if not moved:
            print "You cannot go there from here."

def p_command_take(t):
    '''command : TAKE words'''
    words = t[len(t)-1]
    if words in game.understand:
        words = game.understand[words]
    thing = game.currentRoom.getThing(words)
    if thing != None:
        game.currentRoom.contents.remove(thing)
        game.inventory.append(thing)
        print "Taken."
    else:
        sing = singular(words)
        thing = game.currentRoom.getThing(sing)
        count = 0
        while thing != None:
            game.currentRoom.contents.remove(thing)
            game.inventory.append(thing)
            thing = game.currentRoom.getThing(sing)
            count += 1
        if count == 0:
            print "There is no " + words + "."
        else:
            print "Took " + str(count) + "."

def p_command_takeNumber(t):
    '''command : TAKE NUMBER words'''
    words = t[3]
    number = t[2]
    if words in game.understand:
        words = game.understand[words]
    if number != 1:
        words = singular(words)
    count = 0
    thing = game.currentRoom.getThing(words)
    while thing != None and count < number:
        game.currentRoom.contents.remove(thing)
        game.inventory.append(thing)
        thing = game.currentRoom.getThing(words)
        count += 1
    if count == 0:
        print "There are no " + plural(words) + "."
    elif count == number:
        print "Taken."
    else:
        print "You could only take " + str(count) + "."

def p_command_drop(t):
    '''command : DROP words'''
    words = t[len(t)-1]
    if words in game.understand:
        words = game.understand[words]
    count = 0
    flag = False
    for thing in game.inventory:
        if thing.name==words or thing.name==None and thing.kind.name==words:
            game.inventory.remove(thing)
            game.currentRoom.contents.append(thing)
            print "Dropped."
            flag = True
            break
    if not flag:
        sing = singular(words)
        count = 0
        dropped = []
        for thing in game.inventory:
            if thing.name==sing or thing.name==None and thing.kind.name==sing:
                dropped.append(thing)
                game.currentRoom.contents.append(thing)
                count += 1
        for thing in dropped:
            game.inventory.remove(thing)
        if count != 0:
            print "Dropped " + str(count) + "."
        else:
            print "You have no " + words + "."

def p_command_dropNumber(t):
    '''command : DROP NUMBER words'''
    number = int(t[2])
    words = t[3]
    if words in game.understand:
        words = game.understand[words]
    if number != 0:
        words = singular(words)
    count = 0
    dropped = []
    for thing in game.inventory:
        if thing.name==words or thing.name==None and thing.kind.name==words:
            dropped.append(thing)
            game.currentRoom.contents.append(thing)
            count += 1
            if count == number:
                break
    for thing in dropped:
        game.inventory.remove(thing)
    if count == 0:
        print "You have no " + plural(words) + "."
    elif count == number:
        print "Dropped."
    else:
        print "You could only drop " + str(count) + "."

def p_command_eat(t):
    '''command : EAT words'''
    words = t[len(t)-1]
    if words in game.understand:
        words = game.understand[words]
    flag = False
    for thing in game.inventory:
        if thing.name==words or thing.name==None and thing.kind.name==words:
            if "edible" in thing.qualities and thing.qualities["edible"]:
                game.inventory.remove(thing)
                print "Eaten."
            else:
                print "That is not edible."
            flag = True
            break
    if not flag:
        thing = game.currentRoom.getThing(words)
        if thing != None and (thing.name==words or \
                thing.name==None and thing.kind.name==words):
            if "edible" in thing.qualities and thing.qualities["edible"]:
                game.currentRoom.contents.remove(thing)
                print "Eaten."
            else:
                print "That is not edible."
            flag = True
    if not flag:
        print "You do not have that."

def p_command_look(t):
    '''command : LOOK'''
    print game.currentRoom.describe()

def p_command_quit(t):
    '''command : QUIT'''
    raise SystemExit

def p_command_inspect(t):
    '''command : INSPECT words
               | LOOK AT words'''
    words = t[2]
    if words in game.understand:
        words = game.understand[words]
    flag = False
    for thing in game.inventory:
        if thing.name==words or thing.name==None and thing.kind.name==words:
            print thing.describe()
            flag = True
            break
    if not flag:
        thing = game.currentRoom.getThing(words)
        if thing != None:
            print thing.describe()
        else:
            print "There is no " + words + "."

def p_command_inventory(t):
    '''command : INVENTORY'''
    named = []
    unnamed = {}
    for thing in game.inventory:
        if thing.name != None:
            named.append(thing.name)
        else:
            if thing.kind.name in unnamed:
                unnamed[thing.kind.name] += 1
            else:
                unnamed[thing.kind.name] = 1
    for name in named:
        print name
    for name in unnamed:
        if unnamed[name] == 1:
            if name[0] in ['a', 'e', 'i', 'o', 'u']:
                print "an " + name
            else:
                print "a " + name
        else:
            print str(unnamed[name])+ ' ' + plural(name)

def p_words(t):
    '''words : WORD words
             | WORD'''
    if len(t) == 3:
        t[0] = t[1] + " " + t[2]
    else:
        t[0] = t[1]



##### MAIN #####

if __name__ == "__main__":
    lex.lex()
    yacc.yacc()

    rules = False
    fileName = None
    for arg in sys.argv[1:]:
        if arg == "-r" or arg == "--rules":
            rules = True
        else:
            fileName = arg

    if fileName == None:
        print "ERROR: Must specify game file as argument"
        raise SystemExit

    f = open(fileName, 'r')
    game = pickle.load(f)

    if rules:
        kuriteru = game.things["kuriteru"]

        def sayColor(noun):
            print "You are now the color " + kuriteru.qualities["color"] + "."

        def everyTurn():
            if kuriteru.qualities["color"] == "pale green":
                if game.turn == kuriteru.lastChanged["color"] + 4:
                    kuriteru.setQuality("color", "purple", game.turn)
                    print "You are now the color purple."
                elif game.turn == kuriteru.lastChanged["color"] + 2:
                    print "You feel queasy."

        def eatAsparagus(noun):
            print "You eat the yucky asparagus."
            kuriteru.setQuality("color", "pale green", game.turn)
            print "You are now the color pale green."
    
        game.everyTurn.append(everyTurn)
        game.afterRules["eat asparagus"] = eatAsparagus

    for rule in game.whenPlayBegins:
        rule()
    print game.currentRoom.describe()
    while True:
        words = raw_input("\n> ").split(' ')
        if words[0] in game.understand:
            words[0] = game.understand[words[0]]
        command = ' '.join(words)
        noun = ' '.join(words[1:])
        if command in game.insteadRules:
            game.instead(command)(noun)
        else:
            yacc.parse(command)
            if command in game.afterRules:
                game.afterRules[command](noun)
        for rule in game.everyTurn:
            rule()
        game.turn += 1
