## What is it?


Big gun for little flyes

Just playing a bit with [RethinkDb](https://github.com/rethinkdb/rethinkdb), Python and [Node.js](http://nodejs.org/) (Warum nicht?! :) )

## What is it about?


Skyrim is a videogame by Bethesda. There is a special skill in it called alchemy which allows to produce potions and poisons by mixing different ingredients. Here is script for calculating these recipes.

### Data

JSON data compiled from [this source](http://skyrim.melian.cc/?cmd=cmdSkyrimIngredientList) using script-magic. But on November,4 there were some errors in the list on site, so here is corrected version of it

### Python

Python script understands -h or --help key. Also you may print 'help' or 'h' while it's running.

Ingredients' names and effects may be painted in different ways. To use it you need [ansicolors](https://github.com/verigak/colors) library. To change colors or logic change config src/python/config.json

### Node.js

JS-server starts its work by launching index.js and listens to 8888 port on localhost. There is no ~~hope~~ help for it
