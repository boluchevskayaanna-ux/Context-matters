from data_loader import read_csv


def analyze_business(country, kind, age):
    for rule in read_csv('entrepreneurship_rules.csv'):
        if rule['country'] == country and rule['kind'] == kind:
            result = {'status': 'Unknown', 'rule': rule['rule'],
                      'source': rule['source'], 'evidence': rule['evidence']}
            if rule['min_age'] and age < int(rule['min_age']):
                result['preliminary_status'] = 'Restricted'
            return result
    return {'status': 'Unknown', 'rule': 'No matching rule'}
