⚠️ This is no longer usable after Dota 2 Reborn :(

Grid layout generator
=====================

Generate sorted grid layouts using the most up-to-date stats!

Requirements
------------

  - [A Steam WebAPI key](https://steamcommunity.com/dev/apikey).
  - Python 2.7+
  - [Beautiful Soup 4](http://www.crummy.com/software/BeautifulSoup/). Install
      with pip: `pip install beautifulsoup4`.
  - Optionally [lxml](http://lxml.de). Install with pip: `pip install lxml`.

Though you can ignore these requirements if you just want to use the layout
files included in this repository! Simply copy them to `<steamapps>/common/dota
2 beta/game/dota/cfg/layouts/`, open Dota 2, start a bot game, then import one
of the layouts while in grid view.

Usage
-----

    python generate-grid.py [-h] [--date DATE] [--reverse] key stat out

For help, run `python generate-grid.py -h`.

Valid `--date` values:

   - `month` for stats from this month.
   - `3month` for stats from the last 3 months.
   - `6month` for stats from the last 6 months.
   - `year` for stats from the last year or 12 months.
   - `''` (an empty string) for all-time stats.
   - And a few more that changes from time to time e.g. `patch_6.85b`.

Valid `stat` values:

   - `pr`: Pick rate.
   - `wr`: Win rate.
   - `kda`: KDA ratio.
   - `gpm`: Gold per minute.
   - `xpm`: Experience per minute.
   - `cs@10`: Last hits @ 10 minutes.
   - `cd@10`: Denies @ 10 minutes.
   - `hdpm`: Hero damage per minute.
   - `tdpm`: Tower damage per minute.
   - `hhpm`: Hero healing per minute.

Acknowledgements
----------------

  - Dotabuff for making these stats available. I had to resort to screen
      scraping because I couldn't find a suitable API. Sorry!
  - Valve and Icefrog for making millions of kids addicted to Dota 2 and hats.
