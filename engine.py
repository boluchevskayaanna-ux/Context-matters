# Context Matters — Engine
# Preliminary research data, not verified legal advice.

from data_loader import load_rules
from regional import check_region

rules = load_rules()


def find_rule(country, age):
    for rule in rules:
        if rule['country'] == country and rule['min_age'] <= age <= rule['max_age']:
            return rule
    return None


def analyze_advice(country, age, period, schedule, consent=None, permit=None, state=None):
    # schedule contains hours for Monday through Sunday.
    if len(schedule) != 7 or period not in ['School', 'Holiday']:
        return {'status': 'Unknown', 'reasons': ['Invalid period or schedule.']}
    for hours in schedule:
        if hours < 0 or hours > 24:
            return {'status': 'Unknown', 'reasons': ['Invalid daily hours.']}
    rule = find_rule(country, age)
    if rule is None or sum(schedule) == 0:
        return {'status': 'Unknown', 'reasons': ['No matching rule or no planned work.']}

    weekly_limit, daily_limit = rule[period]
    reasons = []
    restricted = False
    if weekly_limit is not None and sum(schedule) > weekly_limit:
        reasons.append('Weekly limit exceeded.')
        restricted = True
    for day in range(7):
        limit = daily_limit
        # US federal school-week limit: 3 hours on school days,
        # 8 on nonschool days. Assume Monday-Friday are school days.
        if country == 'USA' and age < 16 and period == 'School' and day >= 5:
            limit = 8
        if limit is not None and schedule[day] > limit:
            reasons.append('Daily limit exceeded on day ' + str(day + 1) + '.')
            restricted = True
    if rule['consent'] is True and consent is not True:
        reasons.append('Required guardian consent not confirmed.')
    if rule['permit'] is True and permit is not True:
        reasons.append('Required work authorization not confirmed.')
    if rule['consent'] is None or rule['permit'] is None:
        reasons.append('Consent or permit rules need further context.')
    if country == 'USA':
        reasons.append('State rules and FLSA coverage must be checked.')
    if country == 'France' and age < 16:
        reasons.append('Holiday duration and required rest must be checked.')
    reasons.append('Job type, education status, rest and other conditions are not fully checked.')
    preliminary = 'Conditional'
    if restricted:
        preliminary = 'Restricted'
    elif weekly_limit is None:
        preliminary = 'Unknown'
    regional = None
    if country == 'USA':
        regional = check_region(state, age, period, schedule)
        if regional['status'] == 'Restricted':
            preliminary = 'Restricted'
        reasons.append(regional['reason'])
    # Do not turn preliminary research into a definitive legal result.
    return {'status': 'Unknown', 'preliminary_status': preliminary,
            'evidence': rule['evidence'], 'reasons': reasons,
            'weekly_limit': weekly_limit, 'daily_limit': daily_limit,
            'regional': regional, 'planned_hours': sum(schedule), 'source_ids': rule['source']}


if __name__ == '__main__':
    for country in ['Russia', 'France', 'USA']:
        result = analyze_advice(country, 15, 'School', [2, 2, 2, 2, 2, 0, 0])
        print(country, result)
