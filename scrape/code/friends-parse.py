import re
from bs4 import BeautifulSoup
import sys

from main import parse

patterns = [
    ("multilogue2.1", r"^<strong>([\w\s#\-/'\.]+)\s+and\s+([\w\s#\-/'\.]+):?</strong>\s*(.*)$"),
    ("multilogue2.2", r"^<strong>([\w\s#\-/'\.]+)\s+and\s+</strong><b>([\w\s#\-/'\.]+):</b>\s*(.*)$"),
    ("multilogue2.3", r"^<b>([\w\s#\-/'\.]+)\s+and\s+<b>([\w\s#\-/'\.]+):</b>\s*</b>\s*(.*)$"),
    ("multilogue3.1", r"^<strong>([\w\s#\-/'\.]+),\s*([\w\s#\-/'\.]+),?\s+and\s+([\w\s#\-/'\.]+):?</strong>\s*(.*)$"), # three speakers
    ("multilogue3.2", r"^<strong>([\w\s#\-/'\.]+),\s*([\w\s#\-/'\.]+),?\s+and\s*</strong>\s*<b>([\w\s#\-/'\.]+):?</b>\s*(.*)$"),
    ("multilogue3.3", r"^<b>([\w\s#\-/'\.]+),\s*([\w\s#\-/'\.]+),?\s+and\s+([\w\s#\-/'\.]+):?\s*</b>\s*(.*)$"), # three speakers
    ("multilogue4.1", r"^<strong>([\w\s#\-/'\.]+),\s*([\w\s#\-/'\.]+),\s*([\w\s#\-/'\.]+),?\s+and\s+([\w\s#\-/'\.]+):?</strong>\s*(.*)$"), # 4 speakers
    ("multilogue4.2", r"^<b>([\w\s#\-/'\.]+),\s*([\w\s#\-/'\.]+),\s*([\w\s#\-/'\.]+),?\s+and\s+([\w\s#\-/'\.]+):?</b>\s*(.*)$"), # 4 speakers
    ("dialogue1", r"^<b>([\w\s#\-/'\.]+)\s*:\s*</b>\s*(.*)$"),
    ("dialogue2", r"^<b>([\w\s#\-/'\.]+)\s*</b>\s*:\s*(.*)$"),
    ("dialogue3", r"^<strong>([\w\s#\-/'\.]+)\s*:\s*</strong>\s*(.*)$"),
    ("dialogue4", r"^<strong>([\w\s#\-/'\.]+)\s*</strong>\s*:\s*(.*)$"),
    ("dialogue5", r"^<strong><strong>([\w\s#\-/'\.]+):\s*</strong>\s*</strong>\s*(.*)$"),
    ("dialogue5", r"^<b><b>([\w\s#\-/'\.]+):\s*</b>\s*</b>\s*(.*)$"),
    ("dialogue5", r"^<strong><b>([\w\s#\-/'\.]+):\s*</b></strong>\s*(.*)$"),
    ("blank1", r"^\s*$"),
    ("blank2", r"^<b></b>$"),
    ("blank2", r"^<strong></strong>$"),
    ("header1", r"^(Written|Teleplay|Directed|Story) by"),
    ("header3", r"^(<b>)?Originally written"),
    ("caption1", r"^\[[^\]]+\]"),
    ("caption2", r"^\([^\)]+\)"),
    ("caption3", r"^\{[^\}]+\}"),
    ("commercial", r"^<(strong|b)>\s*Commercial Break\s*</(strong|b)>"),
    ("creds1", r"^<(strong|b)>\s*\w+ Credits\.?\s*</(strong|b)>"),
    ("creds2", r"^\w+ Credits\.?$"),
    ("end", r"^<(strong|b)>(The )?End\s*</(strong|b)>"),
    ("end", r"^(The )?End$"),
    ("epoch", r"^<strong>Thanksgiving \d+</strong>"),
]

garbage = set([
    "<strong>Dedicated to the People of New York City</strong>",
    "<strong>Dedicated to the Memory of Pearl Harmon</strong>",
    "<strong>Dedicated to the Memory of Richard L. Cox, Sr.</strong>",
    "Dedicated to the great work of Eric Aasen, Guineapig and many, many more.",
    "Dedicated to the great work of Eric Aasen, Guineapig and many, many more",
    "<b>To Be Continued......</b>",
    "<strong>To Be Continued</strong>",
    "<strong>TIME LAPSE</strong>",
    "TIME LAPSE",
    "<b>The Next Morning</b>",
    "Commercial Break",
    "Commercial Break.",
    "COMMERCIAL BREAK",
    "<strong>Commerical Break</strong>",
    "OPENING SEQUENCE",
    "Ross and Rachels Apartment",
    "Ross and Rachel while looking at each other surprised and shocked: Jill?",
    "Woman at door in a sing song voice: Amy.",
    "Ross with a look of wondering how long this is going to go on on his face: Still me.",
    "Ross starts talking over her 'do you remember' line: Amy. I'm going to save you some time, ok.  All me.",
    "Monica and Chandler's Apartment.",
    "Monica and Chandler's apartment",
    "Ross and Rachel's Apartment.",
    "Sorry.",
    "Later in the day.",
    "Later on.",
    "Ross makes some sort of sound to let us know it hurt.",
    "Monica opens her front door. Chandler is sitting in the hallway.",
    "Back to Monica and Chandler's apartment.",
    "Amy is sitting on a chair by the bay window looking mad.",
    "Monica and Chandler come through the front door.",
    "Ross walks away with a face of yeah ok.",
    "<strong>Present Day</strong>",
    "<strong>[INTRO]</strong>",
    "CUT TO: Monica and Chandler's apartment.",
    "<strong>FADE OUT</strong>",
    ".",
    "<strong>Six Weeks Earlier</strong>",
])

def html_page_to_structured(html_page, key):
    if len(sys.argv) > 1:
        filter_key = sys.argv[1]
        if key != filter_key:
            return []
    # html5lib is required because the default one does this undesirable thing where it truncates
    # the contents of a tag if its above a certain length
    soup = BeautifulSoup(html_page, "html5lib")
    body = soup.find("body")
    # remove i tags because thye all seem to contain descriptions, no dialogue
    [i.replaceWithChildren() for i in body.find_all("font")]

    paragraphs = body.select("p")
    data = []

    for p in paragraphs:
        for i in p.select("i"):
            i.replaceWithChildren()
        for span in p.select("span"):
            span.replaceWithChildren()
        for a in p.select("a"):
            a.decompose()
        for br in p.select("br"):
            br.decompose()
        raw_string = p.encode_contents().decode("utf-8").strip()
        raw_string = re.sub(r"\s+", " ", raw_string)
        raw_string = re.sub(r"\([^\)]+\)", "", raw_string).strip()
        raw_string = re.sub(r"<b></b>", "", raw_string).strip()
        raw_string = re.sub(r"oo+", "oo", raw_string)
        # raw_string = re.sub(r"&#146;", "'", raw_string)
        # raw_string = re.sub(r"&quot;", '"', raw_string)
        # raw_string = re.sub(r"&amp;", "and", raw_string)
        found_match = False
        for kind, regex in patterns:
            match = re.match(regex, raw_string, re.IGNORECASE)
            if match and not found_match:
                found_match = True
                if "dialogue" in kind:
                    speaker = match[1].strip()
                    utterance = replace_tags_with_their_inner_text(match[2])
                    data.append((speaker, utterance))
                elif "multilogue3." in kind:
                    speaker1 = match[1].strip()
                    speaker2 = match[2].strip()
                    speaker3 = match[3].strip()
                    utterance = replace_tags_with_their_inner_text(match[4])
                    data.append((speaker1, utterance))
                    data.append((speaker2, utterance))
                    data.append((speaker3, utterance))
                elif "multilogue4." in kind:
                    speaker1 = match[1].strip()
                    speaker2 = match[2].strip()
                    speaker3 = match[3].strip()
                    speaker4 = match[4].strip()
                    utterance = replace_tags_with_their_inner_text(match[5])
                    data.append((speaker1, utterance))
                    data.append((speaker2, utterance))
                    data.append((speaker3, utterance))
                    data.append((speaker4, utterance))
                elif kind == "end":
                    return data
                else:
                    pass

        if raw_string in garbage:
            found_match = True
        if not found_match:
            print(p.contents)
            if len(data) > 0:
                print(data[-1])
            raise ValueError(f"{key}\n\"{raw_string}\"")
    raise ValueError("no end annotation found for: " + key)

def replace_tags_with_their_inner_text(text):
    return BeautifulSoup(text, "html5lib").get_text()

parse("friends", html_page_to_structured)

