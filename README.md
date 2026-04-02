# Dicky

Offline dictionary for [Ulauncher](https://ulauncher.io/). Type `d word` and get instant definitions, no internet needed.

Uses [sdcv](https://github.com/huzheng001/stardict-3) (StarDict console dictionary) for lookups and [fzf](https://github.com/junegunn/fzf) for fuzzy search.

![Screenshot](screenshot.png)

## Features

- Instant offline lookups from any StarDict dictionary
- Fuzzy search and autocomplete as you type (powered by fzf)
- Typo correction via edit-distance matching
- Case-insensitive matching
- Numbered definitions shown as separate items
- Etymology/origin displayed where available
- Copy definition to clipboard on Enter
- Link to Wiktionary for the full entry
- Works with multiple dictionaries simultaneously

## Requirements

- [Ulauncher](https://ulauncher.io/) v5 or v6
- [sdcv](https://github.com/huzheng001/stardict-3) (StarDict console dictionary)
- [fzf](https://github.com/junegunn/fzf) (fuzzy finder)
- One or more StarDict dictionaries

## Install

### 1. Install sdcv and fzf

**Fedora/RHEL:**

```bash
sudo dnf install sdcv fzf
```

**Ubuntu/Debian:**

```bash
sudo apt install sdcv fzf
```

**Arch:**

```bash
sudo pacman -S sdcv fzf
```

### 2. Install a dictionary

Dicky works with any dictionary in [StarDict format](https://github.com/huzheng001/stardict-3/blob/master/dict/doc/StarDictFileFormat). You need at least one. Install as many as you like and Dicky will search them all.

#### Free dictionaries

**GCIDE (GNU Collaborative International Dictionary of English)** - free, comprehensive English dictionary. Available from [gcide.gnu.org.ua](https://gcide.gnu.org.ua/).

**Wiktionary exports** - community-maintained, regularly updated:

- [dictinfo.com](https://www.dictinfo.com/) (English Wiktionary in StarDict format)
- [Vuizur/Wiktionary-Dictionaries](https://github.com/Vuizur/Wiktionary-Dictionaries) on GitHub

**CC-CEDICT** - the standard free Chinese-English dictionary, widely available in StarDict format.

**JMDict/EDICT** - the standard free Japanese-English dictionary.

**FreeDict** - open-source bilingual dictionaries for many language pairs at [freedict.org](https://freedict.org/).

#### Commercial dictionaries

StarDict versions of well-known commercial dictionaries can be found online. Dicky works with all of them. Some popular ones people use:

| Language | Dictionaries |
|---|---|
| English | Chambers, Collins, Oxford, Longman, Cambridge |
| English (American) | Merriam-Webster, American Heritage |
| Spanish | Collins Spanish-English, Oxford Spanish-English, VOX |
| Chinese | Oxford Chinese-English, Xiandai Hanyu Cidian |
| French | Le Petit Robert, Collins Robert, Larousse |
| German | Duden, Langenscheidt, PONS |

Larger collections of StarDict dictionaries (including commercial ones) are available at community mirror sites. Search for "StarDict dictionary download" or "stardict bigdict".

#### Where to put them

Place dictionary files in `~/.stardict/dic/`. Each dictionary lives in its own subfolder containing `.ifo`, `.idx` and `.dict` (or `.dict.dz`) files.

```
~/.stardict/dic/
  my-dictionary/
    My_Dictionary.ifo
    My_Dictionary.idx
    My_Dictionary.dict.dz
```

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

- `d colour` - look up a word
- `d flocc` - autocomplete/browse words starting with "flocc"
- `d colur` - typo? suggestions appear automatically

Press Enter on a definition to copy it to clipboard. Select "Open on Wiktionary" to view the full entry online.

## Keyword

The default keyword is `d`. Change it in Ulauncher preferences under Extensions.

## Licence

MIT
