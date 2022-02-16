import xml.etree.ElementTree as ET
from itertools import chain


def len_gen(gen):
    return sum(1 for x in gen)


def simplify_writing(text):
    return text.replace('+', '').lower()


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


class BaseFilter:
    def __init__(self, words):
        self._words = words

    def is_good_word(self, tag: str):
        return True

    def is_good_lemma(self, tag: str):
        return True

    def is_good_form(self, tag: str):
        return False

    def nowadays_words(self):
        return common_filter(self._words)

    def to_lemmas(self, word):
        if not self.is_good_lemma(word.attrib.get('tag')):
            return set()

        return {simplify_writing(x.attrib['lemma']) for x in word}

    def to_forms(self, word):
        forms = set()

        for variant in word:
            for form in variant:
                if form.tag != 'Form':
                    continue

                if self.is_good_form(form.attrib['tag']):
                    forms.add(simplify_writing(form.text))

        return forms

    def convert_word(self, word):
        lemmas = self.to_lemmas(word)
        forms = self.to_forms(word)
        forms -= lemmas
        for lemma in lemmas:
            yield lemma, False

        for form in forms:
            yield form, True

    def convert(self):
        for word in filter(self.is_good_word, self.nowadays_words()):
            yield from self.convert_word(word)


class NounFilter(BaseFilter):
    def is_good_word(self, tag: str):
        return len(tag) < 6 or (tag[6] not in ['S', 'U'])

    def is_good_form(self, tag: str):
        return (tag[0] == 'N') and (tag[1] == 'P')


class AdjectiveFilter(BaseFilter):
    def is_good_lemma(self, tag: str):
        return tag[-1] not in ('C', 'S')

    def is_good_form(self, tag: str):
        return len(tag) > 1 and tag[1] == 'N'


def write_to_file(filename: str, word_filter: BaseFilter):
    with open(f'data/{filename}.txt', mode='wt') as lemma_file:
        with open(f'data/{filename}-forms.txt', mode='wt') as form_file:
            for w, is_form in word_filter.convert():
                f = form_file if is_form else lemma_file
                f.write(w)
                f.write('\n')


def build_nouns():
    nouns = chain(parse('N1.xml'), parse('N2.xml'), parse('N3.xml'))
    write_to_file('nouns', NounFilter(nouns))


def build_agjs():
    adjs = chain(parse('A1.xml'), parse('A2.xml'))
    write_to_file('adjs', AdjectiveFilter(adjs))


def build_verbs():
    verbs = parse('V.xml')
    write_to_file('verbs', BaseFilter(verbs))



build_nouns()
build_agjs()
build_verbs()
