import xml.etree.ElementTree as ET
from itertools import chain


def len_gen(gen):
    return sum(1 for x in gen)


def clear_emphasis(text):
    return text.replace('+', '')


def to_variants(word):
    return {clear_emphasis(x.attrib['lemma']) for x in word}


def parse(path: str):
    return ET.parse(path).getroot()


def common_filter(words):
    for word in words:
        for variant in tuple(word):
            if variant.tag != 'Variant':
                word.remove(variant)
                continue

            if ('pravapis' in variant.attrib) and ('A2008' not in variant.attrib['pravapis']):
                word.remove(variant)
                continue

        if len(word) > 0:
            yield word


def nouns_to_simple_list(words):
    for word in words:
        tags = word.attrib['tag']

        if len(tags) < 2:
            print('{} {}'.format(word.attrib['lemma'], tags))

        else:
            if tags[1] == 'P':
                continue

        yield from to_variants(word)


def adjs_to_simple_list(words):
    for word in words:
        if word.attrib['tag'][-1] in ('C', 'S'):
            continue

        yield from to_variants(word)


def verbs_to_simple_list(words):
    for word in words:
        yield from to_variants(word)


def write_to_file(filename: str, words, transformer):
    with open(filename, mode='wt') as f:
        for w in transformer(common_filter(words)):
            f.write(w)
            f.write('\n')


def build_nouns():
    nouns = chain(parse('N1.xml'), parse('N2.xml'), parse('N3.xml'))
    write_to_file('nouns.txt', nouns, nouns_to_simple_list)


def build_agjs():
    adjs = chain(parse('A1.xml'), parse('A2.xml'))
    write_to_file('adjs.txt', adjs, adjs_to_simple_list)


def build_verbs():
    verbs = parse('V.xml')
    write_to_file('verbs.txt', verbs, verbs_to_simple_list)


build_verbs()
