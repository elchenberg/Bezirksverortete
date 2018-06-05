# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import string

COUNCILLORSCSV = 'berlinbvvmitglieder.csv'

HTML = """<!DOCTYPE html>
<html lang=de>
<head>
<meta charset=UTF-8>
<meta content="width=device-width,initial-scale=1" name=viewport>
<title>Finde Deine Berliner Bezirksverordneten</title>
<style>html{font-family:Montserrat,Verdana,Geneva,sans-serif;line-height:1.6}body{max-width:720px;margin:0 auto;padding:2%;box-sizing:border-box;hyphens:auto}h1{font-family:Merriweather,Georgia,serif;font-size:1.8em}a{text-decoration:none;color:#158}a:hover{text-decoration:underline}table{width:100%;max-width:100%;border-collapse:collapse;word-wrap:normal;overflow-wrap:normal;hyphens:auto;margin-top:1em;box-sizing:border-box}td,th{border-bottom:1px solid #ddd;text-align:left;padding:.5em .2em}tr td:nth-child(3){hyphens:none}.sort:hover{cursor:pointer}.search{box-sizing:border-box;width:100%}.indicator{color:#555}.desc .indicator,.asc .indicator{color:#000}@media screen and (max-width:420px){th,td{display:inline-block;border-width:0}td:last-child{width:100%;border-width:1px}}label{display:none}table caption::before{content:"Tabelle: "}caption{font-size:smaller;color:#555}</style>
</head>
<body>
<header>
<h1>Finde Deine Berliner Bezirksverordneten</h1>
<p>In der untenstehenden Tabelle sind alle Berliner Bezirksverordneten mit der Postleitzahl ihrer Wohnanschrift zu finden. Diese Postleitzahlen sind vom Sommer 2016 und können daher inzwischen veraltet sein. Sie wurden damals von der Berliner Landeswahlleiterin mit den offiziellen Wahlvorschlägen der Parteien veröffentlicht.</p>
<p>Mit einem Klick auf den Namen der Bezirksverordneten gelangt man zu deren Internetseite im Informationssystem der Bezirksverordnetenversammlung, wo die Ausschussmitgliedschaften und oft auch Kontaktdaten zu finden sind.</p>
<p><small>Wer Fehler findet oder mir Rückmeldung geben möchte, erreicht mich per Email <em>helge at elchenberg dot me</em> oder Twitter <a href=https://twitter.com/elchenberg>twitter.com/elchenberg</a>. Die Daten der Tabelle können <a href="$filename">als CSV heruntergeladen werden</a>.</small></p>
</header>
<table id="data">
<caption>Alle Mitglieder der Berliner Bezirksverordnetenversammlungen</caption>
<thead>
<tr>
<th><span class="sort" data-sort="plz"><abbr title="Postleitzahl">PLZ</abbr></span></th>
<th><span class="sort" data-sort="name">Name</span></th>
<th><span class="sort" data-sort="fraktion">Fraktion</span></th>
<th><span class="sort" data-sort="bvv"><abbr title="Bezirksverordnetenversammlung">BVV</abbr></span></th>
</tr>
</thead>
<tbody class="list">
$tbody
</tbody>
</table>
<script src="js/list-1.5.0.min.js"></script>
<script src="js/main.js"></script>
</body>
</html>"""
ROWLINK = ('<tr><td class="plz">%s</td><td><a class="name" href="%s">%s</a></td><td class="fraktion">%s</td>'
           '<td class="bvv">%s</td></tr>\n')
ROW = '<tr><td class="plz">%s</td><td class="name">%s</td><td class="fraktion">%s</td><td class="bvv">%s</td></tr>\n'
def main():
    with open(COUNCILLORSCSV, 'r') as csvfile:
        csvrows = csv.DictReader(csvfile)
        csvrows = [row for row in csvrows]

    csvrows = sorted(csvrows, key=lambda k: k['PLZ'])

    tbody = ''
    for row in csvrows:
        if row['TITEL']:
            fullname = row['TITEL']+' '+row['ANZEIGENAME']
        else:
            fullname = row['ANZEIGENAME']
        if row['LINK']:
            tbody += ROWLINK % (
                row['PLZ'],
                row['LINK'], fullname,
                row['FRAKTION'],
                row['BEZIRK']
            )
        else:
            tbody += ROW % (
                row['PLZ'],
                fullname,
                row['FRAKTION'],
                row['BEZIRK']
            )
    html = string.Template(HTML)
    html = html.safe_substitute({
        'filename': COUNCILLORSCSV,
        'tbody': tbody.strip(),
    })
    with open('index.html', 'w') as htmlfile:
        htmlfile.write(html)
if __name__ == '__main__':
    main()
