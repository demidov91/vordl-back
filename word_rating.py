from requests import Session


session = Session()


def rate_file(filename):
    with open(f'data/{filename}.txt', 'rt') as cyr_file:
        with open(f'data/{filename}.lac.txt', 'rt') as lac_file:
            with open(f'data/{filename}.rate.txt', 'wt') as rate_file:
                for cyr, lac in zip(cyr_file.readlines(), lac_file.readlines()):
                    cyr = cyr.rstrip('\n')
                    lac = lac.rstrip('\n')
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
                    resp = session.post('https://bnkorpus.info/rest/korpus/search', json=data, timeout=10)
                    if resp.status_code != 200:
                        raise ValueError(resp.text)

                    resp_data = resp.json()
                    if 'foundIDs' not in resp_data:
                        raise ValueError(resp_data)

                    line = f'{lac} {cyr} {len(resp_data["foundIDs"])}\n'
                    print(line, end='')
                    rate_file.write(line)
