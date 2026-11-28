import os
import pandas as pd
import streamlit as st
from research_tools import research_tools
from source_finder import show_guidance

st.set_page_config(page_title='Context Matters', layout='wide')
# Keep the visual design in a separate CSS file.
if os.path.exists('style.css'):
    with open('style.css', encoding='utf-8') as file:
        st.markdown('<style>' + file.read() + '</style>', unsafe_allow_html=True)

st.markdown('<div class="brand">context/matters</div>', unsafe_allow_html=True)
pages = ['Home', 'Context Switch', 'Advice Explorer', 'Your Path', 'Interactive Scenarios', 'Affordability Calculator', 'Research & Evidence']
if 'page' not in st.session_state:
    st.session_state.page = 'Home'
if 'category_choice' not in st.session_state:
    st.session_state.category_choice = 'All'
page = st.radio('Navigation', pages, horizontal=True, key='page', label_visibility='collapsed')

# Keep the Excel export beside app.py, or upload it here for local testing.
if os.path.exists('database.xlsx'):
    database = 'database.xlsx'
else:
    database = st.file_uploader('Upload the database (.xlsx)', type=['xlsx'])
if database is None:
    st.info('Export Context Matters Database from Google Sheets as an Excel workbook and upload it here, or save it as database.xlsx beside app.py.')
    st.stop()

try:
    sheets = pd.read_excel(database, sheet_name=None, dtype=str, keep_default_na=False)
    advice = sheets['Advice']
    contexts = sheets['Contexts']
    sources = sheets['Sources']
    scenarios = sheets['Scenarios']
except (ValueError, KeyError, OSError) as error:
    st.error(f'Could not read the database: {error}')
    st.stop()

countries = ['Russia', 'USA', 'France']
# Each dimension has its own status. No aggregate accessibility score.
dimensions = [
    ('Legal', 'legal_status', 'legal_conditions'),
    ('Financial', 'financial_status', 'financial_conditions'),
    ('Administrative', 'administrative_status', 'administrative_conditions'),
    ('Geographic', 'geographic_status', 'geographic_conditions'),
    ('Personal and social', 'personal_social_status', 'practical_barriers'),
]

def show_sources(ids):
    for source_id in ids.split(';'):
        matches = sources[sources['source_id'] == source_id.strip()]
        for _, source in matches.iterrows():
            st.write(source['source_id'], '-', source['institution'], '-', source['title'])
            st.caption(source.get('verification_status', 'Verification pending'))
            if source['url'].startswith(('https://', 'http://')):
                st.link_button('Open source', source['url'])

# Related profiles are evidence leads, never personal eligibility decisions.
def display_status(value):
    return 'Needs verification' if not value or value == 'Unknown' else value


def related_profiles(country, selected, age=None):
    category = advice.loc[advice['advice_id'] == selected, 'category'].iloc[0]
    ids = advice.loc[advice['category'] == category, 'advice_id']
    rows = contexts[(contexts['country'] == country) & contexts['advice_id'].isin(ids) & (contexts['advice_id'] != selected)].copy()
    if age is not None:
        rows['distance'] = (pd.to_numeric(rows['age_group'], errors='coerce') - age).abs()
        rows = rows.sort_values('distance')
    return rows.head(3)


def show_related(country, selected, age=None):
    rows = related_profiles(country, selected, age)
    st.caption('Related research leads: same topic and country, not evidence that the selected advice applies.')
    if rows.empty:
        st.write('No related profile in the current dataset. Consult an official authority for this topic before acting.')
    for _, row in rows.iterrows():
        label = advice.loc[advice['advice_id'] == row['advice_id'], 'advice'].iloc[0]
        st.markdown('**' + label + '**')
        st.caption('Reference age: ' + row['age_group'] + ' | ' + row['residency_status'])
        st.write(row['legal_conditions'])
        show_sources(row['source_ids'])


def show_dimensions(row, personal=False):
    for title, status, description in dimensions:
        value = display_status(row.get(status, ''))
        prefix = 'Reference: ' if personal else ''
        with st.expander(title + ': ' + prefix + value, expanded=personal):
            st.write(row.get(description, '') or 'No dimension-specific finding recorded.')
            if value == 'Needs verification':
                st.caption('The dataset does not establish this dimension. Review the linked evidence and check your specific circumstances.')


def explore(category='All'):
    st.session_state.page = 'Context Switch'
    st.session_state.category_choice = category

def go_to_path(goal=None, country=None):
    if goal is not None:
        st.session_state.route_goal = goal
    if country is not None:
        st.session_state.route_country = country
    st.session_state.page = 'Your Path'

if page == 'Home':
    st.markdown("""
    <div class="hero">
      <div class="kicker">THE OTHER SIDE OF ONLINE ADVICE</div>
      <div class="hero-title">Same advice.<br><span>Different<br>reality.</span></div>
      <div class="hero-copy">The internet is global.<br>Opportunities are not.</div>
      <div class="stamp">CONTEXT<br>IS KEY.</div>
    </div>
    """, unsafe_allow_html=True)
    st.write('Explore how advice about work, money and education changes depending on where you live and your circumstances.')
    st.button('Explore advice', on_click=explore, type='primary')
    st.markdown('<div class="kicker">01 / THE CONTEXT SWITCH</div><div class="feature">WHAT IF YOU LIVED ELSEWHERE?<strong>Just get a job.</strong><p>Sounds simple, right? Compare three different realities.</p></div>', unsafe_allow_html=True)
    st.button('Compare contexts', on_click=explore, args=('Career & Work',))
    st.button('Build your path', on_click=go_to_path)
    st.markdown('<div class="kicker">02 / FIND YOUR TOPIC</div>', unsafe_allow_html=True)
    for category in sorted(advice['category'].unique().tolist()):
        st.button(category, key='home_' + category, on_click=explore, args=(category,), use_container_width=True)
    st.markdown('<div class="kicker">03 / THE RESEARCH</div>', unsafe_allow_html=True)
    a, b, c = st.columns(3)
    a.metric('Advice cases', len(advice))
    b.metric('Countries', len(countries))
    c.metric('Context profiles', len(contexts))
    st.caption('Independent research prototype. Evidence checks are ongoing; this is not personalized legal or financial advice.')

elif page == 'Context Switch':
    st.markdown('<div class="section-note">01 / CONTEXT LAB</div>', unsafe_allow_html=True)
    st.header('Same advice. Different context.')
    with st.expander('Rule-based research tools'):
        research_tools()
    st.write('Explore how the same online advice changes across countries, rules and life circumstances.')
    a, b, c = st.columns(3)
    a.metric('Advice cases', len(advice))
    b.metric('Countries', len(countries))
    c.metric('Context profiles', len(contexts))
    st.caption('Research prototype. Assessments are preliminary; Needs verification means insufficient evidence. Check current official rules before acting.')
    categories = ['All'] + sorted(advice['category'].unique().tolist())
    if st.session_state.category_choice not in categories:
        st.session_state.category_choice = 'All'
    category = st.selectbox('Category', categories, key='category_choice')
    choices = advice
    if category != 'All':
        choices = advice[advice['category'] == category]
    if choices.empty:
        st.stop()
    labels = []
    advice_ids = {}
    for _, row in choices.iterrows():
        label = row['advice']
        labels.append(label)
        advice_ids[label] = row['advice_id']
    selected_label = st.selectbox('Choose advice', labels)
    selected = advice_ids[selected_label]
    case = contexts[contexts['advice_id'] == selected]
    mode = st.radio('Mode', ['Compare countries', 'My context'], horizontal=True)
    if mode == 'My context':
        st.caption('For A003 and A004, country means country of origin, not destination.')
        country = st.selectbox('Your country', countries, key='my_country')
        age = st.number_input('Your age', min_value=13, max_value=100, value=17, step=1)
        residency = st.selectbox('Your status', ['Citizen', 'International student', 'Other or unsure'])
        region = st.text_input('Region or state (optional)', key='my_region')
        match = case[case['country'] == country]
        if match.empty:
            st.info('No direct research profile yet. Explore related evidence below.')
            show_related(country, selected, age)
        else:
            row = match.iloc[0]
            expected = 'Citizen' if row['residency_status'].startswith('Citizen') else 'International student' if row['residency_status'].startswith('International') else 'Other or unsure'
            st.caption('Research profile: age ' + row['age_group'] + ' | ' + row['residency_status'] + ' | ' + row['region'])
            st.write('Age: ' + ('matches reference age' if str(age) == row['age_group'] else 'differs from reference age; age-dependent rules may differ.'))
            st.write('Residency: ' + ('matches broad reference category' if residency == expected and residency != 'Other or unsure' else 'differs or is unconfirmed; eligibility may differ.'))
            st.info('Findings below describe the research profile. Other conditions, local rules and personal eligibility still require verification.')
            show_dimensions(row, personal=True)
            st.write('Reference alternative: ' + row['alternative'])
            with st.expander('Evidence and verification', expanded=True):
                show_sources(row['source_ids'])
                st.caption('Record date: ' + row['checked_date'])
            with st.expander('Related research leads'):
                show_related(country, selected, age)
        show_guidance(st, country, selected, sources, age, region, residency)
        route_goals = {'A001': 'Learn a skill and build experience', 'A007': 'Find a first job', 'A012': 'Find a first job', 'A003': 'Study with a lower budget', 'A015': 'Study with a lower budget', 'A016': 'Study with a lower budget', 'A017': 'Learn a skill and build experience'}
        if selected in route_goals:
            st.button('Explore a general starting route', on_click=go_to_path, args=(route_goals[selected], country))
        else:
            st.button('Explore available routes', on_click=go_to_path, args=(None, country))
        st.stop()
    st.caption('The profiles below are predefined research cases, not personalized legal assessments.')
    selected_countries = st.multiselect('Compare countries', countries, default=countries)
    status_icons = {'Available': '*', 'Conditional': '~', 'Restricted': 'X', 'Unknown': '?', 'N/A': '-'}
    if selected_countries:
        summary = []
        for title, status, description in dimensions:
            item = {'Dimension': title}
            for country in selected_countries:
                match = case[case['country'] == country]
                value = 'No direct profile'
                if not match.empty:
                    value = display_status(match.iloc[0].get(status, ''))
                item[country] = value
            summary.append(item)
        st.subheader('At a glance')
        st.dataframe(pd.DataFrame(summary), hide_index=True, use_container_width=True)
        st.caption('Each dimension is assessed separately. No overall ranking is calculated.')
        st.subheader('Explore the differences')
    for country in selected_countries:
        match = case[case['country'] == country]
        if match.empty:
            with st.container(border=True):
                st.subheader(country)
                st.write('No direct profile for this advice.')
                show_related(country, selected)
                show_guidance(st, country, selected, sources)
            continue
        row = match.iloc[0]
        with st.container(border=True):
            st.subheader(country)
            st.caption(f"Age: {row['age_group']} | {row['residency_status']} | {row['region']}")
            if row['source_ids']:
                st.caption('Evidence linked; individual claims may still be pending verification.')
            else:
                st.caption('No official evidence linked yet.')
            show_dimensions(row)
            st.markdown('**Alternative or next step**')
            st.write(row['alternative'])
            show_guidance(st, country, selected, sources)
            st.markdown('**General planning prompts**')
            st.write('1. Read the legal and administrative conditions above. If they need verification, verify them before making a decision.')
            st.write('2. List what you already have: time, skills, equipment, documents and a realistic budget.')
            st.write('3. Choose one small, safe step toward the goal, such as learning a skill, preparing an application or contacting an official adviser.')
            if row['alternative']:
                st.write('4. An alternative to explore: ' + row['alternative'])
            st.caption('These are general planning prompts, not a guarantee of eligibility or success.')
            with st.expander('Evidence and verification'):
                show_sources(row['source_ids'])
                st.caption('Record date: ' + row['checked_date'])

elif page == 'Advice Explorer':
    st.markdown('<div class="section-note">02 / THE ADVICE ARCHIVE</div>', unsafe_allow_html=True)
    st.header('Advice Explorer')
    st.write('Explore the advice behind the research and its original context.')
    search = st.text_input('Search advice')
    filtered = advice[advice['advice'].str.contains(search, case=False, regex=False)]
    st.caption(f'{len(filtered)} advice cases found')
    for _, row in filtered.iterrows():
        with st.expander(row['advice']):
            st.caption(row['category'] + ' / ' + row['platform'])
            st.write(row['applicability_notes'])
            st.caption(row['verification_status'])
            if row['post_url'].startswith('https://'):
                st.link_button('Original publication', row['post_url'])

elif page == 'Your Path':
    st.markdown('<div class="section-note">03 / YOUR ROUTE</div>', unsafe_allow_html=True)
    st.header('Your goal. Your next steps.')
    st.write('Choose a goal and a country to see a practical starting route.')
    st.caption('These routes are research-based planning guides, not a personalized legal assessment.')
    if not os.path.exists('pathways.csv'):
        st.warning('Add pathways.csv next to app.py to enable this section.')
    else:
        paths = pd.read_csv('pathways.csv', dtype=str, keep_default_na=False)
        goals = sorted(paths['goal'].unique())
        default_goal = st.session_state.pop('route_goal', None)
        if default_goal in goals:
            st.session_state.path_goal = default_goal
        default_country = st.session_state.pop('route_country', None)
        if default_country in countries:
            st.session_state.path_country = default_country
        goal = st.selectbox('What do you want to do?', goals, key='path_goal')
        country = st.selectbox('Where do you live?', countries, key='path_country')
        path = paths[(paths['goal'] == goal) & (paths['country'] == country)]
        if path.empty:
            st.info('This route is not yet researched.')
        else:
            st.markdown('<div class="kicker">YOUR STARTING ROUTE</div>', unsafe_allow_html=True)
            for _, step in path.sort_values('step').iterrows():
                st.subheader(step['step'] + ' / ' + step['title'])
                st.write(step['action'])
                if step['check']:
                    st.caption('Check: ' + step['check'])
                if step['source_ids']:
                    with st.expander('Sources for this step'):
                        show_sources(step['source_ids'])
                st.divider()
            st.info('If a requirement is unclear, do not assume you are ineligible. Check the official rules and ask a qualified adviser or trusted adult when appropriate.')
            st.caption('No application outcome, job or income is guaranteed.')

elif page == 'Interactive Scenarios':
    from decision_lab import show_decision_lab
    show_decision_lab(st, scenarios, show_sources)

elif page == 'Affordability Calculator':
    st.header('The cost of independence.')
    st.markdown('<div class="section-note">BUDGET LAB / MONTHLY PLANNING</div>', unsafe_allow_html=True)
    st.caption('Illustrative adult budget. Use one currency throughout; no exchange-rate conversion.')
    currency = st.selectbox('Currency', ['EUR', 'USD', 'RUB'])
    income = st.number_input('Monthly net income and support', min_value=0.0, value=0.0)
    st.subheader('Monthly expenses')
    categories = ['Housing', 'Groceries', 'Education', 'Healthcare', 'Health insurance', 'Utilities', 'Transport', 'Phone and internet', 'Emergency savings', 'Other expenses']
    costs = {}
    left, right = st.columns(2)
    for i, name in enumerate(categories):
        with (left if i % 2 == 0 else right):
            costs[name] = st.number_input(name, min_value=0.0, value=0.0, key='budget_' + name)
    st.caption('Other expenses: clothing, entertainment, cosmetics and other costs not included above. Avoid counting the same bill twice.')
    st.subheader('One-time expenses')
    deposit = st.number_input('Housing deposit', min_value=0.0, value=0.0)
    setup = st.number_input('Moving, equipment and other initial costs', min_value=0.0, value=0.0)
    total = sum(costs.values())
    balance = income - total
    a, b, c = st.columns(3)
    a.metric('Monthly income', f'{income:,.2f} {currency}')
    b.metric('Monthly allocations', f'{total:,.2f} {currency}')
    c.metric('Monthly balance', f'{balance:,.2f} {currency}')
    st.metric('One-time costs', f'{deposit + setup:,.2f} {currency}')
    if balance < 0:
        st.warning('Your entered monthly allocations exceed your income.')
    else:
        st.info('A positive balance does not guarantee affordability. Check actual costs, irregular bills and available support.')
    st.subheader('Where the money goes')
    amounts = {'Income': income, **costs}
    maximum = max(1, *amounts.values())
    for name, amount in amounts.items():
        width = amount / maximum * 100
        color = '#2536D9' if name == 'Income' else '#F5A8CD'
        st.markdown(f'<div class="budget-row"><div class="budget-label">{name}<span>{amount:,.2f} {currency}</span></div><div class="budget-track"><div style="width:{width:.4f}%;background:{color};height:18px"></div></div></div>', unsafe_allow_html=True)
    st.caption('Blue: income. Pink: monthly expenses and savings allocations. All bars use the same scale.')



else:
    st.markdown('<div class="section-note">06 / THE EVIDENCE</div>', unsafe_allow_html=True)
    st.header('Research & Evidence')
    st.warning('Purposive, nonrepresentative sample. Not all sources or numerical estimates have been independently verified.')
    for name in ['Findings', 'Methodology', 'Economic Data', 'Sources']:
        if name in sheets:
            with st.expander(name, expanded=name == 'Findings'):
                if name == 'Economic Data':
                    st.caption('Candidate benchmarks: check units, populations, dates and source verification before comparing.')
                st.dataframe(sheets[name], hide_index=True, use_container_width=True)
