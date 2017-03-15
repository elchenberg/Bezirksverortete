# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
import csv
import tempfile
import subprocess

import PyPDF2

INFILE = '.berlinbvvkandidierende2016.pdf'
OUTFILE = '.berlinbvvkandidierende2016.csv'

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

        tmpfile = tempfile.SpooledTemporaryFile()
        pdfwriter.write(tmpfile)
        tmpfile.seek(0)

        pdftotext = subprocess.run(['pdftotext', '-layout', '-', '-'],
                                   stdin=tmpfile,
                                   stdout=subprocess.PIPE)
        tmpfile.close()
    text = pdftotext.stdout
    return text.decode()


def extract_liste(text):
    _, text = text.split('(')
    text, *_ = text.split(')')

    normalize = {
        'afd': 'AfD',
        'cdu': 'CDU',
        'fdp': 'FDP',
        'grün': 'GRÜNE',
        'link': 'LINKE',
        'piraten': 'PIRATEN',
        'spd': 'SPD',
        'die partei': 'PARTEI'
    }

    for fragment, kuerzel in normalize.items():
        if fragment in text.lower():
            text = kuerzel
    return text

def extract_name(text):
    titel = ''
    nachnamen = ''
    vornamen = ''
    if 'Dr.' in text:
        text = text.replace('Dr.', '')
        titel = 'Dr.'
    try:
        nachnamen, vornamen = text.split(', ')
        nachnamen = nachnamen.split()[2:]
        nachnamen = ' '.join(nachnamen)
    except ValueError:
        vornamen = 'Can'
        nachnamen = 'Șepșul'
    return titel, nachnamen, vornamen


def extract_person(lines):
    titel = ''
    nachnamen = ''
    vornamen = ''
    geboren = ''
    plz = ''
    for line in lines:
        if line[:3] == 'Nam':
            titel, nachnamen, vornamen = extract_name(line)
        elif line[:3] == 'geb':
            geboren = line.split()[1][:-1]
        elif line[:3] == 'PLZ':
            plz = line.split()[-1]
            break
    person = {
        'TITEL': titel,
        'ANZEIGENAME': vornamen + ' ' + nachnamen,
        'NACHNAMEN': nachnamen,
        'VORNAMEN': vornamen,
        'JAHRGANG': geboren,
        'PLZ': plz
    }
    return person

def main():
    text = pdf_to_plain_text(INFILE)
    lines = text.splitlines()
    lines = [line.strip() for line in lines]
    lines = [line for line in lines if line]

    candidates = []

    for index, line in enumerate(lines):
        if line.startswith('Bezirk:'):
            bezirk = line.split()[1]
        elif line.startswith('Liste Nr'):
            liste = extract_liste(line + ' ' + lines[index+1])
        elif line.startswith('Name'):
            person = extract_person(lines[index:index+6])
            person['LISTE'] = liste
            person['BEZIRK'] = bezirk
            candidates.append(person)

    with open(OUTFILE, 'w') as csvfile:
        fieldnames = [
            'TITEL',
            'ANZEIGENAME',
            'NACHNAMEN',
            'VORNAMEN',
            'JAHRGANG',
            'PLZ',
            'LISTE',
            'BEZIRK'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(candidates)

if __name__ == '__main__':
    main()
