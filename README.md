# Dicky

Offline dictionary for [Ulauncher](https://ulauncher.io/). Type `d word` and get instant definitions, no internet needed.

Uses [sdcv](https://github.com/huzheng001/stardict-3) (StarDict console dictionary) for lookups.

![Looking up "colour" in GCIDE](screenshot-gcide-colour.webp)
![Looking up "color" in GCIDE](screenshot-gcide-color.webp)
![Switching between dictionaries](screenshot-dictionaries.webp)

## Features

- Instant offline lookups from any StarDict dictionary
- Prefix search and autocomplete as you type
- Typo correction via edit-distance matching
- Switch between installed dictionaries from within Ulauncher
- Case-insensitive matching
- Numbered definitions shown as separate items
- Etymology/origin displayed where available
- Copy definition to clipboard on Enter
- Link to Wiktionary for the full entry

## Requirements

- [Ulauncher](https://ulauncher.io/) v5 or v6
- [sdcv](https://github.com/huzheng001/stardict-3) (StarDict console dictionary)
- One or more StarDict dictionaries

## Install

### 1. Install sdcv

**Fedora/RHEL:**

```bash
sudo dnf install sdcv
```

**Ubuntu/Debian:**

```bash
sudo apt install sdcv
```

**Arch:**

```bash
sudo pacman -S sdcv
```

### 2. Install a dictionary

Dicky works with any dictionary in StarDict format. You need at least one.

#### Recommended: Wiktionary from dictinfo.com

The easiest way to get started. [dictinfo.com](https://www.dictinfo.com/) provides regularly updated Wiktionary exports in StarDict format, ready to use. The English-only version (40 MB download) covers 1.3 million headwords. There are also all-languages (8 million headwords) and Western-languages versions if you want broader coverage.

Download a `.7z` file from the site, then extract and install it:

```bash
# Install 7z if you don't have it
# Fedora: sudo dnf install p7zip-plugins
# Ubuntu: sudo apt install p7zip-full
# Arch: sudo pacman -S p7zip

# Extract the archive
7z x wikt-en-en-2025-10-05.7z

# The extracted files might land in the current directory rather than a subfolder.
# You need a subfolder in the dictionary directory. Create it and move the files:
mkdir -p ~/.stardict/dic/wikt-en-en
mv wikt-en-en-2025-10-05.ifo wikt-en-en-2025-10-05.idx wikt-en-en-2025-10-05.dict.dz ~/.stardict/dic/wikt-en-en/
```

#### GCIDE

The GNU Collaborative International Dictionary of English. Based on Webster's 1913, comprehensive and well-formatted. Available in StarDict format from the [stardict.uber.space archive](https://stardict.uber.space/dict.org/index.html). Download the `.tar.bz2` file and extract:

```bash
tar -xjf stardict-dictd_www.dict.org_gcide-2.4.2.tar.bz2 -C ~/.stardict/dic/
```

#### Other free dictionaries

**FreeDict** - open-source bilingual dictionaries for many language pairs at [freedict.org](https://freedict.org/).

**CC-CEDICT** - the standard free Chinese-English dictionary, widely available in StarDict format.

**JMDict/EDICT** - the standard free Japanese-English dictionary.

#### More dictionaries

The [stardict.uber.space](https://stardict.uber.space/index.html) archive has a large collection of StarDict dictionaries across many languages, preserved from the original StarDict download site after it went offline in 2023.

#### Where to put them

sdcv looks for dictionaries in two places:

- `~/.stardict/dic/` (per-user, recommended)
- `/usr/share/stardict/dic/` (system-wide)

Either works. Each dictionary needs its own subfolder containing `.ifo`, `.idx` and `.dict` (or `.dict.dz`) files:

```
~/.stardict/dic/
  wikt-en-en/
    wikt-en-en-2025-10-05.ifo
    wikt-en-en-2025-10-05.idx
    wikt-en-en-2025-10-05.dict.dz
```

If `~/.stardict/dic/` doesn't exist, create it:

```bash
mkdir -p ~/.stardict/dic
```

Some archives extract into a subfolder automatically (`.tar.bz2` files usually do). Others (`.7z` files from dictinfo.com) extract the files flat into the current directory, so you need to create the subfolder yourself and move the files in. Check what you got after extracting.

### Multiple dictionaries

If you have several dictionaries installed, you can switch between them from within Ulauncher.

Type `d` with no word to see a list of all installed dictionaries. Select one to make it active.

Your choice is saved to `~/.config/dicky/active_dict` and persists across restarts.

### 3. Verify sdcv works

```bash
sdcv "hello"
```

If this shows a definition, you're good.

### 4. Install the extension

Open Ulauncher preferences, go to Extensions, click "Add extension" and paste:

```
https://github.com/no-faff/ulauncher-dicky
```

## Usage

Open Ulauncher and type:

- `d` - see installed dictionaries, switch between them
- `d colour` - look up a word
- `d flocc` - autocomplete/browse words starting with "flocc"
- `d colur` - typo? suggestions appear automatically

Press Enter on a definition to copy it to clipboard. Select "Open on Wiktionary" to view the full entry online.

## Keyword

The default keyword is `d`. Change it in Ulauncher preferences under Extensions.

## Dictionary formatting

StarDict dictionaries vary wildly in how they store definitions. Dicky includes parsing tweaks for several formats to make them display cleanly:

- **GCIDE**: decodes accent markup (`Zoöl.` instead of `Zo["o]l.`), joins multi-line definitions, strips source markers and duplicate entries

Long definitions overflow onto a second line in smaller text. This is a workaround for Ulauncher's fixed-width items - there's no way to wrap text within a single result, so Dicky splits the definition across the title and description fields.

If your dictionary looks messy or definitions are cut off in odd places, [open an issue](https://github.com/no-faff/ulauncher-dicky/issues/new) with a screenshot and the dictionary name. These formatting problems are usually fixable, sometimes in ways you wouldn't expect.

## Licence

MIT
