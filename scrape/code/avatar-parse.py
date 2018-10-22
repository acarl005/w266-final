import re
from bs4 import BeautifulSoup
from bs4 import NavigableString

from main import parse

patterns = [
    ("dialogue1", r"^<b>([\w\s#\-/'\.]+):\s*</b>\s*(.*)$"), # standard (colon inside <b>)
    ("dialogue2", r"^<b>([\w\s#\-/'\.]+)</b>\s*:\s*(.*)$"), # standard (colon outside <b>)
    ("dialogue2", r"^<b>([\w\s#\-/'\.]+)</b>\s*<b>:</b>\s*(.*)$"), # <b> around the name and another around the colon
    ("dialogue3", r"^([\w\s#\-/'\.]+)\s*:\s*(.*)$"), # no bold tags
    ("dialogue4", r"^<b>([\w\s#\-/'\.]+)</b>\s+(.*)$"), # no colon
    ("multilogue1", r"^<b>([\w\s#\-/'\.]+)</b>\s+and\s+<b>([\w\s]+)</b>:\s*(.*)$"), # two speakers (colon outside <b>)
    ("multilogue2", r"^<b>([\w\s#\-/'\.]+)</b>\s+and\s+<b>([\w\s]+):</b>\s*(.*)$"), # two speakers (colon inside <b>)
    ("blank", r"^\s*$"),
    ("act1", r"<u><b>Act I+\s*</b></u>"),
    ("act2", r"<b><u>Act I+\s*</u></b>"),
    ("dangle1", r"\."),
    ("dangle2", r"<b></b>"),
    ("credits", "\[End Credits\]")
]

split_dialogue = set([
    "you come with us? It'll be fun!",
    "Start the countdown to victory!",
    "No, Momo, ssh! Sleepy time.",
    "your Mother, get out of here!",
    "your stupid garden!  Get your grimy hind to the market and buy me some real food!",
    "swords, why don't you just do it now?",
    "of houses.  All completely buried in ash.",
    "nothing like a swamp.  What'd you reckon that is, Tho? Some sort of exploding Fire Nation exploding trap that would eat ya?",
    "we met Suki, who is a Kyoshi warrior.  She made me dress like a woman and then she kissed me",
    "lux seaweed.",
    "uninhabited, and the harbor  surrounded by cliffs seemed like the perfect secluded place.",
    "injury has weakened her.",
    "those things.  But for some reason when I meet boys they act as if I'm going to do something horrible to them.",
    "entire world.  We will dominate the Earth!",
    "distract him.",
    "really memorable?",
    "rage, and you just don't have enough anger to fuel it the way you used to.",
    "the original source.",
    "extension of my senses.  For them, the original earthbenders,  wasn't just about fighting. It was their way of interacting with the World.",
    "Maybe you can give me a lesson sometime buddy.",
    "dragons when I was a kid.",
    "would become legendary, and you'd earn the honorary title \"Dragon\".  The last great dragon was conquered long before I was born,  by my Uncle.",
    "want you to dance with me.",
    "Warrior firebending form.",
    "have made it pass the courtyard.",
    "philosophy.",
    "flame will go out.",
    "you will learn is calligraphy. Write your name.",
    "one-headed fish, or the two-headed fish?",
    "there's another way off this island.",
    "you doing here?",
    "Be in the yard in one hour.",
    "truth is,  I guess I don't know you. All I get is a letter.  You could have at",
    "least looked me in the eye when you ripped out my heart.",
    "he could fool me. But now that person",
    "says.",
    "everything through!",
    "Fire Lord before the comet comes,  there won't be a World to save anymore.",
    "through.",
    "strike me on the head.",
    "Tribe prisoners.  I'm afraid your Father's not here.",
    "Kyoshi Warriors, are they here?",
    "freedom on the slim chance that my dad is gonna show up?",
    "We have new prisoners arriving! Everything must be completely secure!",
    "And here's one that I made out of noodles!",
    "prison tower."
])

def html_page_to_structured(html_page, key):
    # html5lib is required because the default one does this undesirable thing where it truncates
    # the contents of a tag if its above a certain length
    soup = BeautifulSoup(html_page, "html5lib")
    # get the element with the transcript in it
    quote = soup.find("blockquote")
    # remove i tags because thye all seem to contain descriptions, no dialogue
    [i.decompose() for i in quote.find_all("i")]

    act_1_found = False
    quote = soup.find("blockquote")
    to_decompose = []
    to_extract = []
    for elem in quote.contents:
        if (elem.name == "u" or elem.name == "b") and elem.string and elem.string.strip() == "Act I":
            act_1_found = True
            to_decompose.append(elem)
        if not act_1_found:
            if type(elem) == NavigableString:
                to_extract.append(elem)
            else:
                to_decompose.append(elem)
    if not act_1_found:
        raise ValueError(f"Act I annotation not found for {key}")
    [elem.extract() for elem in to_extract]
    [elem.decompose() for elem in to_decompose]

    contents = quote.encode_contents().decode("utf-8")
    contents = re.sub("<br/?>", "\n", contents)
    chopped_contents = re.sub(r"\([^)\n]*(\)|\n)", "", contents)
    lines = chopped_contents.split("\n")
    data = []
    for line in lines:
        line = line.strip()
        found_match = False
        for kind, regex in patterns:
            match = re.match(regex, line)
            if match:
                found_match = True
                if "dialogue" in kind:
                    speaker = match[1].strip()
                    utterance = match[2]
                    data.append((speaker, utterance))
                elif "multilogue" in kind:
                    speaker1 = match[1].strip()
                    speaker2 = match[2].strip()
                    utterance = match[3]
                    data.append((speaker1, utterance))
                    data.append((speaker2, utterance))
                elif kind == "credits":
                    return data
                else:
                    # print(kind)
                    pass
        # these lines had an error where it was separated from its previous line of dialog
        if line in split_dialogue:
            data[-1] = (data[-1][0], data[-1][1] + " " + line)
            found_match = True
        elif line == ".)" or line == ")":
            found_match = True
        if not found_match:
            print(chopped_contents)
            if len(data) > 0:
                print(data[-1])
            raise ValueError(f"{key}\n\"{line}\"")
    print(chopped_contents)
    raise ValueError(f"no end credits annotation for {key}")

parse("avatar", html_page_to_structured)

