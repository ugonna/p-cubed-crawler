Product popularity prediction
=============================

A small test project that scrapes some parts of the web and searches Twitter for mentions of a product keyword. It
stores this data (**rather inefficiently**) and can later plot a historical trend for the popularity of the product, based
on mentions.

It was later expanded as an [academic endeavor](http://ugonna.co/download/ugo-ppp_public_report.pdf) with
sentiment-analysis (code not available here) to try and distinguish between negative and positive feedback/popularity for
trending products.

This code is written using the Python programming language (Python 2.7) and will only work on the
[Google App Engine](https://cloud.google.com/appengine/) platform as a web application.

**IMPORTANT:** This code will not work straight out of the box. It crawled specific web-pages with specific structures
and the chances are high that those page structures have changed since this code was written (within three weeks of May
2013). Furthermore, it uses Twitter API v1 which is now retired.

It is put here for reference and for posterity; I doubt I'll be making any updates to it seeing as it was a small
(successful) experiment.

Main modules
============

- main.py - The main entry point of the web application. Handle the presentation of the home page and all the other web pages
- process.py - Handles task queueing and dispatching.
- twitter - Handles Twitter search data retrieval
- scraper - Handles web page search, mining and scraping.
- _others_ - Utility scripts to handle various utility functionality

Libraries/tools used
====================

- [Beautiful Soup 4](http://www.crummy.com/software/BeautifulSoup/) for scraping the interwebs
- [gae-pytz](https://code.google.com/p/gae-pytz/) for help [with timezones](http://blog.ugonna.co/2014/04/watch-clock.html)
- [Flot Charts](http://www.flotcharts.org/) for plotting charts
- [Twitter Bootstrap](http://getbootstrap.com/) for UI framework

*******

Copyright 2013 Ugonna Nwakama
