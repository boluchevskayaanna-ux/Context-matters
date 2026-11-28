from engine import analyze_advice, find_rule
from data_loader import load_rules, load_sources

assert len(load_rules()) == 7
assert find_rule('Russia', 15)['School'] == (12, 2.5)
assert find_rule('USA', 17)['School'] == (None, None)
assert find_rule('France', 14)['consent'] is True
assert find_rule('Russia', 16)['consent'] is False
assert analyze_advice('Russia', 15, 'School', [2]*5+[0,0])['preliminary_status'] == 'Conditional'
assert analyze_advice('France', 15, 'School', [2]*5+[0,0])['preliminary_status'] == 'Restricted'
assert analyze_advice('USA', 17, 'School', [2]*5+[0,0])['status'] == 'Unknown'
ids = [s['source_id'] for s in load_sources()]
assert all(i.strip() in ids for r in load_rules() for i in r['source'].split(';'))
print('9 checks passed')

from regional import find_region, check_region
from data_loader import load_regions
assert len(load_regions()) == 51
assert len(set(row['state'] for row in load_regions())) == 51
assert find_region('District of Columbia') is not None
assert find_region('Invalid') is None
assert check_region('Florida', 15, 'School', [3]*5+[1,0])['status'] == 'Restricted'
assert check_region('Washington', 17, 'School', [4]*5+[1,0])['status'] == 'Restricted'
assert check_region('Alaska', 15, 'School', [2]*5+[0,0])['status'] == 'Unknown'
assert analyze_advice('USA', 15, 'School', [3]*5+[1,0], state='Florida')['preliminary_status'] == 'Restricted'
assert analyze_advice('USA', 15, 'School', [3]*5+[1,0], state='Florida')['status'] == 'Unknown'
print('9 additional regional checks passed')

from internships import analyze_internship
from entrepreneurship import analyze_business
assert analyze_internship('France','student',308)['compensation_required'] is False
assert analyze_internship('France','student',309)['minimum_eur'] == 1390.5
assert analyze_internship('USA','commercial')['status'] == 'Unknown'
assert analyze_internship('Russia','educational')['evidence'] == 'Provisional'
assert analyze_business('Russia','NPD',13)['preliminary_status'] == 'Restricted'
assert analyze_business('Russia','NPD',15)['status'] == 'Unknown'
assert analyze_business('USA','business',17)['evidence'] == 'Missing'
assert analyze_business('France','EURL/SASU',15)['preliminary_status'] == 'Restricted'
print('8 additional internship and business checks passed')

assert analyze_internship('France','student',309)['source'] == 'S021'
assert analyze_internship('USA','commercial')['source'] == 'S020'
assert analyze_internship('Russia','apprenticeship')['source'] == 'S172; S173'
assert analyze_business('France','EURL/SASU',16)['source'] == 'S046'
assert analyze_business('USA','business',17)['source'] == 'S171'
print('5 source alignment checks passed')
