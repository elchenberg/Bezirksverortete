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
<style>html{font-family:Montserrat,Verdana,Geneva,sans-serif;overflow-wrap:break-word;hyphens:auto;line-height:1.6}body{max-width:720px;margin:0 auto;padding:2%}h1{font-family:Merriweather,Georgia,serif}input{padding:.5em;margin-top:1em}a{text-decoration:none;color:#158}a:hover{text-decoration:underline}table{width:100%;border-collapse:collapse;overflow-wrap:normal;hyphens:manual;margin-top:1em}td,th{border-bottom:1px solid #ddd;padding:.5em .2em;text-align:left}</style>
</head>
<body onload="autofillPLZ()">
<header>
<h1>Finde Deine Berliner Bezirksverordneten</h1>
<p>In der untenstehenden Tabelle sind alle Berliner Bezirksverordneten mit der Postleitzahl ihrer Wohnanschrift zu finden. Diese Postleitzahlen sind <em>vom Sommer 2016</em> und können daher inzwischen veraltet sein. Sie wurden damals von der Berliner Landeswahlleiterin mit den offiziellen Wahlvorschlägen der Parteien veröffentlicht.</p>
<p>Mit einem Klick auf den Namen der Bezirksverordneten gelangt man zu deren Internetseite im Informationssystem der Bezirksverordnetenversammlung, wo die Ausschussmitgliedschaften und oft auch Kontaktdaten zu finden sind.</p>
<p><small>Wer Fehler findet oder mir Rückmeldung geben möchte, erreicht mich per Email <em>helge at elchenberg dot me</em> oder Twitter <a href=https://twitter.com/elchenberg>twitter.com/elchenberg</a>. Die Daten der Tabelle können <a href="$filename">als CSV heruntergeladen werden</a>.</small></p>
</header>
<script>
document.write('<input type="number" id="inputPLZ" onkeyup="filterPLZ()" oninput="filterPLZ()" placeholder="PLZ" maxlength="5" min="10115" max="14199">')
</script>
<table>
<thead>
<tr>
<th>PLZ</th>
<th>Name</th>
<th>Fraktion</th>
<th>Bezirksverordneten­versammlung</th>
</tr>
</thead>
<tbody>
$tbody
</tbody>
</table>
<script>function autofillPLZ(){var input=window.location.hash.substr(1);if(!isNaN(input)&&input.length<=5){document.getElementById("inputPLZ").value=input;filterPLZ()}}function filterPLZ(){var input,tbody,tr,td,i;input=document.getElementById("inputPLZ").value;tbody=document.getElementsByTagName("tbody")[0];tr=tbody.getElementsByTagName("tr");if(!isNaN(input)&&input.length<=5){for(i=0;i<tr.length;i++){td=tr[i].getElementsByTagName("td")[0];if(td){if(td.innerHTML.startsWith(input)){tr[i].style.display=""}else{tr[i].style.display="none"}}}}}</script>
</body>
</html>"""
ROWLINK = ('<tr><td>%s</td><td><a href="%s">%s</a></td><td>%s</td>'
           '<td>%s</td></tr>\n')
ROW = '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n'
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
    html = html.safe_substitute({'filename': COUNCILLORSCSV,
                                 'tbody': tbody})
    #html = html.replace('\n', '')
    with open('index.html', 'w') as htmlfile:
        htmlfile.write(html)
if __name__ == '__main__':
    main()
