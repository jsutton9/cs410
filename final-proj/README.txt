Summary

This project implements a subset of Inform 7. It is written in Python 2.7 and consists of three files: informClasses.py, informCompile.py, and informPlay.py, which must all be in the same directory. These also depend on the PLY (Python lex and yacc) package. The informCompile.py program converts the inform source into objects of the classes defined in informClasses.py, which are serialized and written to a file using Python's pickle module. The informPlay.py program may then be run with that file to play the game.

usage:
$ python informCompile.py game.i7 game
$ python informPlay.py game [-r]
where game.i7 is the source file, game contains the compiled game data and -r (or --rules) is an option to include some rules in the game, further detailed below.



Compilation

The following forms in the source file can be parsed by the compiler:
defining kinds:
	A scimitar is a kind of sword that is usually sharp.
	Strawberry and asparagus and gouda cheese are kinds of food.
defining things:
	Kuriteru is a person.
	Genghis Khan and Claudius Caesar are persons.
containment/possession:
	An asparagus is in the Vegetable Patch.
	Kuriteru has a cookie.
	The backpack contains 3 coats.
	In the berry patch are 25 strawberries.
	The desk supports a book.
defining properties:
	Kuriteru has some text called color.
setting properties:
	The color of Kuriteru is purple.
	The mass of a strawberry is usually 20.
defining rooms:
	Kuriteru's Yard is a room.
	Vegetable Patch and Kuriteru's Treehouse are rooms.
specifying relative room locations:
	Ten Forward is north from deck ten.
	The Labyrinth is down from Knossos.
"understand" statements:
	Understand "tree" or "trunk" as large tree trunk.
A string in quotation marks that is not part of a sentence is assigned as the description of the last defined room.
Although code is included to deal with rules, the parser will not properly parse them.

To compile a source file, run informCompile.py with the source file followed by a target file to which to write the game data as command line arguments.



Playing

To play a game, run informPlay.py with the game file written to by informCompile.py as a command line argument.

Because the compiler cannot properly parse rules, there are some rules which can be added to the game by informCompile.py by supplying the -r (or --rules) flag as a command line argument as a demonstration of rules working with the rest of the code. This will make the color of Kuriteru purple, changing as specified by the rules in the lecture slides.

When playing a game, commands of the following forms can be interpreted:
take:
	take asparagus
	take the tree
	take strawberries (this takes all available strawberries)
	take the asparaguses
	take 13 strawberries
drop:
	drop asparagus
	drop the tree
	drop a strawberry
	drop strawberries
	drop the asparaguses
	drop eight strawberries
movement:
	go south
	go down
	east
	up
	go to Kuriteru's Yard
	go to the vegetable patch
eat:
	eat strawberry
	eat the asparagus
	eat an asparagus
inspect room:
	look
	l
inspect object:
	inspect tree
	inspect a strawberry
	look at the asparagus
view inventory:
	inventory
	i
quit:
	quit
	q
