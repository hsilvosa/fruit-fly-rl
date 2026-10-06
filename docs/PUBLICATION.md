# Preparing a public source release

The public repository is a source distribution with guides, aggregate experiment evidence, and original map illustrations. It does not ship connectome downloads, trained weights, private journals, launch records, full flight archives, local environments, or generated QA logs. A fresh clone can prepare the data and run the observed-map planner without a trained checkpoint.

## Organization and license scope

The [repository map](../README.md#repository-map) identifies runtime modules and local artifact folders. Existing root launchers are retained for compatibility. Detailed evidence belongs in ignored `private/`; public summaries belong in `docs/evidence/`, and deliberately published image assets belong in `docs/images/`. General QA figures remain ignored under `reports/`.

Original project code and documentation use [MIT](../LICENSE). Downloaded MaleCNS data is separately attributed under CC BY 4.0; the project license does not change its license or the licenses of dependencies. The original creators, modifications, and citation are listed in [references](REFERENCES.md). Preserve these notices when redistributing derived data.

The deliberately published [architectural drafts](ARCHITECTURAL_SCENES.md) live under `assets/architecture/draft-0.1`, including original OBJ/MTL geometry, collision/scenario JSON and previews. They use MIT and contain no third-party scans. Asset manifests record exact hashes; generated text uses LF, including on Windows. Future imported real-place assets need their own license and source review before publication.

`.gitignore` excludes local artifacts, environments, caches, logs, model binaries, and common credential files. It does not remove already tracked files or history. `.gitattributes` normalizes text and keeps image files binary; Python/documentation use LF, Windows launchers use CRLF.

## Check the tracked tree

Run from the repository root:

```powershell
.\.conda\python.exe -s scripts/verify_repository.py
.\.conda\python.exe -s scripts/verify_publication.py . --output reports/publication-qa.json
git diff --check
git status --short
```

Repository checks inspect documentation, module discovery, and CLI help without running training or policy evaluation. Publication checks inspect tracked files for excluded artifacts, unavailable links, personal paths, unfinished result placeholders, common credential patterns, and text-encoding errors. Image links must resolve within the tracked public tree. Review the diff as well; pattern scans cannot establish the absence of every secret.

Focused publication tests are in [test_publication.py](../tests/test_publication.py). Use the broader test suite when changing shared runtime behavior. Do not rerun reserved navigation tests merely to prepare a release.

## Keep development history private

The local `publication` branch has a fresh root containing the reviewed public tree. The local `master` branch retains older development records. Publish only the reviewed branch, not all branches or the older history. Cleanup does not itself push anything to a remote service.

After committing the reviewed tree, produce and audit a source-only ZIP:

```powershell
New-Item -ItemType Directory -Path dist -Force | Out-Null
git -c core.autocrlf=false archive --format=zip --output=dist/fly-rl-public.zip HEAD
.\.conda\python.exe -s scripts/verify_publication.py . --archive dist/fly-rl-public.zip --output reports/publication-archive-qa.json
```

The archive audit compares its file list and content with committed Git blobs, accounting for the declared text-line conversion in `.gitattributes`. Windows launcher CRLF export is accepted; changed commands, modified binary content, extra files, and `.git` history are rejected. The ZIP deliberately omits local models and data; retain private backups separately. Auditing the current tree or archive does not sanitize unrelated historical branches.
