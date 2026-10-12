"""Recreate the book-authored ingestion fixtures; no external sources or OCR."""
import io
import json
from pathlib import Path
from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

HERE = Path(__file__).resolve().parent


def build(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    markdown = ('# Restart runbook\n\n## Release TK-042\n\n'
        'Do not restart before approval.\n\n'
        'The cafe\u0301 team owns the restart.\n\n'
        '```python\nif approved:\n    restart()\n```\n')
    html = '''<!doctype html><html><head><title>Retry policy</title></head><body>
<nav>Home Support Retry Retry Retry</nav><main>
<h1 id="policy">Retry policy</h1><p id="intro">Limits depend on region.</p>
<table id="limits"><tr><th>Region</th><th>Retry limit</th></tr>
<tr><td>East</td><td>2</td></tr><tr><td>West</td><td>4</td></tr></table>
<p id="exception">No retry on HTTP 403.</p></main>
<footer>Copyright book fixture</footer><script>retry=999</script></body></html>'''
    merged = '''<main><table id="merged"><tr><th>Region</th><th>Limit</th></tr>
<tr><td rowspan="2">East</td><td>2</td></tr><tr><td>4</td></tr></table></main>'''
    for name, content in [('runbook.md', markdown), ('runbook-copy.md', markdown),
                          ('retry.html', html), ('merged.html', merged),
                          ('unknown.md', '# Unreviewed rights\nDo not ingest yet.\n'),
                          ('private.md', '# PRIVATE FIXTURE\nProtected marker.\n')]:
        (directory/name).write_bytes(content.encode('utf-8'))
    (directory/'broken.md').write_bytes(b'# Invalid\nBad UTF-8: \xff\n')
    pdf = canvas.Canvas(str(directory/'contract.pdf'), pagesize=(612, 792), invariant=1)
    for number, lines in [(1, ['Signed response policy', 'First response is four hours.']),
                          (2, ['Verification note', 'Clock starts after verification.'])]:
        pdf.setFont('Helvetica', 11)
        pdf.drawString(54, 754, 'ACME SUPPORT - CONTROLLED FIXTURE')
        pdf.setFont('Helvetica-Bold', 16)
        pdf.drawString(54, 692, lines[0])
        pdf.setFont('Helvetica', 12)
        pdf.drawString(54, 650, lines[1])
        pdf.setFont('Helvetica', 9)
        pdf.drawString(54, 32, f'Page {number}')
        pdf.showPage()
    pdf.save()
    raster = Image.new('RGB', (1020, 1320), 'white')
    draw = ImageDraw.Draw(raster)
    draw.text((70, 110), 'Scanned retention amendment', fill='black', font_size=38)
    draw.text((70, 190), 'Retention is 15 days.', fill='black', font_size=34)
    scan = canvas.Canvas(str(directory/'scanned.pdf'), pagesize=(612, 792), invariant=1)
    scan.drawImage(ImageReader(raster), 0, 0, width=612, height=792)
    scan.save()
    rows = []
    for source_id, name in [('S-md','runbook.md'), ('S-html','retry.html'),
                            ('S-pdf','contract.pdf'), ('S-copy','runbook-copy.md'),
                            ('S-scan','scanned.pdf'), ('S-bad','broken.md'),
                            ('S-merged','merged.html'), ('S-unknown','unknown.md'),
                            ('S-private','private.md')]:
        rows.append({'source_id': source_id, 'source_version': '1', 'path': name,
                     'allowed_scopes': ['private'] if source_id == 'S-private' else ['support-team'],
                     'indexing_allowed': source_id != 'S-unknown',
                     'license': 'book-authored-fixture' if source_id != 'S-unknown' else None,
                     'retention_policy': 'fixture-until-project-removal'})
    (directory/'sources.json').write_bytes((json.dumps(rows, indent=2)+'\n').encode('utf-8'))


if __name__ == '__main__':
    build(HERE/'fixtures')
