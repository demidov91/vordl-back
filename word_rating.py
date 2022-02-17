from requests import Session


class RateBuilder:
    _existing_words = None

    def __init__(self, word_len: int):
        self.word_len = word_len
        self.session = Session()

    @property
    def existing_words(self):
        if self._existing_words is None:
            words = set()
            with open(f'data/{self.word_len}.different.rate.txt') as f:
                for line in f:
                    _, word, _ = line.split(' ')
                    words.add(word)

            self._existing_words = words
            print(f'{len(self._existing_words)} exists')

        return self._existing_words

    def rate_file(self):
        with open(f'data/{self.word_len}.different.txt', 'rt') as cyr_file:
            with open(f'data/{self.word_len}.different.lac.txt', 'rt') as lac_file:
                with open(f'data/{self.word_len}.different.rate.txt', 'at') as rate_file:
                    for cyr, lac in zip(cyr_file, lac_file):
                        cyr = cyr.rstrip('\n')
                        lac = lac.rstrip('\n')

                        if cyr in self.existing_words:
                            continue

                        data = {
                            'params': {
                                'textStandard': {
                                    'subcorpuses': ['teksty', 'pieraklady'],
                                },
                                'words': [
                                    {
                                        'allForms': False,
                                        'grammar': None,
                                        'word': cyr,
                                    },
                                ],
                                'wordsOrder': 'PRESET',
                            },
                        }
                        resp = self.session.post('https://bnkorpus.info/rest/korpus/search', json=data, timeout=10)
                        if resp.status_code != 200:
                            raise ValueError(resp.text)

                        resp_data = resp.json()
                        if 'foundIDs' not in resp_data:
                            raise ValueError(resp_data)

                        line = f'{lac} {cyr} {len(resp_data["foundIDs"])}\n'
                        print(line, end='')
                        rate_file.write(line)


builder = RateBuilder(5)
builder.rate_file()
