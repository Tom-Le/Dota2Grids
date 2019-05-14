#!/usr/bin/env python

"""
Generate sorted grid layouts for Dota 2's pick screen, sorted by stats such as GPMs, XPMs, and last
hits @ 10 mins.
"""

from bs4 import BeautifulSoup
import urllib2, json

user_agent = 'Dota2GridBot9000'
"""
str: User agent string for HTTP requests.
"""

stat_sources = {
    'cs@10': ('http://www.dotabuff.com/heroes/farm', 2),      # Last hits @ 10 minutes
    'cd@10': ('http://www.dotabuff.com/heroes/farm', 3),      # Denies @ 10 minutes
    'gpm': ('http://www.dotabuff.com/heroes/economy', 2),     # Gold per minute
    'xpm': ('http://www.dotabuff.com/heroes/economy', 3),     # Experience per minute
    'kda': ('http://www.dotabuff.com/heroes/impact', 2),      # KDA ratio
    'wr': ('http://www.dotabuff.com/heroes/winning', 2),      # Win rate
    'pr': ('http://www.dotabuff.com/heroes/winning', 3),      # Pick rate
    'hdpm': ('http://www.dotabuff.com/heroes/damage', 2),     # Hero damage per minute
    'tdpm': ('http://www.dotabuff.com/heroes/damage', 3),     # Tower damage per minute
    'hhpm': ('http://www.dotabuff.com/heroes/damage', 4),     # Hero healing per minute
}
"""
dict: Sources (on Dotabuff) for stats.
    Each entry is a 2-tuple; first element is the URL, second element is the column index.
"""

class DotabuffStatsScraper:
    """
    Scrape and store stats from a page in Dotabuff's Heroes section.
    """

    NAME_COLUMN_INDEX = 1
    """
    int: Index of column for heroes' names.
    """

    def __init__(self, url, keys):
        """
        Scrape stats from given URL and store in new object.

        Args:
            url (str): URL of page to scrape from.
            keys (iter): Iterable of 2-tuples `(name, index)` to describe the data on the page.
                Each tuple `(name, index)` describes the name of the stats and the index of the
                column for the stats.

        Raises:
            urllib2.HTTPError: If HTTP request failed.
            ValueError: If we were unable to scrape data from page.
        """
        # Get page's content.
        request = urllib2.Request(url=url, headers={'User-Agent' : user_agent})
        response = urllib2.urlopen(request)
        document = BeautifulSoup(response, "lxml")

        # Find and import data.
        if document.table == None:
            raise ValueError("Unable to scrape data from page: Table not found.")

        # Iterate through each row in page's main table.
        self.stats = {}
        for row in document.table.tbody.find_all('tr'):
            data = {}

            # Scrape data from row.
            cols = row.find_all('td')
            try:
                # Get hero's name.
                hero_name = cols[self.NAME_COLUMN_INDEX].strings.next()
                # Get requested stats for heroes.
                for key_name, key_index in keys:
                    data[key_name] = cols[key_index]['data-value']
            except IndexError:
                raise ValueError("Unable to scrape data from page: Cannot read row.")

            # Store scraped data.
            self.stats[hero_name] = data

    def get_stats(self, hero, key):
        """
        Get stats for a hero.

        Args:
            hero (dict): Information of hero whose stats we are getting.
                This dict is expected to be in the following format::

                    {
                        'id' : 1,
                        'name' : 'npc_dota_hero_antimage',
                        'localized_name' : 'Anti-Mage',
                    }

            key (str): Name of stats to get.

        Returns:
            str: Stats for requested hero, or None if there's no stats for the hero or key
            specified.
        """
        # Find hero in list of stats.
        hero_name = hero['localized_name'];
        if hero_name in self.stats:
            if key in self.stats[hero_name]:
                return self.stats[hero_name][key]

        # Couldn't find hero or key. Return None.
        return None

def get_heroes_list(key):
    """
    Get up to date list of Dota 2 heroes from Steam's WebAPI.

    Args:
        key (str): Steam WebAPI key.

    Returns:
        list: List of dicts, each containing information about a hero.
            Each dict is in the following format::

                {
                    'id' : 1,
                    'name' : 'npc_dota_hero_antimage',
                    'localized_name' : 'Anti-Mage',
                }

    Raises:
        ValueError: If key is not a valid Steam WebAPI key.
        urllib2.HTTPError: If HTTP request failed not because key was invalid.
    """
    # Query Steam WebAPI for up to date list of Dota 2 heroes.
    qkey = urllib2.quote(key)
    request = urllib2.Request(url='http://api.steampowered.com/IEconDOTA2_570/GetHeroes/v0001/?language=en_us&key=' + qkey,
                              headers={'User-Agent' : user_agent})
    try:
        response = urllib2.urlopen(request)
    except urllib2.HTTPError as e:
        if e.code == 403:
            # Received 403 Forbidden. Key is invalid.
            raise ValueError("Key " + key + " was not accepted as a valid")
        else:
            # Just re-raise error.
            raise e

    # Read JSON response and return list of heroes.
    data = json.load(response)
    return data['result']['heroes']

def generate_grid(heroes, ratio='16:9'):
    """
    Generate grid layout from list of heroes.

    Args:
        heroes (list): List of dicts describing heroes.
            Each dict should be in the following format::

                {
                    'id' : 1,
                    'name' : 'npc_dota_hero_antimage',
                    'localized_name' : 'Anti-Mage',
                }

            The generated grid will match how this list is sorted. The first hero in the list is on
            the top left, while the last hero in the list is on the bottom right.
        ratio (optional, str): Screen's aspect ratio.
            Can be '4:3', '16:9', or '16:10'. Defaults to '16:9'.

    Returns:
        str: Sorted grid layout, serialized into text that can be saved to a text file to be
        imported in Dota 2.

    Raises:
        ValueError: If ratio is not 4:3, 16:9, or 16:10.
    """
    # Determine values for laying out grid based on aspect ratio.
    # TODO: Verify these values for 4:3 and 16:10.
    if ratio == '16:9':
        scale = 0.390228  # Grid icon's scale
        startXPos = 0  # Top left x-coordinate
        startYPos = 51 # Top left y-coordinate
        iconWidth = 51 # Icon's width
        iconHeight = 51 # Icon's height
        numCol = 19 # Number of columns
    elif ratio == '4:3':
        scale = 0.34848  # Grid icon's scale
        startXPos = 0  # Top left x-coordinate
        startYPos = 50 # Top left y-coordinate
        iconWidth = 55 # Icon's width
        iconHeight = 55 # Icon's height
        numCol = 20 # Number of columns
    elif ratio == '16:10':
        scale = 0.390228  # Grid icon's scale
        startXPos = 0  # Top left x-coordinate
        startYPos = 54 # Top left y-coordinate
        iconWidth = 54 # Icon's width
        iconHeight = 54 # Icon's height
        numCol = 20 # Number of columns
    else:
        raise ValueError("Invalid ratio.")

    # Generate layout.
    layout_lines = []
    layout_lines.append('"fulldeck_layout.txt"')
    layout_lines.append('{')

    # Iterate through each hero in sorted list of heroes.
    xPos, yPos = startXPos, startYPos  # x and y-coordinates of current iteration.
    col = 0 # Column of current iteration.
    for index, hero in enumerate(heroes):
        # Append layout info for current hero.
        layout_lines.append('\t"{}"'.format(index))
        layout_lines.append('\t{')

        layout_lines.append('\t\t"HeroID"\t"{}"'.format(hero['id']))
        layout_lines.append('\t\t"x"\t"{}"'.format(xPos))
        layout_lines.append('\t\t"y"\t"{}"'.format(yPos))
        layout_lines.append('\t\t"scale"\t"{}"'.format(scale))
        layout_lines.append('\t\t"zpos"\t"100"')

        layout_lines.append('\t}')

        # Change x and y-coordinates.
        col += 1
        if col > numCol:
            # Row has max. number of columns.
            # Move back to first column, but move down a row.
            xPos = startXPos
            yPos += iconHeight
            col = 0
        else:
            # Move to next column.
            xPos += iconWidth

    # Wrap up.
    layout_lines.append('}')
    return '\n'.join(layout_lines)

def main():
    """
    Script's main routine.
    """
    # Parse arguments.
    import argparse

    parser = argparse.ArgumentParser(description='Generate sorted grid layouts for Dota 2!')
    parser.add_argument('key',
                        help='Your Steam WebAPI key.')
    parser.add_argument('stat',
                        metavar='stat',
                        choices=stat_sources.keys(),
                        help='Stat to sort heroes. Choose from: %(choices)s.')
    parser.add_argument('out',
                        help='Path to output file.')
    parser.add_argument('--date',
                        default='month',
                        help='Date parameter to pass to Dotabuff.')
    parser.add_argument('--reverse',
                        action='store_false',
                        help='Sort from smallest to largest, instead of largest to smallest.')

    args = parser.parse_args()

    # Get up to date list of heroes.
    heroes = get_heroes_list(key=args.key)

    # Grab stats from user's chosen source.
    source = stat_sources[args.stat]
    url = source[0] + '?date=' + urllib2.quote(args.date)
    stat = args.stat
    column = source[1]
    buff = DotabuffStatsScraper(url=url, keys=[(args.stat, column)])

    # Generate sorted list of heroes.
    sheroes = sorted(heroes,
                     key=lambda hero: float(buff.get_stats(hero, args.stat)),
                     reverse=args.reverse)

    # Generate grid and write to output file.
    with open(args.out, 'w') as output_fp:
        output_fp.write(generate_grid(sheroes))

if __name__ == '__main__':
    main()
