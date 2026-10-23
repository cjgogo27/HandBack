"""Build a plain static HTML report; no telemetry or external rendering dependencies."""
from pathlib import Path
import re, csv, json
import markdown

ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'docs/report.md').read_text(encoding='utf8')
# All non-image local links point to the actual GitHub artifact, not a Pages .md view.
source=re.sub(r'(?<!!)\[([^\]]+)\]\((?!https?://)([^)]+)\)',
    lambda m:'['+m[1]+'](https://github.com/cjgogo27/HandBack/blob/main/'+
        ('data/'+m[2].split('../data/',1)[1] if m[2].startswith('../data/') else 'docs/'+m[2])+')',source)
body=markdown.markdown(source,extensions=['tables','fenced_code','toc'])
html='''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="A bounded Piper study of learning-value-based control handback: results, mechanism audit and reproducible analysis.">
<title>HandBack — technical report</title>
<style>
:root{color-scheme:light;--ink:#172b3a;--muted:#526778;--line:#dce4e9;--accent:#12627f}
*{box-sizing:border-box}body{margin:0;background:#fbfcfe;color:var(--ink);font:17px/1.65 system-ui,-apple-system,Segoe UI,sans-serif}
nav{border-bottom:1px solid var(--line);padding:18px max(20px,calc((100vw - 1040px)/2));display:flex;gap:24px;flex-wrap:wrap;background:white}
a{color:var(--accent);text-underline-offset:3px}nav a{text-decoration:none;font-size:14px}main{max-width:1040px;margin:40px auto;padding:0 22px 70px}
h1{font-size:clamp(29px,4vw,43px);line-height:1.18;letter-spacing:-.035em;max-width:960px;margin:20px 0}h2{font-size:24px;line-height:1.3;margin-top:42px}
p{max-width:940px}table{border-collapse:collapse;display:block;overflow-x:auto;width:100%;font-size:14px;margin:24px 0}
th,td{padding:10px 12px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}th{background:#edf3f7;white-space:nowrap}tbody tr:last-child{border-bottom:2px solid var(--line)}
code{background:#eaf0f4;padding:2px 4px;border-radius:3px;font-size:.85em}pre{overflow:auto;padding:16px;background:#eaf0f4}pre code{padding:0}img{max-width:100%;height:auto;background:white}blockquote{border-left:3px solid var(--accent);margin-left:0;padding-left:18px}
.status{background:#e9f2f5;border:1px solid #b8d1db;border-radius:6px;padding:16px 20px;margin:28px 0;font-size:16px}
footer{border-top:1px solid var(--line);padding-top:24px;font-size:13px;color:var(--muted)}
@media print{nav,.status{display:none}body{font-size:10pt;background:white}main{margin:0;max-width:none;padding:0}h1{font-size:23pt}h2{font-size:15pt;margin-top:20px}table{font-size:9pt;break-inside:avoid}a{color:inherit}img{max-height:6cm}footer{font-size:8pt}}
</style></head><body><nav aria-label="Project navigation">
<a href="https://github.com/cjgogo27/HandBack">GitHub</a>
<a href="https://github.com/cjgogo27/HandBack/blob/main/docs/report.md">Markdown report</a>
<a href="https://github.com/cjgogo27/HandBack/blob/main/docs/reproduction.md">Reproduce</a>
<a href="https://github.com/cjgogo27/HandBack/tree/main/data">Data</a></nav><main>
<div class="status"><strong>Exploratory result:</strong> feasibility gates failed; learning-value and first-support selected identical training treatments. No larger experiment was run.</div>
'''+body+'''
<footer>HandBack v0.1.0 · Exploratory technical report, not a peer-reviewed publication.<br>
Report and derived results: CC BY 4.0. Code: MIT. <a href="https://github.com/cjgogo27/HandBack/blob/main/docs/reference_study.md">10 reporting precedents and 5 release examples</a>.</footer>
</main></body></html>
'''
(ROOT/'docs/report.html').write_text(html,encoding='utf8',newline='\n')
data={'rows':list(csv.DictReader((ROOT/'data/stage_a.csv').open(encoding='utf8'))),
      'media':json.loads((ROOT/'data/media_manifest.json').read_text(encoding='utf8'))}
template=(ROOT/'scripts/site_template.html').read_text(encoding='utf8')
(ROOT/'docs/index.html').write_text(template.replace('__STUDY_DATA__',json.dumps(data,separators=(',',':')).replace('</','<\\/')),encoding='utf8',newline='\n')
(ROOT/'docs/.nojekyll').touch()
print('Built docs/index.html and docs/report.html')
