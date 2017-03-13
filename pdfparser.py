# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
import csv
import json
import tempfile
import subprocess

import PyPDF2

def pdf_to_plain_text(filename):
    with open(filename, 'rb') as pdffile:
        pdfreader = PyPDF2.PdfFileReader(pdffile)
        pdfwriter = PyPDF2.PdfFileWriter()
        for page in pdfreader.pages:
            column_left = copy.copy(page)
            column_right = copy.copy(page)

            right, top = page.mediaBox.upperRight

            column_left.mediaBox.lowerLeft = (0, 0)
            column_left.mediaBox.upperRight = (right/2, top)

            column_right.mediaBox.lowerLeft = (right/2, 0)
            column_right.mediaBox.upperRight = (right, top)

            pdfwriter.addPage(column_left)
            pdfwriter.addPage(column_right)

        tmpfile = tempfile.NamedTemporaryFile()
        pdfwriter.write(tmpfile)
        tmpfile.flush()

    commands = ['pdftotext', '-layout', tmpfile.name, '-']
    pdftotext = subprocess.run(commands, stdout=subprocess.PIPE)
    text = pdftotext.stdout
    return text.decode()

PDFTEXT = pdf_to_plain_text('berlinbvvkandidierende2016.pdf')
PDFLINES = [line.strip() for line in PDFTEXT.split('\n')]

PERSONS = []

for l, line in enumerate(PDFLINES):
    if not line:
        continue
    if line.startswith('Bezirk:'):
        bezirk = line.split()[1]
        continue
    if line.startswith('Liste Nr'):
        next_line = PDFLINES[l+1]
        name_in_next_line = next_line.startswith('Name')
        if not name_in_next_line:
            if not line[-1] == '-':
                line += ' '
            line += next_line
        liste = line.split(':')[1].strip()
        liste, kurz = liste.split(' (')
        kurz = kurz[:-1]
        continue
    try:
        liste
    except NameError:
        continue
    if line.startswith('Name'):
        titel = ''
        nachname = ''
        vornamen = ''
        geboren = ''
        plz = ''
        for string in PDFLINES[l:l+6]:
            if string[:3] == 'Nam':
                try:
                    _, vornamen = string.split(', ')
                    _, _, *nachname = _.split()
                    if nachname[0] == 'Dr.':
                        titel = nachname[0]
                        nachname = ' '.join(nachname[1:])
                    else:
                        nachname = ' '.join(nachname)
                except ValueError:
                    vornamen = 'Can'
                    nachname = 'Șepșul'
            elif string[:3] == 'geb':
                geboren = string.split()[1][:-1]
            elif string[:3] == 'PLZ':
                plz = string.split()[-1]
                break
        PERSONS.append({
            'titel': titel,
            'nachname': nachname,
            'vornamen': vornamen,
            'geboren': geboren,
            'plz': plz,
            'liste': liste,
            'kurz': kurz,
            'bezirk': bezirk
        })
        continue

with open('berlinbvvkandidierende2016.json', 'w') as jsonfile:
    jsonfile.write(json.dumps(PERSONS,
                              ensure_ascii=False,
                              indent=4,
                              sort_keys=True))

with open('berlinbvvkandidierende2016.csv', 'w') as csvfile:
    FIELDNAMES = [
        'titel',
        'nachname',
        'vornamen',
        'geboren',
        'plz',
        'liste',
        'kurz',
        'bezirk'
    ]
    WRITER = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
    WRITER.writeheader()
    WRITER.writerows(PERSONS)
