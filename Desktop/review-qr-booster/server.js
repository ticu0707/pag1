const http = require('http');
const fs = require('fs');
const path = require('path');

const BASE = __dirname;
const PORT = 3333;
const MIME = {
  '.html': 'text/html',
  '.js': 'application/javascript',
  '.css': 'text/css',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.json': 'application/json'
};

http.createServer((req, res) => {
  const url = req.url === '/' ? '/app.html' : req.url;
  const file = path.join(BASE, url);
  fs.readFile(file, (err, data) => {
    if (err) {
      res.writeHead(404);
      res.end('404 Not Found');
      return;
    }
    const ext = path.extname(file);
    res.writeHead(200, { 'Content-Type': MIME[ext] || 'text/plain' });
    res.end(data);
  });
}).listen(PORT, () => {
  console.log(`Server pornit: http://localhost:${PORT}`);
});
