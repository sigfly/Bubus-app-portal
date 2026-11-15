"""Bygg en statisk app-portal fra en liste med private GitHub-repoer."""
import html
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path, PurePosixPath

TOKEN = os.environ.get("PRIVATE_REPOS_READ_TOKEN", "")
if not TOKEN:
    raise SystemExit("Mangler PRIVATE_REPOS_READ_TOKEN i GitHub Actions secrets.")

apps = json.loads(Path("apps.json").read_text(encoding="utf-8"))
site = Path("_site")
site.mkdir(exist_ok=True)
links = []
slugs = set()

for app in apps:
    slug = app["slug"]
    repo = app["repo"]
    source_file = app.get("file", "index.html")

    if not re.fullmatch(r"[a-z0-9-]+", slug) or slug in slugs:
        raise ValueError(f"Ugyldig eller duplisert slug: {slug}")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise ValueError(f"Ugyldig repo i apps.json: {repo}")
    if (not source_file or source_file.startswith("/")
            or ".." in PurePosixPath(source_file).parts
            or not source_file.lower().endswith((".html", ".htm"))):
        raise ValueError(f"Ugyldig HTML-fil i apps.json: {source_file}")
    slugs.add(slug)

    # GitHub Contents API leverer rå HTML-bytes. Repoets standardgren brukes.
    path = urllib.parse.quote(source_file, safe="/")
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    request = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github.raw+json",
        "Authorization": f"Bearer {TOKEN}",
        "User-Agent": "personal-app-portal-builder",
        "X-GitHub-Api-Version": "2026-03-10",
    })
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            contents = response.read()
    except urllib.error.HTTPError as error:
        raise RuntimeError(
            f"Kan ikke hente {source_file} fra {repo} (HTTP {error.code}). "
            "Sjekk repo, filnavn og token-tilgang."
        ) from error

    destination = site / "apps" / slug / "index.html"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(contents)
    print(f"Hentet {repo}/{source_file} -> {destination}")

    title = html.escape(app["title"])
    description = html.escape(app.get("description", ""))
    links.append(
        f'<a class="card" href="./apps/{slug}/">'
        f'<strong>{title}</strong><span>{description}</span>'
        '</a>'
    )

cards = "\n".join(links)
homepage = """<!DOCTYPE html>
<html lang="no">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex, nofollow">
  <title>Mine apper</title>
  <style>
    :root { color-scheme: dark; }
    * { box-sizing: border-box; }
    body { margin: 0; font: 16px system-ui, sans-serif;
           color: #f5f7fb; background: #101827; }
    main { max-width: 950px; margin: 0 auto; padding: 65px 22px; }
    h1 { font-size: clamp(2rem, 5vw, 3rem); margin: 0 0 10px; }
    .intro { color: #a5b4cc; margin: 0 0 32px; }
    .grid { display: grid; gap: 16px;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }
    .card { display: flex; flex-direction: column; gap: 14px;
            padding: 24px; border-radius: 14px; text-decoration: none;
            border: 1px solid #354159; background: #1d293d; color: inherit; }
    .card:hover, .card:focus-visible { background: #2c3b54;
                                        outline-color: #a4b8ff; }
    .card strong { font-size: 1.15rem; }
    .card span { color: #adbad0; }
  </style>
</head>
<body>
  <main>
    <h1>🚀 Mine apper</h1>
    <p class="intro">Samlet på ett sted</p>
    <div class="grid">%%CARDS%%</div>
  </main>
</body>
</html>
"""
(site / "index.html").write_text(homepage.replace("%%CARDS%%", cards), encoding="utf-8")
(site / ".nojekyll").touch()
print(f"Bygget startside med {len(apps)} apper.")
