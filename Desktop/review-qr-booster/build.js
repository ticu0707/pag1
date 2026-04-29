const fs = require('fs');
const path = require('path');

const base = __dirname;

let html = fs.readFileSync(path.join(base, 'app-template.html'), 'utf8');
const qrcode = fs.readFileSync(path.join(base, 'qrcode.min.js'), 'utf8');
const html2canvas = fs.readFileSync(path.join(base, 'html2canvas.min.js'), 'utf8');
const jspdf = fs.readFileSync(path.join(base, 'jspdf.umd.min.js'), 'utf8');

html = html.replace('/* __QRCODE_JS__ */', qrcode);
html = html.replace('/* __HTML2CANVAS_JS__ */', html2canvas);
html = html.replace('/* __JSPDF_JS__ */', jspdf);

const out = path.join(base, 'app.html');
fs.writeFileSync(out, html, 'utf8');

const sizeKB = Math.round(fs.statSync(out).size / 1024);
console.log(`OK — app.html generat: ${sizeKB} KB`);
