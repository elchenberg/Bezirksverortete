# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
import csv
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

def extract_name(string):
    titel = ''
    nachname = ''
    vornamen = ''
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
    return titel, nachname, vornamen

def extract_liste(strings):
    line = strings[0]
    next_line = strings[1]
    liste = ''
    kurz = ''
    name_in_next_line = next_line.startswith('Name')
    if not name_in_next_line:
        if not line[-1] == '-':
            line += ' '
        line += next_line
    liste = line.split(':')[1].strip()
    liste, kurz = liste.split(' (')
    kurz = kurz[:-1]
    return liste, kurz

def extract_person(strings):
    titel = ''
    nachname = ''
    vornamen = ''
    geboren = ''
    plz = ''
    for string in strings:
        if string[:3] == 'Nam':
            titel, nachname, vornamen = extract_name(string)
        elif string[:3] == 'geb':
            geboren = string.split()[1][:-1]
        elif string[:3] == 'PLZ':
            plz = string.split()[-1]
            break
    person = {
        'titel': titel,
        'nachname': nachname,
        'vornamen': vornamen,
        'geboren': geboren,
        'plz': plz
    }
    return person

def main():
    pdftext = pdf_to_plain_text('.berlinbvvkandidierende2016.pdf')
    pdflines = [line.strip() for line in pdftext.split('\n')]

    kandidierende = []

    for idl, line in enumerate(pdflines):
        if not line:
            continue
        if line.startswith('Bezirk:'):
            bezirk = line.split()[1]
            continue
        if line.startswith('Liste Nr'):
            liste, kurz = extract_liste(pdflines[idl:idl+2])
            continue
        try:
            liste
        except NameError:
            continue
        if line.startswith('Name'):
            person = extract_person(pdflines[idl:idl+6])
            person['liste'] = liste
            person['kurz'] = kurz
            person['bezirk'] = bezirk
            kandidierende.append(person)
            continue

    with open('.berlinbvvkandidierende2016.csv', 'w') as csvfile:
        fieldnames = [
            'titel',
            'nachname',
            'vornamen',
            'geboren',
            'plz',
            'liste',
            'kurz',
            'bezirk'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(kandidierende)

if __name__ == '__main__':
    main()
