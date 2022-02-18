import re
import shutil


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


lac_to_cyr_jot_vow = {
    'u': 'ю',
    'e': 'е',
    'i': 'і',   # I know, but it's more convenient.
    'o': 'ё',
    'a': 'я',
}


lac_to_cyr_vow = {
    'u': 'у',
    'e': 'э',
    'i': 'і',
    'o': 'о',
    'a': 'а',
    'y': 'ы',
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
    "'": '',
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


lac_to_cyr_cons = {v: k for k, v in cyr_to_lac_cons.items() if k != "'"}
lac_to_cyr_polot_cons = {v: k for k, v in cyr_to_lac_polot_cons.items()}


def vowel_replace(prefix=''):
    if prefix not in ['', 'i', 'j']:
        raise ValueError(prefix)

    def _inner(match):
        orig = match.string[match.start():match.end()]
        if len(orig) != 1:
            raise ValueError(orig, match.string)

        res = cyr_to_lac_vow[orig]
        return f'{prefix}{res}'

    return _inner


def to_cyr_vowel(jot=False):
    def _inner(match):
        mapping = lac_to_cyr_jot_vow if jot else lac_to_cyr_vow
        vowel = match.string[match.start():match.end()]
        if len(vowel) == 2:
            vowel = vowel[1:]

        return mapping[vowel]

    return _inner


def polot_cons_replace(match):
    return cyr_to_lac_polot_cons[match.string[match.start():match.end()-1]]


def cons_replace(match):
    return cyr_to_lac_cons[match.string[match.start():match.end()]]


def convert_to_lac(word: str) -> str:
    word = re.sub(r'\A[юеёя]', vowel_replace('j'), word)
    word = re.sub(r"(?<=')[юеёяі]", vowel_replace('j'), word)
    word = re.sub(r"(?<=[юеёяіуэыоаў\-])[юеёя]", vowel_replace('j'), word)
    word = re.sub(r'[юеёя]', vowel_replace('i'), word)
    word = re.sub(r'[іуэыоа]', vowel_replace(), word)
    word = re.sub('[цнзлс]ь', polot_cons_replace, word)
    word = re.sub(f"[{''.join(cyr_to_lac_cons.keys())}]", cons_replace, word)

    return word


def convert_to_cyr(word: str) -> str:
    word = re.sub(f"(?<=[{''.join(lac_to_cyr_cons.keys())}])j[aoiue]", lambda m: "'" + to_cyr_vowel(jot=True)(m), word)
    word = re.sub("[ji][aoue]", to_cyr_vowel(jot=True), word)
    word = re.sub("[aoueyi]", to_cyr_vowel(jot=False), word)
    word = re.sub('ch', 'х', word)
    word = re.sub(
        f"[{''.join(lac_to_cyr_cons.keys())}]",
        lambda m: lac_to_cyr_cons[m.string[m.start():m.end()]],
        word,
    )
    word = re.sub(
        f"[{''.join(lac_to_cyr_polot_cons.keys())}]",
        lambda m: lac_to_cyr_polot_cons[m.string[m.start():m.end()]] + 'ь',
        word,
    )

    return word


def convert_file(filename: str):
    with open(f'data/{filename}.txt', mode='rt') as in_file:
        with open(f'data/{filename}.lac.txt', mode='wt') as out_file:
            for word in in_file:
                out_file.write(convert_to_lac(word))


def build_n_words(word_length: int):
    expected_length = word_length + 1

    for filename in ['lemma', 'forms']:
        total_words = set()
        with open(f'data/{filename}.lac.txt', 'rt') as in_file:
            for line in in_file:
                if len(line) == expected_length:
                    total_words.add(line)

        with open(f'data/{word_length}.{filename}.lac.txt', 'wt') as out_file:
            for line in total_words:
                out_file.write(line)


def split_for_n_different(word_length):
    expected_length = word_length + 1
    with open(f'data/{word_length}.lemma.lac.txt', 'rt') as in_file:
        with open(f'data/{word_length}.different.lac.txt', 'wt') as d_file, open(
                f'data/{word_length}.repeat.lac.txt', 'wt'
        ) as r_file:
            for word in in_file:
                if len(set(word)) == expected_length:
                    d_file.write(word)

                else:
                    r_file.write(word)


def lacin_file_to_cyr(filename):
    with open(f'data/{filename}.lac.txt', 'rt') as in_file:
        with open(f'data/{filename}.txt', 'wt') as out_file:
            for line in in_file:
                out_file.write(convert_to_cyr(line))


def build_ask_and_acceptable(word_len: int):
    shutil.copy(f'data/{word_len}.repeat.lac.txt', f'data/{word_len}.accept.lac.txt')
    with open(f'data/{word_len}.not.ask.lac.txt', 'rt') as bad_file:
        bad_words = {x.strip() for x in bad_file}

    with open(f'data/{word_len}.accept.lac.txt', 'at') as append_file:
        with open(f'data/{word_len}.different.rate.txt', 'rt') as rate_file:
            with open(f'data/{word_len}.ask.lac.txt', 'wt') as popular_file:
                for line in rate_file:
                    lac, _, rate = line.split()
                    if int(rate) > 90 and lac not in bad_words:
                        popular_file.write(lac)
                        popular_file.write('\n')

                    else:
                        append_file.write(lac)
                        append_file.write('\n')

        with open(f'data/{word_len}.forms.lac.txt', 'rt') as forms_file:
            for line in forms_file:
                append_file.write(line)

        append_file.write('uordl\nŭordl\n')


convert_file('lemma')
convert_file('forms')
build_n_words(5)
split_for_n_different(5)
lacin_file_to_cyr('5.different')
build_ask_and_acceptable(5)
