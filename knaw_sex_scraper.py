from bs4 import BeautifulSoup
import pandas as pd
import requests

def get_soup(name):
    # Get souped html from meertens.knaw.nl from given name
    naam_url = 'http://www.meertens.knaw.nl/nvb/populariteit/naam/{}'
    
    current_url = naam_url.format(name)
    html = requests.get(current_url) \
                   .text
    soup = BeautifulSoup(html, "html5lib")
    return soup

def get_tbody(soup):
    # Find the tbody of the nameinfo table
    table = soup.find('table', attrs={'class': 'nameinfo'})
    tbody = table.tbody
    return tbody

def get_row(tbody, index):
    # Find a row in a tbody
    row = tbody.findAll('tr')[index]
    return row
    
def get_col(tr, index):
    # Find a col in a tr
    col = tr.findAll('td')[index]
    return col

def to_int(cell):
    # Cast string to int, replaces -- with 0
    content = cell.get_text() \
                  .replace('--', '0') \
                  .replace('< 5', '5')
    nr = int(content)
    return nr

def get_cell_value(tbody, row_index, col_index):
    # Get int value from given coordinates in tbody
    row = get_row(tbody, row_index)
    cell = get_col(row, col_index)
    nr = to_int(cell)
    return nr

def get_sex_and_chance(name):
    # Returns a tuple: string, float where string is in 'boy', 'girl', 'onbekend' and 0 <= float <= 1
    soup = get_soup(name)
    
    # Get the cell value for boys and girls
    try:
        tbody = get_tbody(soup)
        boys = get_cell_value(tbody, 1, 2)
        girls = get_cell_value(tbody, 5, 2)
    except AttributeError:
        return 'onbekend', 0

    # Get a chance of boy and girl
    try:
        p_boy = boys / (boys+girls)
        p_girl = 1 - p_boy
    except ZeroDivisionError:
        return 'onbekend', 0

    # Return most likely class and chance
    if p_boy > p_girl:
        return 'boy', p_boy
    else:
        return 'girl', p_girl     
    
name = 'maxime'
"{} - {} - {:.1%}".format(name, *get_sex_and_chance(name))