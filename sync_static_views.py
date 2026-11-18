import urllib.request
import os

urls = {
    'pagina/index.html': 'http://127.0.0.1:8000/',
    'pagina/galeria.html': 'http://127.0.0.1:8000/galeria/',
    'pagina/colecciones.html': 'http://127.0.0.1:8000/colecciones/',
    'pagina/artistas.html': 'http://127.0.0.1:8000/artistas/',
    'pagina/contacto.html': 'http://127.0.0.1:8000/contacto/'
}

for dest, src in urls.items():
    try:
        req = urllib.request.Request(src, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode('utf-8')
            # Ajustar para que funcione tanto en servidor como abriendo el archivo HTML directamente
            content_fixed = (
                content.replace('/static/', '../static/')
                       .replace('href="/galeria/"', 'href="galeria.html"')
                       .replace('href="/colecciones/"', 'href="colecciones.html"')
                       .replace('href="/artistas/"', 'href="artistas.html"')
                       .replace('href="/contacto/"', 'href="contacto.html"')
                       .replace('href="/"', 'href="index.html"')
            )
            with open(dest, 'w', encoding='utf-8') as f:
                f.write(content_fixed)
            print(f'Actualizado {dest} ({len(content_fixed)} bytes)')
    except Exception as e:
        print(f'Error en {dest}: {e}')
