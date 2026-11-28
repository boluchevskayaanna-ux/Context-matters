from data_loader import read_csv


def analyze_internship(country, kind, hours=None):
    for rule in read_csv('internship_rules.csv'):
        if rule['country'] == country and rule['kind'] == kind:
            result = {'status': 'Unknown', 'rule': rule['rule'],
                      'source': rule['source'], 'evidence': rule['evidence']}
            if country == 'France' and hours is not None and hours >= 0:
                threshold = float(rule['threshold_hours'])
                result['compensation_required'] = hours > threshold
                if hours > threshold:
                    result['minimum_eur'] = round(hours * float(rule['rate']), 2)
            return result
    return {'status': 'Unknown', 'rule': 'No matching verified classification'}
