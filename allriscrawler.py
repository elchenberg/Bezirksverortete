# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import http.client
import time
import unicodedata
import zlib

import lxml.html

CANDIDATESCSV = '.berlinbvvkandidierende2016.csv'
COUNCILLORSCSV = 'berlinbvvmitglieder.csv'
WEBPAGESTXT = 'links.txt'

def normalized_name(text):
    """
    Strip umlauts and accents from names.

    Convert input strings to lowercase,
    convert umlauts, strip accents,
    replace hyphens with whitespace
    and remove redundant whitespace.

    :param text: The input string.
    :type text: String.

    :returns: The processed string.
    :rtype: String.
    """
    text = text.lower()

    text = text.replace('ß', 'ss')
    text = text.replace('ä', 'ae')
    text = text.replace('ö', 'oe')
    text = text.replace('ü', 'ue')

    text = text.replace('-', ' ')
    text = ' '.join(text.split())

    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode('utf-8')
    return text

def persons_from_csv(filename):
    persons = {}
    try:
        with open(filename, 'r') as csvfile:
            csvrows = csv.DictReader(csvfile)
            csvrows = [row for row in csvrows]

        for index, row in enumerate(csvrows):
            name = row['ANZEIGENAME']
            bezirk = row['BEZIRK']
            identifier = normalized_name(name)
            try:
                persons[bezirk][identifier] = csvrows[index]
            except KeyError:
                persons[bezirk] = {identifier: csvrows[index]}

    except FileNotFoundError:
        pass

    return persons

def extract_councillor(htmltablerow):
    titel = ''
    name = ''
    fraktion = ''
    link = ''

    name = htmltablerow[2].text_content()
    name = name.replace('Bezv.V.', '')
    name = name.replace('Bezv.', '')
    if 'Prof.' in name:
        name = name.replace('Prof.', '')
        titel = 'Prof.'
    if 'Dr.' in name:
        name = name.replace('Dr.', '')
        titel += ' Dr.'
        titel = titel.strip()
    if 'Dipl.-Oec.' in name:
        name = name.replace('Dipl.-Oec.', '')
        titel += ' Dipl.-Oec.'
        titel = titel.strip()
    name = ' '.join(name.split())

    fraktion = htmltablerow[4].text_content()
    fraktion = normalized_fraktion(fraktion)

    if len(htmltablerow[2]) and not fraktion == 'AfD':
        link = htmltablerow[2][0].get('href')
        link = link.replace('&options=4', '')

    councillor = {
        'TITEL': titel,
        'ANZEIGENAME': name,
        'FRAKTION': fraktion,
        'LINK': link
    }
    return councillor

def download_councillors():
    with open(WEBPAGESTXT, 'r') as txtfile:
        urls = txtfile.readlines()
    urls = [url.strip() for url in urls]

    session = http.client.HTTPSConnection('www.berlin.de', timeout=10)
    councillors = {}
    for url in urls:
        if councillors:
            time.sleep(2)

        bezirk = bezirk_from_url(url)

        headers = {'Accept-Encoding': 'gzip',
                   'Connection': 'keep-alive'}
        session.request('GET', url, headers=headers)
        response = session.getresponse()

        response = response.read()
        response = zlib.decompress(response, 47)

        try:
            response = response.decode('latin-1', 'strict')
        except UnicodeDecodeError:
            response = response.decode('windows-1252', 'strict')

        html = lxml.html.fromstring(response)
        html.make_links_absolute(url)

        tablerows = html.cssselect('.zl12')
        tablerows += html.cssselect('.zl11')

        number = html.cssselect('table.tk1:nth-child(8)')[0]
        number = number.text_content()
        _, number = number.split(':')
        number = number.strip()
        if number.isdigit():
            number = int(number)
            if not number == len(tablerows):
                print('%s:' % bezirk,
                      '%s councillors were found.' % len(tablerows),
                      'Should be %s councillors.' % number)

        for row in tablerows:
            councillor = extract_councillor(row)
            councillor['BEZIRK'] = bezirk
            identifier = normalized_name(councillor['ANZEIGENAME'])
            try:
                councillors[bezirk][identifier] = councillor
            except KeyError:
                councillors[bezirk] = {identifier: councillor}
    session.close()
    return councillors

def bezirk_from_url(url):
    slug = url.split('/')[3][3:]
    bezirk = slug.split('-')
    bezirk = [element.capitalize() for element in bezirk]
    bezirk = '-'.join(bezirk)
    bezirk = bezirk.replace('oe', 'ö')
    return bezirk

def normalized_fraktion(fraktion):
    translation = {
        'afd': 'AfD',
        'cdu': 'CDU',
        'fdp': 'FDP',
        'grün': 'GRÜNE',
        'link': 'LINKE',
        'piraten': 'PIRATEN',
        'spd': 'SPD',
        'die partei': 'PARTEI'
    }
    for key, normalized in translation.items():
        if key in fraktion.lower():
            return normalized
    return fraktion

def main():
    candidates = persons_from_csv(CANDIDATESCSV)
    previously = persons_from_csv(COUNCILLORSCSV)
    currently = download_councillors()

    # Mit dem einfachen Abgleich von Bezirk und Name können etwa 97%
    # der aktuellen Bezirksverordneten mit den Daten des PDFs der
    # Wahlvorschläge/-listen verknüpft werden. Die Daten der
    # verbleibenden Bezirksverordneten sind von Hand nachzutragen.
    output = []
    for bezirk in sorted(currently.keys()):
        for identifier in sorted(currently[bezirk].keys()):
            allris = currently[bezirk][identifier]
            if previously and identifier in previously[bezirk]:
                locally = previously[bezirk][identifier]
            elif candidates and identifier in candidates[bezirk]:
                locally = candidates[bezirk][identifier]
            else:
                locally = {'NACHNAMEN': '', 'VORNAMEN': '',
                           'JAHRGANG': '', 'LISTE': '', 'PLZ': ''}
                print(
                    'Unidentified: %s,' % allris['ANZEIGENAME'],
                    '%s %s' % (allris['FRAKTION'], allris['BEZIRK'])
                )
            output.append({
                'TITEL': allris['TITEL'],
                'ANZEIGENAME': allris['ANZEIGENAME'],
                'NACHNAMEN': locally['NACHNAMEN'],
                'VORNAMEN': locally['VORNAMEN'],
                'JAHRGANG': locally['JAHRGANG'],
                'FRAKTION': allris['FRAKTION'],
                'LISTE': locally['LISTE'],
                'BEZIRK': allris['BEZIRK'],
                'PLZ': locally['PLZ'],
                'LINK': allris['LINK']
            })

    with open(COUNCILLORSCSV, 'w') as csvfile:
        fieldnames = [
            'TITEL',
            'ANZEIGENAME',
            'NACHNAMEN',
            'VORNAMEN',
            'JAHRGANG',
            'FRAKTION',
            'LISTE',
            'BEZIRK',
            'PLZ',
            'LINK'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output)

    #import json
    #with open(COUNCILLORSCSV.replace('csv', 'json'), 'w') as jsonfile:
    #    json.dump(output, jsonfile, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()
