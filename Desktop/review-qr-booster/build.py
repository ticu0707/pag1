import os

base = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(base, 'app-template.html'), encoding='utf-8') as f:
    html = f.read()

with open(os.path.join(base, 'qrcode.min.js'), encoding='utf-8') as f:
    qrcode = f.read()

with open(os.path.join(base, 'html2canvas.min.js'), encoding='utf-8') as f:
    html2canvas = f.read()

with open(os.path.join(base, 'jspdf.umd.min.js'), encoding='utf-8') as f:
    jspdf = f.read()

html = html.replace('/* __QRCODE_JS__ */', qrcode)
html = html.replace('/* __HTML2CANVAS_JS__ */', html2canvas)
html = html.replace('/* __JSPDF_JS__ */', jspdf)

out = os.path.join(base, 'app.html')
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)

size_kb = os.path.getsize(out) // 1024
print(f'OK — app.html generat: {size_kb} KB')
