Server-Eventi-Italia
====================

## Description
Server side of [Eventi-Italia app](https://github.com/Gabriele91/Client-Eventi-Italia) for Android. This project was made for an university exam and is designed for [the heroku platform](https://www.heroku.com/).

## Dependencies

All dependencies are written in requirements.txt and you can install them with:
```bash
pip install -r requirements.txt
```
## How to test

Just type the command below in the main directory:
```bash
honcho start
```
List of command supported:
* `http://localhost:5000/list` - list of all regions availables
* `http://localhost:5000/init` - reinitialize the db (also with POST, with `command` argument)
* `http://localhost:5000/update` - restart the update (also with POST, with `command` argument)
* `http://localhost:5000/start` - start the update (also with POST, with `command` argument)
* `http://localhost:5000/stop` - stop the update (also with POST, with `command` argument)
* `http://localhost:5000/region_name/list` - cities list from a region
* `http://localhost:5000/region_name/city_name` - get all news from a city

Support DELETE for city news, region news and the all database content.  
Support PUT for news, cities and regions.

## Authors

[Andrea](https://github.com/campo23)  
[Gabriele](https://github.com/Gabriele91)  
[Mirco](https://github.com/MircoT)

## License

The MIT License (MIT)

Copyright (C) 2013 Mirco Tracolli

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

