import json
import os
import subprocess
import re

from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction

ICON = "images/icon.svg"
MAX_RESULTS = 8
DESC_LEN = 200
STARDICT_DIR = os.path.expanduser("~/.stardict/dic")


def load_headwords():
    """Load all headwords from every .idx file in the StarDict directory."""
    words = []
    if not os.path.isdir(STARDICT_DIR):
        return words
    for dirpath, _, filenames in os.walk(STARDICT_DIR):
        for fname in filenames:
            if fname.endswith(".idx"):
                words.extend(parse_idx(os.path.join(dirpath, fname)))
    return sorted(set(words))


def parse_idx(idx_path):
    """Parse a StarDict .idx file and return headwords."""
    words = []
    with open(idx_path, "rb") as f:
        data = f.read()
    i = 0
    while i < len(data):
        end = data.index(b"\x00", i)
        words.append(data[i:end].decode("utf-8", errors="replace"))
        i = end + 1 + 8  # null + 4-byte offset + 4-byte size
    return words


def fzf_filter(query, wordlist_text):
    """Run fzf --filter against the wordlist. Returns ranked matches."""
    try:
        result = subprocess.run(
            ["fzf", "--filter", query],
            input=wordlist_text, capture_output=True, text=True, timeout=5,
        )
    except FileNotFoundError:
        return []
    return result.stdout.splitlines()


def find_near_misses(word, word_set):
    """Generate edit-distance-1 variants and return those that are real words."""
    w = word.lower()
    candidates = set()
    for i in range(len(w) + 1):
        for c in "abcdefghijklmnopqrstuvwxyz":
            candidates.add(w[:i] + c + w[i:])
    for i in range(len(w)):
        candidates.add(w[:i] + w[i + 1:])
        for c in "abcdefghijklmnopqrstuvwxyz":
            if c != w[i]:
                candidates.add(w[:i] + c + w[i + 1:])
    for i in range(len(w) - 1):
        candidates.add(w[:i] + w[i + 1] + w[i] + w[i + 2:])
    candidates.discard(w)
    return [c for c in candidates if c in word_set]


def sdcv_json(word):
    """Fetch definition for an exact word via sdcv."""
    try:
        result = subprocess.run(
            ["sdcv", "-n", "-j", "-e", "--utf8-output", word],
            capture_output=True, text=True, timeout=5,
        )
    except FileNotFoundError:
        return None
    if result.returncode != 0 or not result.stdout.strip():
        return []
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return []


def extract_header(definition_text):
    """Pull pronunciation and word class from the definition start."""
    lines = [l for l in definition_text.strip().splitlines() if l.strip()]
    if not lines:
        return "", ""

    pronunciation = ""
    for line in lines[:3]:
        match = re.search(r"/[^/]+/", line)
        if match:
            pronunciation = match.group(0)
            break

    word_class = ""
    for line in lines[:5]:
        stripped = line.strip().lower()
        if stripped in (
            "noun", "verb", "adjective", "adverb", "pronoun",
            "preposition", "conjunction", "interjection",
            "transitive verb", "intransitive verb", "prefix",
            "suffix", "combining form",
        ):
            word_class = line.strip()
            break

    return pronunciation, word_class


def extract_definitions(definition_text, limit=5):
    """Pull numbered definitions from the text."""
    defs = []
    for line in definition_text.splitlines():
        match = re.match(r"^\s*(\d+)\.\s+(.+)", line)
        if match:
            defs.append(match.group(2).strip())
            if len(defs) >= limit:
                break
    return defs


def extract_origin(definition_text):
    """Pull the ORIGIN line if present."""
    for line in definition_text.splitlines():
        if line.startswith("ORIGIN:"):
            return line
    return ""


class DictionaryExtension(Extension):
    def __init__(self):
        super().__init__()
        self.headwords = load_headwords()
        self.word_set = {w.lower() for w in self.headwords}
        self.wordlist_text = "\n".join(self.headwords)
        self.subscribe(KeywordQueryEvent, QueryListener())


class QueryListener(EventListener):
    def on_event(self, event, extension):
        keyword = event.get_keyword()
        word = (event.get_argument() or "").strip()

        if not word:
            return RenderResultListAction([
                ExtensionResultItem(
                    icon=ICON,
                    name="Type a word to look up",
                    description="Offline dictionary lookup via sdcv",
                    on_enter=HideWindowAction(),
                )
            ])

        # Try exact match
        entries = sdcv_json(word)

        if entries is None:
            return RenderResultListAction([
                ExtensionResultItem(
                    icon=ICON,
                    name="sdcv not found",
                    description="Install sdcv: sudo dnf install sdcv",
                    on_enter=HideWindowAction(),
                )
            ])

        if entries:
            return self.show_definition(keyword, word, entries, extension)

        # No exact match - use fzf + near-miss
        return self.show_suggestions(keyword, word, extension)

    def show_definition(self, keyword, word, entries, extension):
        items = []
        for entry in entries:
            defn = entry.get("definition", "")
            matched_word = entry.get("word", word)

            pronunciation, word_class = extract_header(defn)
            numbered_defs = extract_definitions(defn)
            origin = extract_origin(defn)

            title_parts = [matched_word]
            if pronunciation:
                title_parts.append(pronunciation)
            if word_class:
                title_parts.append(f"({word_class})")
            title = "  ".join(title_parts)

            if numbered_defs:
                for i, d in enumerate(numbered_defs):
                    items.append(ExtensionResultItem(
                        icon=ICON,
                        name=title if i == 0 else f"{i+1}. {d}",
                        description=f"1. {d}" if i == 0 else "",
                        highlightable=False,
                        on_enter=CopyToClipboardAction(d),
                    ))
            else:
                desc = " ".join(defn.split())
                if len(desc) > DESC_LEN:
                    desc = desc[:DESC_LEN] + "..."
                items.append(ExtensionResultItem(
                    icon=ICON,
                    name=title,
                    description=desc,
                    highlightable=False,
                    on_enter=CopyToClipboardAction(defn.strip()),
                ))

            if origin:
                items.append(ExtensionResultItem(
                    icon=ICON,
                    name="Origin",
                    description=origin.replace("ORIGIN: ", ""),
                    highlightable=False,
                    on_enter=CopyToClipboardAction(origin),
                ))

            items.append(ExtensionResultItem(
                icon=ICON,
                name=f"Open '{matched_word}' on Wiktionary",
                description="View full entry in browser",
                highlightable=False,
                on_enter=OpenUrlAction(
                    f"https://en.wiktionary.org/wiki/{matched_word}"
                ),
            ))

        # Also show other words starting with the same prefix
        fzf_matches = fzf_filter(word, extension.wordlist_text)
        seen = {word.lower()}
        for suggestion in fzf_matches:
            if len(items) >= MAX_RESULTS:
                break
            if suggestion.lower() in seen:
                continue
            seen.add(suggestion.lower())
            s_entries = sdcv_json(suggestion)
            if s_entries:
                preview = " ".join(s_entries[0].get("definition", "").split())[:DESC_LEN]
            else:
                preview = ""
            items.append(ExtensionResultItem(
                icon=ICON,
                name=suggestion,
                description=preview,
                highlightable=False,
                on_enter=SetUserQueryAction(f"{keyword} {suggestion}"),
            ))

        return RenderResultListAction(items[:MAX_RESULTS])

    def show_suggestions(self, keyword, word, extension):
        # fzf results (prefix + fuzzy, already ranked by fzf)
        fzf_matches = fzf_filter(word, extension.wordlist_text)

        # Edit-distance-1 near misses (typo correction)
        near_misses = find_near_misses(word, extension.word_set)

        # Interleave: near misses first (typo corrections), then fzf,
        # skipping any fzf results already covered by near misses
        seen = set()
        ordered = []
        near_set = {w.lower() for w in near_misses}
        # Near misses that fzf also ranks highly go first
        for w in near_misses:
            wl = w.lower()
            if wl not in seen:
                seen.add(wl)
                ordered.append(w)
        for w in fzf_matches:
            wl = w.lower()
            if wl not in seen:
                seen.add(wl)
                ordered.append(w)

        if not ordered:
            return RenderResultListAction([
                ExtensionResultItem(
                    icon=ICON,
                    name=f"No results for '{word}'",
                    description="Word not found in any dictionary",
                    on_enter=HideWindowAction(),
                )
            ])

        items = [
            ExtensionResultItem(
                icon=ICON,
                name=f"No exact match for '{word}'",
                description="Did you mean:",
                highlightable=False,
                on_enter=HideWindowAction(),
            )
        ]

        # Fetch definitions for top suggestions
        for suggestion in ordered[:MAX_RESULTS - 1]:
            entries = sdcv_json(suggestion)
            if entries:
                defn = entries[0].get("definition", "")
                preview = " ".join(defn.split())[:DESC_LEN]
            else:
                preview = ""

            items.append(ExtensionResultItem(
                icon=ICON,
                name=suggestion,
                description=preview,
                highlightable=False,
                on_enter=SetUserQueryAction(f"{keyword} {suggestion}"),
            ))

        return RenderResultListAction(items[:MAX_RESULTS])


if __name__ == "__main__":
    DictionaryExtension().run()
