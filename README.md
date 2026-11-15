# App Portal

Automatisk statisk GitHub Pages-startside for standalone HTML-filer fra private GitHub-repoer.

## Oppsett

1. Opprett repo `app-portal` under din GitHub-konto. Et offentlig repo fungerer på GitHub Free. Med GitHub Pro kan kilderepoet være privat; Pages-nettstedet blir vanligvis likevel offentlig.
2. Last opp *innholdet* i denne mappen til roten av repoet (inkludert `.github/`). Kontroller at standardgrenen heter `main`.
3. Rediger `apps.json`: `slug` er URL-navn, `title` og `description` vises på startsiden, `repo` er `EIER/REPONAVN`, og `file` er den eksakte relative banen til HTML-filen.
4. Opprett et GitHub fine-grained Personal Access Token med `Repository access: Only select repositories` og velg de private app-repoene. Gi bare `Repository permissions -> Contents: Read-only`. Velg rett `Resource owner`. Gi tokenet utløpsdato, og roter når det utløper.
5. I `app-portal` går du til `Settings -> Secrets and variables -> Actions -> New repository secret`. Bruk navnet `PRIVATE_REPOS_READ_TOKEN`, og lim inn tokenet som verdi. IKKE lagre tokenet i kode eller `apps.json`.
6. Gå til `Settings -> Pages -> Build and deployment -> Source: GitHub Actions`.
7. I `Actions` velger du `Publiser App Portal` og `Run workflow` (eller rediger og commit `apps.json` for å starte en push-kjøring).
8. Åpne `https://BRUKERNAVN.github.io/app-portal/`.

## Oppdateringer

Workflow kjører når `apps.json` eller skriptet endres, når du starter den manuelt, og etter planen fire ganger i døgnet. Nye versjoner av HTML-filene hentes fra app-repoenes standardgren. Endringer i app-repoene starter *ikke* i seg selv en kjøring; derfor kan oppdatering vises først ved neste planlagte kjøring.

## Viktig sikkerhet

Publiserte HTML-appfiler er offentlig tilgjengelige på GitHub Pages, selv om originalrepoene er private. Ikke publiser passord, API-nøkler, sensitive data eller annen hemmelig informasjon. `noindex` er ingen tilgangskontroll. Hvis portalen er i et offentlig repo, vil også `apps.json` med reponavn være offentlig.

## Begrensninger

Oppsettet er laget for en enkelt HTML-fil per app uten eksterne lokale CSS/JS-filer. GitHub Contents API har maksgrense på 100 MB per fil. Et fine-grained PAT er knyttet til én resource owner; for repoer under flere eiere/organisasjoner må du justere autentiseringen.
