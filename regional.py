from data_loader import load_regions, number


def find_region(state):
    for row in load_regions():
        if row['state'] == state:
            return row
    return None


def check_region(state, age, period, schedule):
    row = find_region(state)
    if row is None:
        return {'status': 'Unknown', 'reason': 'State not selected or not found.'}
    key = 'school_weekly_14_15'
    if age >= 16:
        key = 'school_weekly_16_17'
    if period == 'Holiday':
        if age < 16:
            key = None
        else:
            key = 'holiday_weekly_16_17'
    limit = None
    if key is not None:
        limit = number(row[key])
    status = 'Unknown'
    if limit is not None:
        status = 'Conditional'
        if sum(schedule) > limit:
            status = 'Restricted'
    return {'status': status, 'weekly_limit': limit,
            'source_ids': row['source_ids'], 'evidence': 'Provisional',
            'reason': 'Selected weekly rule only; exceptions and other state rules not checked.'}
