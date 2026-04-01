# Imgur Migrate (Fork)

This repository is a maintained fork of the original project by `dlccyes`.

- Original project: <https://github.com/dlccyes/imgur-migrate>
- This fork: <https://github.com/vsrixyz/imgur-migrate>

## What This Tool Does

`imgur-migrate` scans Markdown files, downloads embedded Imgur images, and rewrites image links to local files.

Example conversion:

- From: `![diagram](https://i.imgur.com/abc123.png)`
- To (wikilink mode): `![[notes-1.png]]`
- To (mdlink mode): `![diagram](notes-1.png)`

## Improvements In This Fork

Compared to the original upstream version, this fork adds:

- Better install script reliability:
  - `install.sh` works from any current directory.
  - If the binary is missing, it attempts a local `pyinstaller` build automatically.
  - Clearer install/build error messages.
- Safer download behavior:
  - Request timeout and explicit user-agent.
  - Handles request failures without crashing.
  - Skips non-200 responses, empty payloads, and non-image (`text/*`) content.
  - Avoids rewriting files when no valid images were downloaded.
- Optional output folder for downloaded images:
  - New CLI option: `--images-dir <subdir>`
  - Stores images in a subdirectory and rewrites Markdown links to that relative path.

## Install

### Clone

```bash
git clone https://github.com/vsrixyz/imgur-migrate
cd imgur-migrate
```

### macOS / Linux

```bash
sh install.sh
```

This installs `imgur-migrate` to `/usr/local/bin/imgur-migrate`.

### Windows

No native binary is provided in this repo. Run directly with Python:

```bash
pip install -r requirements.txt
python imgur_migrate.py -h
```

## Usage

### Help

```bash
imgur-migrate -h
```

### Modes

- `wikilink`: `![[file-1.png]]`
- `mdlink`: `![alt](file-1.png)`

```bash
imgur-migrate --mode wikilink
imgur-migrate --mode mdlink
```

Default mode is `wikilink`.

### Process a directory

```bash
imgur-migrate
imgur-migrate /path/to/notes
```

### Process one file

```bash
imgur-migrate /path/to/notes "README.md"
```

### Save images to a subfolder

```bash
imgur-migrate /path/to/notes --images-dir assets/img
```

## Limitations

- Only Imgur links matching `https://i.imgur.com/...` are replaced.
- Only Markdown image syntax `![](...)` / `![alt](...)` is processed.
- Links inside code blocks or inline code are not excluded.

## Upstream Attribution

All credit for the original idea and initial implementation goes to the upstream project:
<https://github.com/dlccyes/imgur-migrate>
