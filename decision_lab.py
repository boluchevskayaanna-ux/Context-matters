import random

READINESS = {
    'Budgeting': ['Estimate recurring expenses before making a commitment', 'Distinguish one-time costs from monthly costs', 'Compare total costs rather than advertised prices', 'Identify a trusted person to ask about financial questions'],
    'Research': ['Find an official source for a rule', 'Check the date and jurisdiction of information', 'Compare two independent sources', 'Recognize when advice lacks evidence'],
    'Planning': ['Break a goal into manageable steps', 'Track application deadlines', 'Allow time for unexpected delays', 'Identify an alternative if a plan changes'],
    'Support and administration': ['Know whom to contact for school or work questions', 'Identify documents needed for an application', 'Recognize suspicious requests for personal information', 'Ask a trusted adult or institution for help when needed'],
    'Everyday organization': ['Plan meals and routine expenses', 'Organize appointments and commitments', 'Find reliable transport information', 'Balance study, rest and other responsibilities'],
}
INTERESTS = {
    'Economics and data': ['Compare why prices differ across countries', 'Find patterns in a dataset', 'Evaluate the costs and benefits of a public policy', 'Explain a chart to someone else'],
    'Technology': ['Build a small digital tool', 'Debug a simple program', 'Organize information in a database', 'Design an accessible website'],
    'Society and policy': ['Compare education systems', 'Discuss competing policy proposals', 'Investigate how institutions work', 'Organize a community initiative'],
    'Business and organization': ['Research what customers need', 'Plan a project budget', 'Coordinate a team project', 'Evaluate whether a service solves a real problem'],
    'Creative communication': ['Design a visual explanation', 'Write an article for a specific audience', 'Develop a presentation', 'Create an educational video or story'],
    'Science and environment': ['Investigate a scientific question', 'Compare environmental evidence', 'Design a small experiment', 'Explain how a natural system works'],
}
PROJECTS = {
    'Economics and data': 'Compare two countries using public statistics and create a chart. Explore economics, statistics or public policy courses.',
    'Technology': 'Build a small website or spreadsheet tool. Explore introductory programming and information systems.',
    'Society and policy': 'Write a short policy comparison or join a supervised community project. Explore social science and international relations.',
    'Business and organization': 'Design a hypothetical service and interview potential users with appropriate permission. Explore management and entrepreneurship.',
    'Creative communication': 'Create an infographic explaining a topic you care about. Explore communication, languages or design.',
    'Science and environment': 'Analyze an open environmental dataset or do a teacher-approved experiment. Explore science and environmental studies.',
}
# Original research-literacy exercises; not jurisdiction-specific legal conclusions.
EXTRA = [
('A scholarship covers tuition but not rent. What should you compare?', 'Total attendance costs and available support', 'Tuition alone', 'Living costs can change affordability.', 'education'),
('Two universities advertise different annual fees. One excludes mandatory charges.', 'Compare all mandatory charges', 'Compare headline fees only', 'Comparable totals require the same cost categories.', 'education'),
('A course advertises a certificate. You need it for an application.', 'Check whether the receiving institution accepts it', 'Assume every certificate is accepted', 'Recognition depends on the receiving institution.', 'education'),
('An application page has last year’s deadline.', 'Find the current admission cycle or ask admissions', 'Use last year’s date as confirmed', 'Deadlines can change between cycles.', 'education'),
('A scholarship is described as fully funded in a video.', 'Read the award terms and eligibility', 'Assume every expense is covered', 'Funding descriptions may omit exclusions.', 'education'),
('A job advert asks for an upfront fee to guarantee employment.', 'Do not pay; verify the employer with a trusted adult', 'Pay immediately to secure the offer', 'Upfront fees and guarantees are warning signs.', 'work'),
('A friend says a work rule applies everywhere in a country.', 'Check national and regional rules', 'Assume every region is identical', 'Jurisdiction can affect applicable requirements.', 'work'),
('A job advert lists gross pay. You are planning a budget.', 'Check expected net pay and deductions', 'Treat gross pay as take-home pay', 'Gross and net income are different.', 'work'),
('A placement promises experience but gives no description of duties.', 'Ask for written duties and supervision details', 'Assume the title guarantees learning', 'Actual duties determine educational value.', 'work'),
('A job schedule conflicts with school commitments.', 'Discuss a suitable schedule with school and a trusted adult', 'Ignore the conflict', 'Work plans need to fit education and applicable rules.', 'work'),
('A rental advertisement excludes utilities.', 'Estimate utilities and other recurring charges', 'Budget only advertised rent', 'Rent is not the full housing cost.', 'budget'),
('A budget has monthly income of 900 and costs of 950.', 'Identify the 50-unit gap and review options', 'Assume the budget balances', '900 minus 950 equals negative 50.', 'budget'),
('A yearly fee is 1200 units.', 'Include 100 units per month and plan for the payment date', 'Ignore it in monthly planning', 'Annual costs need both allocation and cash timing.', 'budget'),
('A funded trip reimburses costs after travel.', 'Check when payment arrives and whether upfront costs are covered', 'Assume reimbursement means no upfront cost', 'Reimbursement timing affects available funds.', 'budget'),
('A price comparison uses two different currencies.', 'Use a consistent currency and dated exchange rate', 'Compare the raw numbers', 'Different currency units are not directly comparable.', 'budget'),
('A popular video cites no source for a legal claim.', 'Find the current official rule', 'Treat popularity as evidence', 'Popularity does not establish accuracy.', 'research'),
('An official page and a blog disagree.', 'Check dates, scope and the current official rule', 'Choose the more appealing answer', 'Scope and currency matter when sources conflict.', 'research'),
('A statistic compares average wages across countries.', 'Check definitions, dates and units', 'Assume the averages measure the same thing', 'Different definitions can invalidate comparisons.', 'research'),
('A recommendation is based on one person’s success.', 'Treat it as an example and check broader evidence', 'Assume it works for everyone', 'One experience cannot establish universal applicability.', 'research'),
('A volunteer opportunity has unclear age requirements.', 'Ask the organizer and a trusted adult about eligibility and supervision', 'Assume anyone can participate', 'Age and supervision requirements vary by program.', 'research'),
]
LINKS = {'education': ('EducationUSA', 'https://educationusa.state.gov/'), 'work': ('ILO — labour information', 'https://www.ilo.org/'), 'budget': ('OECD — financial education', 'https://www.oecd.org/financial/education/'), 'research': ('UNESCO — media and information literacy', 'https://www.unesco.org/en/media-information-literacy')}

def scores(groups, answers):
    return {name: sum(answers[name])/len(items) for name, items in groups.items()}

def assessment(st, groups, mode):
    interest = mode == 'Future Direction'
    options = ['Not interested', 'A little interested', 'Interested', 'Very interested'] if interest else ['Not yet', 'With help', 'Usually', 'Confidently']
    answers = {}
    with st.form('assessment_'+mode):
        for name, items in groups.items():
            st.subheader(name)
            answers[name] = [st.radio(q, options, index=None, key=mode+name+str(i)) for i,q in enumerate(items)]
        submitted = st.form_submit_button('See my results')
    if not submitted:
        return
    if any(v is None for a in answers.values() for v in a):
        st.warning('Please answer every question before viewing results.')
        return
    values = scores(groups, {k:[options.index(v) for v in a] for k,a in answers.items()})
    st.caption('Each response is worth 0–3 points. Each area is the mean of its responses. This is a reflection exercise, not a validated assessment.')
    for name,value in sorted(values.items(), key=lambda x:x[1], reverse=interest):
        st.write(name, f'{value:.2f} / 3')
        st.progress(value/3)
        if interest:
            st.write(PROJECTS[name])
        else:
            missing = [q for q,v in zip(groups[name],answers[name]) if options.index(v)<2]
            st.write('Practice next: '+ '; '.join(missing) if missing else 'Keep practicing these skills with appropriate support.')
    if interest:
        st.caption('Interest is not ability or eligibility. Explore several areas before choosing a direction.')
    else:
        st.caption('These results do not determine whether you should live independently. Age, local rules, resources and trusted support matter.')

def question_bank(scenarios):
    bank=[]
    for _,r in scenarios.iterrows():
        bank.append(dict(id=r['scenario_id'], country=r['country'], question=r['situation'], options=[r['option_a'],r['option_b']], correct=r['option_b'], feedback=r['feedback_b'], wrong=r['feedback_a'], sources=r['source_ids'], topic=''))
    for i,(q,a,b,f,t) in enumerate(EXTRA):
        bank.append(dict(id='L'+str(i),country='All',question=q,options=[a,b],correct=a,feedback=f,wrong=f,sources='',topic=t))
    return bank

def challenge(st, scenarios, show_sources):
    bank=question_bank(scenarios)
    country=st.selectbox('Context', ['All countries','Russia','USA','France'])
    pool=[q for q in bank if country=='All countries' or q['country'] in ('All',country)]
    count=st.slider('Number of questions', 5, min(30,len(pool)), min(10,len(pool)))
    config=(country,count)
    if st.button('Start / restart challenge'):
        selected=random.sample(pool,count)
        for q in selected:
            q['options']=random.sample(q['options'],len(q['options']))
        st.session_state['lab_run']=st.session_state.get('lab_run',0)+1
        st.session_state['lab_questions']=selected
        st.session_state['lab_config']=config
        st.session_state['lab_results']=None
    if st.session_state.get('lab_config')!=config:
        st.info('Start a challenge with these settings.')
        return
    questions=st.session_state['lab_questions']
    run=st.session_state['lab_run']
    with st.form('challenge_'+str(run)):
        answers=[]
        for i,q in enumerate(questions):
            answers.append(st.radio(f"{i+1}. {q['question']}",q['options'],index=None,key=f'lab_{run}_{i}'))
        submitted=st.form_submit_button('Check answers')
    if submitted:
        if any(a is None for a in answers):
            st.warning('Answer every question first.')
        else:
            st.session_state['lab_results']=answers
    results=st.session_state.get('lab_results')
    if results is not None:
        st.metric('Correct answers', f"{sum(a==q['correct'] for a,q in zip(results,questions))} / {len(questions)}")
        for i,(a,q) in enumerate(zip(results,questions)):
            with st.expander(f"{i+1}. {'Correct' if a==q['correct'] else 'Review'} — {q['question']}"):
                st.write('Your answer: '+a)
                st.write('Recommended answer: '+q['correct'])
                st.write(q['feedback'] if a==q['correct'] else q['wrong'])
                if a!=q['correct'] and q['wrong']!=q['feedback']:
                    st.write(q['feedback'])
                if q['sources']:
                    show_sources(q['sources'])
                elif q['topic']:
                    label,url=LINKS[q['topic']]
                    st.caption('Further reading — general topic resource, not direct evidence for this exercise.')
                    st.markdown(f'[{label}]({url})')
                else:
                    st.caption('Original planning exercise; no external source required.')

def show_decision_lab(st, scenarios, show_sources):
    st.markdown('<div class="section-note">04 / DECISION LAB</div>',unsafe_allow_html=True)
    st.header('What would you do?')
    mode=st.radio('Choose a tool',['Independence Readiness','Future Direction','Context Challenge'],horizontal=True)
    if mode=='Context Challenge':
        st.caption('Practice evaluating advice. Existing legal cases are research examples; verify current rules before acting.')
        challenge(st,scenarios,show_sources)
    else:
        assessment(st, INTERESTS if mode=='Future Direction' else READINESS,mode)
