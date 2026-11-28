import csv
from pathlib import Path

DATA = Path(__file__).parent / 'data'


def read_csv(filename):
    with open(DATA / filename, encoding='utf-8-sig', newline='') as file:
        return list(csv.DictReader(file))


def number(value):
    if value == '':
        return None
    return float(value)


def boolean(value):
    if value == 'True':
        return True
    if value == 'False':
        return False
    return None


def load_rules():
    rules = []
    for row in read_csv('employment_rules.csv'):
        rule = {
            'country': row['country'],
            'min_age': int(row['min_age']),
            'max_age': int(row['max_age']),
            'School': (number(row['school_weekly']), number(row['school_daily'])),
            'Holiday': (number(row['holiday_weekly']), number(row['holiday_daily'])),
            'consent': boolean(row['consent']),
            'permit': boolean(row['permit']),
            'source': row['source'],
            'evidence': row['evidence']
        }
        rules.append(rule)
    return rules


def load_sources():
    return read_csv('sources.csv')


def load_regions():
    return read_csv('regional_rules.csv')
