from ply import lex, yacc
from informClasses import *
import sys
import pickle



##### LEX RULES #####

tokens = ("THE", "THAT", "IF", "NOW", "SAY", "OF", "ROOM", "IS", "HAVE", "CONTAIN", "SUPPORT", "IN", "STRING", "WORD", "NUMBER", "PERIOD", "NEWLINE", "USUALLY", "BY", "AND", "FROM", "UNDERSTAND", "AS", "AFTER", "WHEN", "PLAY", "BEGINS", "EVERY", "TURN", "RBRACKET", "LBRACKET", "COLON", "SEMICOLON", "NOT", "MOVE", "REMOVE", "INSTEAD", "TO", "OR", "ISKINDOF", "ISIN", "HASSOMETEXTCALLED", "FOR")

reserved = {"a": "A", "an": "A", "the": "THE", "that": "THAT", "if": "IF", "now": "NOW", "say": "SAY", "of": "OF", "room": "ROOM", "rooms": "ROOM", "is": "IS", "are": "IS", "has": "HAVE", "contain": "CONTAIN", "contains": "CONTAIN", "contained": "CONTAIN", "containing": "CONTAIN", "support": "SUPPORT", "supports": "SUPPORT", "supported": "SUPPORT", "supporting": "SUPPORT", "in": "IN", "usually": "USUALLY", "by": "BY", "and": "AND", "from": "FROM", "understand": "UNDERSTAND", "as": "AS", "after": "AFTER", "when": "WHEN", "play": "PLAY", "begins": "BEGINS", "every": "EVERY", "turn": "TURN", "not": "NOT", "move": "MOVE", "remove": "REMOVE", "instead": "INSTEAD", "to": "TO", "or": "OR", "for": "FOR"}

numbers = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7, "eigth": 8, "ninth": 9, "tenth": 10, "eleventh": 11, "twelfth": 12, "thirteenth": 13, "fourteenth": 14, "fifteenth": 15, "sixteenth": 16, "seventeenth": 17, "eighteenth": 18, "nineteenth": 19, "twentieth": 20}

def t_HASSOMETEXTCALLED(t):
    r'has\ some\ text\ called'
    return t
def t_ISKINDOF(t):
    r'is\ a\ kind\ of|are\ kinds\ of'
    return t
def t_ISIN(t):
    r'(is|are)\ (in|on|contained\ by|supported\ by)'
    return t
def t_STRING(t):
    r'"[^"]*"'
    return t
def t_NUMBER(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t
def t_WORD(t):
    r'[^\.\ \t\n":;\[\]]+'
    t.value = t.value.lower()
    if t.value in numbers:
        t.type = "NUMBER"
        t.value = numbers[t.value]
    elif t.value in reserved:
        t.type = reserved[t.value]
    if t.type != "A":
        return t
t_PERIOD = r'\.'
t_NEWLINE = r'\n+'
t_COLON = r':'
t_SEMICOLON = r';'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_ignore_SPACE = r'[\ \t]+'



##### YACC RULES #####

def p_code(t):
    '''code : heading NEWLINE paragraphs
            | paragraphs'''
    pass

def p_paragraphs(t):
    '''paragraphs : paragraph NEWLINE paragraphs
                  | rule NEWLINE paragraphs
                  | paragraph NEWLINE
                  | rule'''
    pass

def p_heading(t):
    '''heading : STRING
               | STRING BY words'''
    global game
    game.title = t[1]
    if len(t) == 4:
        game.author = t[3]

def p_paragraph_sentence(t):
    '''paragraph : sentence paragraph
                 | sentence'''
    pass

def p_paragraph_string(t):
    '''paragraph : STRING paragraph
                 | STRING'''
    global game
    game.lastRoom.description = t[1]

def p_sentence(t):
    '''sentence : assertion PERIOD'''
    t[1]()

def p_assertion_kind(t):
    '''assertion : conjunction ISKINDOF words
                 | conjunction ISKINDOF words THAT IS conjunction
                 | conjunction ISKINDOF words THAT IS USUALLY conjunction'''
    names = t[1]
    parentName = t[3]
    if len(t) > 6:
        qualities = t[len(t)-1]
    else:
        qualities = []
    def f():
        global game
        parent = game.kinds[parentName]
        for name in names:
            kind = Kind(name, parent)
            if name in game.kinds:
                print "WARNING: Kind \"" + name + "\" defined more than once." 
            game.kinds[name] = kind
            game.kinds[name+'s'] = kind
            game.kinds[name+'es'] = kind
            for quality in qualities:
                kind.qualities[quality] = True
    t[0] = f

def p_assertion_isa(t):
    '''assertion : conjunction IS words'''
    thingNames = t[1]
    kindName = t[3]
    if len(thingNames) > 1:
        kindName = singular(kindName)
    def f():
        global game
        kind = game.kinds[kindName]
        for thingName in thingNames:
            if thingName in game.things:
                print "WARNING: Thing \""+thingName+"\" defined more than once."
            thing = Thing(kind)
            game.things[thingName] = thing
            thing.name = thingName
            thing.kind.lastReferenced = thing
    t[0] = f

def p_assertion_contained(t):
    '''assertion : things ISIN thingOrRoom
                 | things ISIN THE words OF thingOrRoom'''
    things = t[1]
    place = t[len(t)-1]
    def f():
        place.contents += things
        for thing in things:
            thing.location = place
    t[0] = f

def p_assertion_contains(t):
    '''assertion : thingOrRoom HAVE things
                 | thingOrRoom CONTAIN things
                 | thingOrRoom SUPPORT things'''
    place = t[1]
    things = t[3]
    def f():
        place.contents += things
        for thing in things:
            thing.location = place
    t[0] = f


def p_assertion_inis(t):
    '''assertion : IN thingOrRoom IS things'''
    place = t[2]
    thing = t[4]
    def f():
        place.contents += thing
    t[0] = f

def p_assertion_hasText(t):
    '''assertion : thing HASSOMETEXTCALLED words'''
    thing = t[1]
    quality = t[3]
    def f():
        global game
        if quality in thing.qualities:
            print "WARNING: \"" + quality + "\" defined more than once."
        thing.setQuality(quality, None)
    t[0] = f

def p_assertion_setQuality(t):
    '''assertion : THE words OF thing IS STRING
                 | THE words OF thing IS NUMBER
                 | THE words OF thing IS USUALLY STRING
                 | THE words OF thing IS USUALLY NUMBER'''
    quality = t[2]
    thing = t[4]
    value = t[len(t)-1]
    def f():
        thing.setQuality(quality, value)
    t[0] = f

def p_assertion_defineRoom(t):
    '''assertion : conjunction IS ROOM'''
    roomNames = t[1]
    def f():
        global game
        for roomName in roomNames:
            if roomName in game.rooms:
                print "WARNING: \"" + roomName + "\" is defined more than once."
            room = Room()
            room.name = roomName
            game.rooms[roomName] = room
            game.lastRoom = room
            if game.currentRoom == None:
                game.currentRoom = room
    t[0] = f

def p_assertion_relativeRoom(t):
    '''assertion : conjunction IS words FROM words'''
    thitherName = t[1][0]
    direction = t[3]
    thenceName = t[5]
    def f():
        global game
        if thitherName in game.rooms:
            thither = game.rooms[thitherName]
        else:
            thither = Room()
            thither.name = thitherName
            game.rooms[thitherName] = thither
        if thenceName in game.rooms:
            thence = game.rooms[thenceName]
        else:
            print "ERROR: \"" + thenceName + "\" was not understood."
            raise SystemExit
        if direction not in game.directions:
            print "ERROR: \"" + direction + "\" is not a direction."
        elif direction in thence.adjacent:
            print "ERROR: \""+thenceName+"\" may only have one thing \""\
                    +direction+"\" from it."
        else:
            thence.adjacent[direction] = thither
            thither.adjacent[game.directions[direction]] = thence
        game.lastRoom = thither
    t[0] = f

def p_assertion_understand(t):
    '''assertion : UNDERSTAND stringDisjunction AS words'''
    strings = t[2]
    words = t[4]
    def f():
        global game
        for string in strings:
            game.understand[string[1:-1]] = words
    t[0] = f

def p_rule_everyTurn(t):
    '''rule : EVERY TURN COLON statements
            | EVERY TURN COLON result'''
    global game
    game.everyTurn += t[len(t)-1]

def p_rule_beginning(t):
    '''rule : WHEN PLAY BEGINS COLON statements
            | WHEN PLAY BEGINS COLON result'''
    global game
    game.whenPlayBegins += t[4]

def p_rule_instead(t):
    '''rule : INSTEAD OF action COLON statements
            | INSTEAD OF action COLON result
            | INSTEAD OF action WHEN conditionDisjunction COLON statements
            | INSTEAD OF action WHEN conditionDisjunction COLON result'''
    global game
    statements = t[len(t)-1]
    if len(t) > 6:
        game.insteadRules[t[3]] = [t[5], statements]
    else:
        game.insteadRules[t[3]] = [lambda noun=None: True, statements]

def p_rule_after(t):
    '''rule : AFTER action COLON statements
            | AFTER action COLON result
            | AFTER action WHEN conditionDisjunction COLON statements
            | AFTER action WHEN conditionDisjunction COLON result'''
    global game
    action = t[2]
    statements = t[len(t)-1]
    if len(t) == 7:
        game.afterRules[action] = [t[4], statements]
    else:
        game.afterRules[action] = [lambda noun=None: True, statements]

def p_results(t):
    '''results : NEWLINE result SEMICOLON results
               | NEWLINE result SEMICOLON'''
    first = t[1]
    if len(t) == 5:
        second = t[4]
        def f(noun):
            first(noun)
            second(noun)
    else:
        def f(noun):
            first(noun)
    t[0] = f

def p_result_say(t):
    '''result : SAY STRING'''
    string = t[2]
    def f(noun=None):
        print string
    t[0] = f

def p_result_now(t):
    '''result : NOW assertion'''
    assertion = t[2]
    t[0] = lambda noun=None: assertion()

def p_result_move(t):
    '''result : MOVE thing TO thingOrRoom'''
    thing = t[2]
    place = t[4]
    def f(noun=None):
        if thing in thing.location.contents:
            thing.location.contents.remove(thing)
        thing.location = place
        place.contents.append(thing)
    t[0] = f

def p_result_remove(t):
    '''result : REMOVE thing FROM PLAY'''
    thing = t[2]
    def f(noun=None):
        global game
        if thing in game.things.values():
            for key in game.things:
                if game.things[key] == thing:
                    del game.things[key]
        if thing.location != None and thing in thing.location.contents:
            thing.location.contents.remove(thing)
    t[0] = f

def p_action(t):
    '''action : words'''
    t[0] = t[1]

def p_statements(t):
    '''statements : results conditionals
                  | results
                  | conditionals'''
    if len(t) == 4:
        first = t[1]
        second = t[3]
        def f(noun=None):
            first(noun)
            second(noun)
    else:
        statement = t[1]
        def f(noun=None):
            statement(noun)
    t[0] = f

def p_conditionals(t):
    '''conditionals : NEWLINE conditional conditionals
                    | NEWLINE conditional'''
    if len(t) == 3:
        first = t[1]
        second = t[2]
        def f(noun=None):
            first(noun)
            second(noun)
    else:
        statement = t[1]
        def f(noun=None):
            statement(noun)
    t[0] = f

def p_conditional(t):
    '''conditional : IF conditionDisjunction COLON result
                   | IF conditionDisjunction COLON results'''
    cond = t[2]
    results = t[len(t)-2]
    t[0] = lambda noun=None: results(noun) if cond(noun) else None

def p_conditionDisjunction(t):
    '''conditionDisjunction : conditionConjunction OR conditionDisjunction
                            | conditionConjunction'''
    if len(t) == 3:
        cond1 = t[1]
        cond2 = t[3]
        t[0] = lambda noun=None: cond1(noun) or cond2(noun)
    else:
        t[0] = t[1]

def p_conditionConjunction(t):
    '''conditionConjunction : condition AND conditionConjunction
                            | condition'''
    if len(t) == 3:
        cond1 = t[1]
        cond2 = t[3]
        t[0] = lambda noun=None: cond1(noun) and cond2(noun)
    else:
        t[0] = t[1]

def p_condition_inverse(t):
    '''condition : NOT condition'''
    condition = t[2]
    t[0] = lambda noun=None: not condition(noun)

def p_condition_booleanQuality(t):
    '''condition : conditionSubject IS words
                 | conditionSubject IS words FOR THE NUMBER TURN'''
    thing = t[1]
    quality = t[3]
    if len(t) == 3:
        def f(noun=None):
            thing = thing(noun)
            if quality not in thing.qualities:
                return False
            else:
                return thing.qualities[quality]
    else:
        turns = t[6]
        def f(noun=None):
            thing = thing(noun)
            if quality not in thing.qualities:
                return False
            elif not thing.qualities:
                return False
            else:
                global game
                return game.turn - thing.lastChanged[quality] == turns
    t[0] = f

def p_condition_quality(t):
    '''condition : THE words OF conditionSubject IS STRING
                 | THE words OF conditionSubject IS STRING FOR THE NUMBER TURN'''
    quality = t[2]
    thing = t[4]
    value = t[6]
    if len(t) == 7:
        def f(noun=None):
            thing = thing(noun)
            if quality not in thing.qualities:
                return False
            else:
                return thing.qualities[quality] == value
    else:
        turns = t[9]
        def f(noun=None):
            thing = thing(noun)
            if not (quality in thing.qualities):
                return False
            elif thing.qualities[quality] != value:
                return False
            else:
                global game
                return game.turn - thing.lastChanged[quality] == turns
    t[0] = f

def p_condition_contained(t):
    '''condition : conditionSubject ISIN conditionSubject'''
    thing = t[1]
    place = t[3]
    t[0] = lambda noun=None: thing.location == place

def p_condition_contains(t):
    '''condition : conditionSubject HAVE conditionSubject
                 | conditionSubject CONTAIN conditionSubject
                 | conditionSubject SUPPORT conditionSubject'''
    place = t[1]
    thing = t[3]
    t[0] = lambda noun=None: thing in place.contents

def p_conditionSubject(t):
    '''conditionSubject : thing
                        | LBRACKET words RBRACKET'''
    if len(t) == 2:
        thing = t[1]
        t[0] = lambda name=None: thing
    elif t[2] == "noun":
        t[0] = lambda noun: noun

def p_things(t):
    '''things : words
              | NUMBER words'''
    global game
    name = t[len(t)-1]
    if len(t) == 3:
        name = singular(name)
        number = t[1]
    else:
        number = 1
    if name in game.things:
        thing = game.things[name]
        thing.kind.lastReferenced = thing
        t[0] = [thing]
    else:
        if name in game.kinds:
            kind = game.kinds[name]
        else:
            kind = Kind(name, game.kinds["thing"])
            game.kinds[name] = kind
        things = [Thing(kind) for _ in xrange(number)]
        kind.lastReferenced = things[-1]
        t[0] = things

def p_thingOrRoom(t):
    '''thingOrRoom : words
                   | THE words'''
    global game
    name = t[len(t)-1]
    if name in game.rooms:
        thing = game.rooms[name]
    elif name in game.things:
        thing = game.things[name]
        thing.kind.lastReferenced = thing
    elif name in game.kinds:
        if len(t) == 2:
            thing = Thing(game.kinds[name])
            thing.kind.lastReferenced = thing
        else:
            thing = game.kinds[name].lastReferenced
            if thing == None:
                print "ERROR: \"The " + name + "\" was not understood."
                raise SystemExit
    else:
        print "ERROR: \"" + ' '.join(t[1:]) + "\" was not understood."
        raise SystemExit
    t[0] = thing

def p_conjuntion(t):
    '''conjunction : words AND conjunction
                   | words'''
    if len(t) == 2:
        t[0] = [t[1]]
    else:
        t[0] = [t[1]] + t[3]

def p_stringDisjunction(t):
    '''stringDisjunction : STRING OR stringDisjunction
                         | STRING'''
    if len(t) == 4:
        t[0] = [t[1]] + t[3]
    else:
        t[0] = [t[1]]

def p_words(t):
    '''words : WORD words
             | WORD'''
    if len(t) == 2:
        t[0] = t[1]
    else:
        t[0] = t[1] + ' ' + t[2]

def p_thing(t):
    '''thing : words
             | THE words'''
    global game
    name = t[len(t)-1]
    if name in game.things:
        thing = game.things[name]
        thing.kind.lastReferenced = thing
    elif name in game.kinds:
        if len(t) == 2:
            thing = game.kinds[name]
        else:
            thing = game.kinds[name].lastReferenced
            if t[0] == None:
                print "ERROR: \"" + ' '.join(t[1:]) + "\" was not understood."
                raise SystemExit
    else:
        print "ERROR: \"" + ' '.join(t[1:]) + "\" was not understood."
        raise SystemExit
    t[0] = thing



##### MAIN #####

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "ERROR: Must specify input source file and output game file"
        raise SystemExit

    inFile = open(sys.argv[1], 'r')
    outFile = open(sys.argv[2], 'w')

    lex.lex()
    yacc.yacc()
    game = Game()
    yacc.parse(inFile.read())
    pickle.dump(game, outFile)

    inFile.close()
    outFile.close()
