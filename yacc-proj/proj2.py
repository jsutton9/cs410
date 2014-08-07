from datetime import date
from ply import lex, yacc
import xml.etree.ElementTree as ET
import sys



##### LEX RULES #####

tokens = ("BORN", "TITLE", "SUFFIX", "PAPER", "DIED", "SONOF", "DAUGHTEROF", "AND", "MARRIED", "MARRIAGE", "HUSBAND", "WIFE", "LPAREN", "RPAREN", "PERIOD", "NEWLINE", "YEAR", "MONTH", "NUMBER", "WEEKDAY", "STATE", "INITIAL", "CAPITAL")

def t_HE(t):
    r'\ he\ |He\ '
    global person
    person.genderCount += 1
    pass
def t_SHE(t):
    r'\ she\ |She\ '
    global person
    person.genderCount -= 1
    pass
def t_BORN(t):
    r'[bB]orn'
    return t
def t_TITLE(t):
    r'Mrs?\.'
    return t
def t_SUFFIX(t):
    r'[JS]r\.'
    return t
def t_PAPER(t):
    r'Press|Times|Newspaper|Intermountain'
    return t
def t_NOTSPOUSE(t):
    r'and\ +(husband|wife)'
    pass
def t_MONTH(t):
    r'January|Jan\.|February|Feb\.|March|April|May|June|July|August|Aug\.|September|Sept\.|October|Oct\.|November|Nov\.|December|Dec\.'
    if t.value == "Jan.":
        t.value = "January"
    elif t.value == "Feb.":
        t.value = "February"
    elif t.value == "Aug.":
        t.value = "August"
    elif t.value == "Sept.":
        t.value = "September"
    elif t.value == "Oct.":
        t.value = "October"
    elif t.value == "Nov.":
        t.value = "November"
    elif t.value == "Dec.":
        t.value = "December"
    return t
def t_STATE(t):
    r'W\.\ ?Va\.|Va\.|D\.C\.'
    return t
def t_INITIAL(t):
    r'[A-Z]\.'
    return t
t_DIED = r'died|passed\ away|departed'
t_SONOF = r'son\ of'
t_DAUGHTEROF = r'daughter\ of'
t_AND = r'and'
t_MARRIED = r'married'
t_MARRIAGE = r'marriage'
t_HUSBAND = r'husband'
t_WIFE = r'wife'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_PERIOD = r'\.|-|;|:'
t_NEWLINE = r'\n+'
t_YEAR = r'[1-2][0-9][0-9][0-9]'
t_NUMBER = r'[0-9]+'
t_WEEKDAY = r'Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday'
t_CAPITAL = r'St\.|Ft\.|"?[A-Z]([a-zA-Z]|\xe2\x80\x99)*"?'
t_ignore_OTHER = r'.'



##### ADDITIONAL CODE #####

class Person:
    def __init__(self):
        self.name = None
        self.gender = None
        self.parents = None
        self.birthDate = None
        self.birthDateApprox = False
        self.birthPlace = None

        self.spouse = None
        self.marriageDate = None
        self.marriageDateApprox = False
        self.marriagePlace = None

        self.deathDate = None
        self.deathPlace = None

        self.reference = None

        self.publicationDate = None
        self.age = None
        self.deathWeekday = None
        self.marriageDuration = None
        self.genderCount = 0

    def obit(self):
        if self.deathDate == None and self.publicationDate != None and \
          self.deathWeekday != None:
            self.deathDate = relativeDate(self.publicationDate, self.deathWeekday)
        if self.deathDate != None and self.deathDate[2] == None and \
          self.publicationDate != None:
            self.deathDate[2] = self.publicationDate[2]
        if self.birthDate == None and self.deathDate != None and \
          self.deathDate[2] != None and self.age != None:
            self.birthDate = [None, None, \
              str(int(self.deathDate[2])-int(self.age))]
            self.birthDateApprox = True
        if self.birthDate != None and self.birthDate[2] != None and \
          self.deathDate != None and self.deathDate[2] == None and \
          self.age != None:
            self.deathDate[2] = str(int(self.birthDate[2])+int(self.age))
            self.deathDateApprox = True
        if self.marriageDate == None and self.deathDate != None and \
          self.deathDate[2] != None and self.marriageDuration != None:
            self.marriageDate = [None, None, 
              str(int(self.deathDate[2])-int(self.marriageDuration))]
            self.marriageDateApprox = True
        if self.gender == None and self.genderCount != 0:
            if self.genderCount > 0:
                self.gender = 'M'
            else:
                self.gender = 'F'

        ret = ""
        if self.name != None:
            ret += self.name
        if self.parents != None:
            if self.gender == 'M':
                ret += ", son of "
            elif self.gender == 'F':
                ret += ", daughter of "
            else:
                ret += ", child of "
            ret += self.parents + ","
        ret += " was born"
        if self.birthDate != None:
            if self.birthDateApprox:
                ret += " about"
            ret += " " + dateString(self.birthDate)
        if self.birthPlace != None:
            ret += " at " + self.birthPlace
        ret += ". "

        if self.spouse != None:
            if self.gender == 'M':
                ret += "He married " + self.spouse
            elif self.gender == 'F':
                ret += "She married " + self.spouse
            else:
                ret += "He/She married " + self.spouse
            if self.marriageDate != None:
                if self.marriageDateApprox:
                    ret += " about"
                ret += " " + dateString(self.marriageDate)
            if self.marriagePlace != None:
                ret += " at " + self.marriagePlace
            ret += ". "

        if self.gender == 'M':
            ret += "He died"
        elif self.gender == 'F':
            ret += "She died"
        else:
            ret += "He/She died"
        if self.deathDate != None:
            ret += " " + dateString(self.deathDate)
        if self.deathPlace != None:
            ret += " at " + self.deathPlace
        ret += "."

        if self.reference != None:
            ret += " Reference: " + self.reference + "."

        return ret

towns = {"Benbush": "Tucker", "Brownsville": "Cameron", "Brushy Run": "Pendleton", "Cabins": "Grant", "Clarksburg": "Harrison", "Cumberland": "Allegany", "Flintstone": "Allegany", "Fort Seybert": "Pendleton", "Gormania": "Grant", "Harman": "Randolph", "Kearneysville": "Jefferson", "Landes": "Grant", "Petersburg": "Grant", "Seoul": "South Korea", "Washington": "District of Columbia", "Weirton": "Hancock", "Wellsburg": "Brooks", "West Jefferson": "Madison", "Winchester": "Frederick"}

counties = {"Allegany": "Maryland", "Brooks": "West Virginia", "Cameron": "Texas", "Frederick": "Virginia", "Grant": "West Virginia", "Hancock": "West Virginia", "Harrison": "West Virginia", "Jefferson": "West Virginia", "Madison": "Ohio", "Pendleton": "West Virginia", "Randolph": "West Virginia", "Tucker": "West Virginia"}

monthNumbers = {"January":1, "February":2, "March":3, "April":4, \
                "May":5, "June":6, "July":7, "August":8, \
                "September":9, "October":10, "November":11, \
                "December":12}

def dateString(date):
    if date[1] == None:
        return date[2]
    elif date[2] == None:
        return date[0] + ' ' + date[1]
    else:
        return date[0] + ' ' + date[1] + ' ' + date[2]

def relativeDate(pubDate, weekday):
    monthNames = {n:m for m, n in monthNumbers.items()}
    weekdayNumbers = {"Monday":0, "Tuesday":1, "Wednesday":2, \
                      "Thursday":3, "Friday":4, "Saturday":5, \
                      "Sunday":6}
    ref = date(int(pubDate[2]), monthNumbers[pubDate[1]], int(pubDate[0]))
    delta = (ref.weekday() - weekdayNumbers[weekday]) % 7
    ret = date.fromordinal(ref.toordinal() - delta)
    return [str(ret.day), monthNames[ret.month], str(ret.year)]

def relativeYear(bDate, dDate, age):
    dYear = bDate[2] + age
    bMonth = monthNumbers[bDate[1]]
    dMonth = monthNumbres[dDate[1]]
    if dMonth < bMonth or dMonth == bMonth and int(dDate[0]) < int(bDate[0]):
        dYear += 1
    return [dDate[0], dDate[1], dYear] 
def clarifyPlace(placeString):
    words = placeString.split()
    for word in words:
        if word in towns:
            county = towns[word]
            if county in counties:
                return word + ", " + county + " County, " + counties[county]
            else:
                return word + ", " + county
    for i in xrange(len(words)-1):
        pair = words[i] + ' ' + words[i+1]
        if pair in towns:
            return pair+", "+towns[pair]+" County, "+counties[towns[pair]]
    return placeString



##### YACC RULES #####

def p_obituary(t):
    '''obituary : sentence obituary
                | sentence'''
    pass

def p_sentence(t):
    '''sentence : referenceSentence
                | publicationDateSentence
                | birthSentence
                | deathSentence
                | spouseSentence'''
    pass


def p_name(t):
    '''name : CAPITAL subname
            | INITIAL subname
            | CAPITAL subname SUFFIX'''
    t[0] = t[1] + ' ' + t[2]
    if len(t) == 4:
        t[0] += ' ' + t[3]
def p_name_title(t):
    '''name : TITLE name'''
    t[0] = t[2]

def p_subname(t):
    '''subname : CAPITAL
               | CAPITAL subname
               | nee subname
               | INITIAL subname'''
    t[0] = t[1]
    if len(t) == 3:
        t[0] += ' ' + t[2]

def p_nee(t):
    '''nee : LPAREN CAPITAL RPAREN'''
    t[0] = '(' + t[2] + ')'

def p_names(t):
    '''names : name AND name
             | CAPITAL AND name
             | CAPITAL INITIAL AND name
             | CAPITAL INITIAL SUFFIX AND name'''
    t[0] = t[1] + ' ' + t[2] + ' ' + t[3]
    if len(t) > 4:
        t[0] += ' ' + t[4]
        if len(t) > 5:
            t[0] += ' ' + t[5]


def p_date_weekday(t):
    '''date : WEEKDAY date'''
    t[0] = t[2]
def p_date_partial(t):
    '''date : NUMBER MONTH'''
    t[0] = [t[1], t[2], None]
def p_date_partialBackwards(t):
    '''date : MONTH NUMBER'''
    t[0] = [t[2], t[1], None]
def p_date(t):
    '''date : NUMBER MONTH YEAR'''
    t[0] = [t[1], t[2], t[3]]
def p_date_backwards(t):
    '''date : MONTH NUMBER YEAR'''
    t[0] = [t[2], t[1], t[3]]


def p_referenceSentence_reference(t):
    '''referenceSentence : reference PERIOD
                         | reference NEWLINE'''
    pass
def p_referenceSentence_referenceDate(t):
    '''referenceSentence : reference date PERIOD
                         | reference date NEWLINE'''
    global person
    person.publicationDate = t[2]
def p_referenceSentence_dateReference(t):
    '''referenceSentence : date reference NEWLINE'''
    global person
    person.publicationDate = t[1]
def p_referenceSentence_miscellany(t):
    '''referenceSentence : reference miscellany date NEWLINE'''
    global person
    person.publicationDate = t[3]

def p_miscellany(t):
    '''miscellany : CAPITAL NUMBER NUMBER'''
    pass

def p_reference(t):
    '''reference : CAPITAL PAPER
                 | CAPITAL reference'''
    t[0] = t[1] + ' ' + t[2]
    global person
    person.reference = t[0]

def p_publicationDateSentence(t):
    '''publicationDateSentence : date NEWLINE'''
    global person
    person.publicationDate = t[1]


def p_place(t):
    '''place : CAPITAL place'''
    t[0] = t[1] + ' ' + t[2]
def p_place_last(t):
    '''place : CAPITAL
             | STATE'''
    t[0] = t[1]


def p_deathSentence(t):
    '''deathSentence : death PERIOD
                     | death NEWLINE
                     | deathIntro death'''
    pass

def p_deathIntro(t):
    '''deathIntro : CAPITAL deathIntro
                  | TITLE'''
    pass

def p_death(t):
    '''death : name deathPhrase DIED deathPredicate
             | name DIED deathPredicate'''
    global person
    person.name = t[1]

def p_deathPhrase_age(t):
    '''deathPhrase : NUMBER'''
    global person
    person.age = int(t[1])
def p_deathPhrase_place(t):
    '''deathPhrase : NUMBER place'''
    global person
    person.age = int(t[1])
    person.deathPlace = clarifyPlace(t[2])
def p_deathPhrase_address(t):
    '''deathPhrase : NUMBER NUMBER place'''
    global person
    person.age = int(t[1])
    person.deathPlace = clarifyPlace(t[3])

def p_deathPredicate_placeWeekday(t):
    '''deathPredicate : place WEEKDAY'''
    global person
    person.deathPlace = clarifyPlace(t[1])
    person.deathWeekday = t[2]
def p_deathPredicate_datePlace(t):
    '''deathPredicate : date place'''
    global person
    person.deathDate = t[1]
    person.deathPlace = clarifyPlace(t[2])
def p_deathPredicate_date(t):
    '''deathPredicate : date'''
    global person
    person.deathDate = t[1]
def p_deathPredicate_weekdayPlace(t):
    '''deathPredicate : WEEKDAY place'''
    global person
    person.deathWeekday = t[1]
    person.deathPlace = clarifyPlace(t[2])


def p_birthSentence(t):
    '''birthSentence : birth PERIOD
                     | birth NEWLINE
                     | CAPITAL birth PERIOD'''
    pass
def p_birthSentence_suffix(t):
    '''birthSentence : birth SUFFIX'''
    global person
    person.parents += ' '+t[2]

def p_birth(t):
    '''birth : BORN date place names
             | BORN date place SONOF names
             | BORN date place DAUGHTEROF names'''
    global person
    person.birthDate = t[2]
    person.birthPlace = clarifyPlace(t[3])
    if len(t) == 5:
        person.parents = t[4]
    else:
        person.parents = t[5]
        if t[4] == "son of":
            person.gender = 'M'
        else:
            person.gender = 'F'


def p_spouseSentence(t):
    '''spouseSentence : spouse spouseSentenceEnd
                      | CAPITAL spouse spouseSentenceEnd
                      | CAPITAL CAPITAL spouse spouseSentenceEnd
                      | TITLE CAPITAL spouse spouseSentenceEnd'''
    pass

def p_spouseSentenceEnd(t):
    '''spouseSentenceEnd : CAPITAL spouseSentenceEnd
                         | AND spouseSentenceEnd
                         | HUSBAND spouseSentenceEnd
                         | BORN spouseSentenceEnd
                         | PERIOD'''
    pass

def p_spouse_husbandName(t):
    '''spouse : HUSBAND name
              | HUSBAND name date'''
    global person
    person.spouse = t[2]
    person.gender = 'F'
def p_spouse_husbandNameDuration(t):
    '''spouse : HUSBAND name NUMBER'''
    global person
    person.spouse = t[2]
    person.marriageDuration = t[3]
    person.gender = 'F'
def p_spouse_husbandNameDate(t):
    '''spouse : HUSBAND name MARRIED date'''
    global person
    person.spouse = t[2]
    person.marriageDate = t[4]
    person.gender = 'F'
def p_spouse_two(t):
    '''spouse : HUSBAND name AND name'''
    global person
    person.spouse = t[2] + ' and ' + t[4]
    person.gender = 'F'
def p_spouse_wifeName(t):
    '''spouse : WIFE name'''
    global person
    if person.spouse != None:
        person.spouse += ' and ' + t[2]
    else:
        person.spouse = t[2]
    person.gender = 'M'
def p_spouse_wifeDurationName(t):
    '''spouse : WIFE NUMBER name'''
    global person
    person.marriageDuration = t[2]
    person.spouse = t[3]
    person.gender = 'M'
def p_spouse_wifeNameDatePlace(t):
    '''spouse : WIFE name MARRIED date place'''
    global person
    person.spouse = t[2]
    person.marriageDate = t[4]
    person.marriagePlace = clarifyPlace(t[5])
    person.gender = 'M'
def p_spouse_marriageName(t):
    '''spouse : MARRIAGE name'''
    global person
    if person.spouse == None:
        person.spouse = t[2]
def p_spouse_yearName(t):
    '''spouse : YEAR MARRIED name'''
    global person
    person.marriageDate = [None, None, t[1]]
    person.spouse = t[3]


def p_error(t):
    pass



##### MAIN #####

def getPages(tree):
    for child in tree.getroot():
        if child.tag[-4:] == "body":
            body = child
            break
    lineElements = []
    for child in body:
        if child.tag[-1] == 'p':
            lineElements.append(child)
    pages = []
    page = ""
    keyVal = "{http://schemas.microsoft.com/office/word/2003/wordml}val"
    newPage = {"P14", "P15", "P16", "P17", "P18", \
               "P19", "P22", "P25", "P26"}
    for line in lineElements:
        for child in line:
            if child.tag[-2:] == "Pr":
                if child[0].attrib[keyVal] in newPage and page != "":
                    pages.append(page)
                    page = ""
                else:
                    page += '\n'
            elif child.tag[-1] == 'r':
                for grandChild in child:
                    if grandChild.tag[-1] == 't' and \
                            grandChild.text != None:
                        page += grandChild.text
    if page != "":
        pages.append(page)
    return pages

if __name__ == "__main__":
    lex.lex()
    yacc.yacc()
    for arg in sys.argv[1:]:
        if arg[-4:] == ".txt":
            person = Person()
            f = open(arg, 'r')
            yacc.parse(f.read())
            f.close()
            print person.obit()
            print ""
        elif arg[-4:] == ".xml":
            pages = getPages(ET.parse(arg))
            for page in pages:
                person = Person()
                yacc.parse(page)
                print person.obit()
                print ""
