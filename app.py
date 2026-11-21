import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title='Context Matters', layout='wide')
# Keep the visual design in a separate CSS file.
with open('style.css', encoding='utf-8') as file:
    st.markdown('<style>' + file.read() + '</style>', unsafe_allow_html=True)

st.markdown('<div class="brand">context/matters</div>', unsafe_allow_html=True)
pages = ['Home', 'Context Switch', 'Advice Explorer', 'Interactive Scenarios', 'Affordability Calculator', 'Research & Evidence']
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

def explore(category='All'):
    st.session_state.page = 'Context Switch'
    st.session_state.category_choice = category

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
    st.button('Explore advice -', on_click=explore, type='primary')
    st.markdown('<div class="kicker">01 / THE CONTEXT SWITCH</div><div class="feature">WHAT IF YOU LIVED ELSEWHERE?<strong>Just get a job.</strong><p>Sounds simple, right? Compare three different realities.</p></div>', unsafe_allow_html=True)
    st.button('Compare contexts -', on_click=explore, args=('Career & Work',))
    st.markdown('<div class="kicker">02 / FIND YOUR TOPIC</div>', unsafe_allow_html=True)
    for category in sorted(advice['category'].unique().tolist()):
        st.button(category + ' -', key='home_' + category, on_click=explore, args=(category,), use_container_width=True)
    st.markdown('<div class="kicker">03 / THE RESEARCH</div>', unsafe_allow_html=True)
    a, b, c = st.columns(3)
    a.metric('Advice cases', len(advice))
    b.metric('Countries', len(countries))
    c.metric('Context profiles', len(contexts))
    st.caption('Independent research prototype. Evidence checks are ongoing; this is not personalized legal or financial advice.')

elif page == 'Context Switch':
    st.header('Same advice. Different context.')
    st.write('Explore how the same online advice changes across countries, rules and life circumstances.')
    a, b, c = st.columns(3)
    a.metric('Advice cases', len(advice))
    b.metric('Countries', len(countries))
    c.metric('Context profiles', len(contexts))
    st.caption('Research prototype. Assessments are preliminary; Unknown means insufficient evidence. Check current official rules before acting.')
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
    st.caption('The profiles below are predefined research cases, not personalized legal assessments.')
    case = contexts[contexts['advice_id'] == selected]
    selected_countries = st.multiselect('Compare countries', countries, default=countries)
    status_icons = {'Available': '*', 'Conditional': '~', 'Restricted': 'X', 'Unknown': '?', 'N/A': '-'}
    if selected_countries:
        summary = []
        for title, status, description in dimensions:
            item = {'Dimension': title}
            for country in selected_countries:
                match = case[case['country'] == country]
                value = 'Unknown'
                if not match.empty:
                    value = match.iloc[0].get(status, 'Unknown') or 'Unknown'
                item[country] = status_icons.get(value, '') + ' ' + value
            summary.append(item)
        st.subheader('At a glance')
        st.dataframe(pd.DataFrame(summary), hide_index=True, use_container_width=True)
        st.caption('Each dimension is assessed separately. No overall ranking is calculated.')
        st.subheader('Explore the differences')
    for country in selected_countries:
        match = case[case['country'] == country]
        if match.empty:
            continue
        row = match.iloc[0]
        with st.container(border=True):
            st.subheader(country)
            st.caption(f"Age: {row['age_group']} | {row['residency_status']} | {row['region']}")
            if row['source_ids']:
                st.caption('Evidence linked; individual claims may still be pending verification.')
            else:
                st.caption('No official evidence linked yet.')
            for title, status, description in dimensions:
                with st.expander(f"{title}: {row.get(status, 'Unknown') or 'Unknown'}"):
                    st.write(row.get(description, '') or 'Insufficient information.')
            st.markdown('**Alternative or next step**')
            st.write(row['alternative'])
            st.markdown('**Your next steps**')
            st.write('1. Read the legal and administrative conditions above. If they are Unknown, verify them before making a decision.')
            st.write('2. List what you already have: time, skills, equipment, documents and a realistic budget.')
            st.write('3. Choose one small, safe step toward the goal, such as learning a skill, preparing an application or contacting an official adviser.')
            if row['alternative']:
                st.write('4. An alternative to explore: ' + row['alternative'])
            st.caption('These are general planning prompts, not a guarantee of eligibility or success.')
            with st.expander('Evidence and verification'):
                show_sources(row['source_ids'])
                st.caption('Record date: ' + row['checked_date'])

elif page == 'Advice Explorer':
    st.header('Advice Explorer')
    st.write('Explore the advice behind the research and its original context.')
    search = st.text_input('Search advice')
    filtered = advice[advice['advice'].str.contains(search, case=False, regex=False)]
    st.caption(f'{len(filtered)} advice cases found')
    for _, row in filtered.iterrows():
        with st.expander(row['advice']):
            st.caption(row['category'] + ' Â· ' + row['platform'])
            st.write(row['applicability_notes'])
            st.caption(row['verification_status'])
            if row['post_url'].startswith('https://'):
                st.link_button('Original publication', row['post_url'])

elif page == 'Interactive Scenarios':
    st.header('What would you do?')
    st.caption('Hypothetical educational situations, not personal advice.')
    scenario_labels = []
    scenario_ids = {}
    for _, scenario in scenarios.iterrows():
        label = scenario['scenario_id'] + ' - ' + scenario['situation']
        scenario_labels.append(label)
        scenario_ids[label] = scenario['scenario_id']
    if scenario_labels:
        selected_label = st.selectbox('Select a scenario', scenario_labels)
        selected = scenario_ids[selected_label]
        row = scenarios[scenarios['scenario_id'] == selected].iloc[0]
        st.caption(row['country'])
        answer = st.radio('Your decision', [row['option_a'], row['option_b']], index=None, key=selected)
        if answer is not None:
            if answer == row['option_a']:
                st.info(row['feedback_a'])
            else:
                st.info(row['feedback_b'])
            show_sources(row['source_ids'])

elif page == 'Affordability Calculator':
    st.header('Affordability Calculator')
    st.caption('Illustrative adult monthly budget. No currency conversion or personal financial recommendation.')
    currency = st.selectbox('Currency', ['EUR', 'USD', 'RUB'])
    income = st.number_input('Net monthly income', min_value=0.0, value=1500.0)
    rent = st.number_input('Monthly rent', min_value=0.0, value=750.0)
    expenses = st.number_input('Other essential expenses', min_value=0.0, value=450.0)
    balance = income - rent - expenses
    a, b, c = st.columns(3)
    a.metric('Income', f'{income:,.2f} {currency}')
    b.metric('Essential costs', f'{rent + expenses:,.2f} {currency}')
    c.metric('Monthly balance', f'{balance:,.2f} {currency}')
    if balance < 0:
        st.warning('Expenses exceed income in this hypothetical budget.')
    else:
        st.info('This balance does not account for unexpected expenses or upfront costs.')
    st.bar_chart(pd.DataFrame({'Amount': [income, rent, expenses]}, index=['Income', 'Rent', 'Other essentials']))

else:
    st.header('Research & Evidence')
    st.warning('Purposive, nonrepresentative sample. Not all sources or numerical estimates have been independently verified.')
    for name in ['Findings', 'Methodology', 'Economic Data', 'Sources']:
        if name in sheets:
            with st.expander(name, expanded=name == 'Findings'):
                if name == 'Economic Data':
                    st.caption('Candidate benchmarks: check units, populations, dates and source verification before comparing.')
                st.dataframe(sheets[name], hide_index=True, use_container_width=True)
