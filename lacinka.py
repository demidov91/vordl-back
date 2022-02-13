import re


cyr_to_lac_vow = {
    'ю': 'u',
    'е': 'e',
    'і': 'i',
    'ё': 'o',
    'я': 'a',
    'у': 'u',
    'э': 'e',
    'ы': 'y',
    'о': 'o',
    'а': 'a',
}

cyr_to_lac_polot_cons = {
    'ц': 'ć',
    'н': 'ń',
    'з': 'ź',
    'л': 'ĺ',
    'с': 'ś',
}


cyr_to_lac_cons = {
    'й': 'j',
    'ц': 'c',
    'к': 'k',
    'н': 'n',
    'г': 'h',
    'ш': 'š',
    'ў': 'ŭ',
    'з': 'z',
    'х': 'ch',
    #"'": 'j',
    'ф': 'f',
    'в': 'v',
    'п': 'p',
    'р': 'r',
    'л': 'l',
    'д': 'd',
    'ж': 'ž',
    'ч': 'č',
    'с': 's',
    'м': 'm',
    'т': 't',
    'б': 'b',
}


def vowel_replace(prefix=''):
    if prefix not in ['', 'i', 'j']:
        raise ValueError(prefix)

    def _inner(match):
        orig = match.string[match.start():match.end()]
        orig = orig.lstrip("'")
        if len(orig) != 1:
            raise ValueError(orig, match.string)

        res = cyr_to_lac_vow[orig]
        return f'{prefix}{res}'

    return _inner


def polot_cons_replace(match):
    return cyr_to_lac_polot_cons[match.string[match.start():match.end()-1]]


def cons_replace(match):
    return cyr_to_lac_cons[match.string[match.start():match.end()]]


def convert(word: str) -> str:
    word = re.sub(r'\A[юеёя]', vowel_replace('j'), word)
    word = re.sub(r"'[юеёяі]", vowel_replace('j'), word)
    word = re.sub(r"(?<=[юеёяіуэыоаў\-])[юеёя]", vowel_replace('j'), word)
    word = re.sub(r'[юеёя]', vowel_replace('i'), word)
    word = re.sub(r'[іуэыоа]', vowel_replace(), word)
    word = re.sub('[цнзлс]ь', polot_cons_replace, word)
    word = re.sub(f"[{''.join(cyr_to_lac_cons.keys())}]", cons_replace, word)

    return word


def convert_file(filename: str):
    with open(f'data/{filename}.txt', mode='rt') as in_file:
        with open(f'data/{filename}.lac.txt', mode='wt') as out_file:
            for word in in_file.readlines():
                out_file.write(convert(word))


convert_file('verbs')