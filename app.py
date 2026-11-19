import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title='Context Matters', layout='wide')
st.title('Context Matters')
st.caption('The internet is global. Opportunities are not.')
st.sidebar.header('Explore')
page = st.sidebar.radio('Section', ['Context Switch', 'Advice Explorer', 'Interactive Scenarios', 'Affordability Calculator', 'Research & Evidence'])

# Keep the Excel export beside app.py, or upload it here for local testing.
if os.path.exists('database.xlsx'):
    database = 'database.xlsx'
else:
    database = st.sidebar.file_uploader('Upload the database (.xlsx)', type=['xlsx'])
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
            st.write(source['source_id'], '—', source['institution'], '—', source['title'])
            st.caption(source.get('verification_status', 'Verification pending'))
            if source['url'].startswith(('https://', 'http://')):
                st.link_button('Open source', source['url'])

if page == 'Context Switch':
    st.header('Same advice. Different context.')
    st.info('Research prototype: context assessments are preliminary. Unknown means insufficient evidence, not inaccessible. Check current official rules before acting.')
    category = st.selectbox('Category', ['All'] + sorted(advice['category'].unique().tolist()))
    choices = advice
    if category != 'All':
        choices = advice[advice['category'] == category]
    if choices.empty:
        st.stop()
    labels = []
    advice_ids = {}
    for _, row in choices.iterrows():
        label = row['advice_id'] + ' — ' + row['advice']
        labels.append(label)
        advice_ids[label] = row['advice_id']
    selected_label = st.selectbox('Choose advice', labels)
    selected = advice_ids[selected_label]
    st.caption('The profiles below are predefined research cases, not personalized legal assessments.')
    case = contexts[contexts['advice_id'] == selected]
    selected_countries = st.multiselect('Compare countries', countries, default=countries)
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
            with st.expander('Evidence and verification'):
                show_sources(row['source_ids'])
                st.caption('Record date: ' + row['checked_date'])

elif page == 'Advice Explorer':
    st.header('Advice Explorer')
    search = st.text_input('Search advice')
    filtered = advice[advice['advice'].str.contains(search, case=False, regex=False)]
    for _, row in filtered.iterrows():
        with st.expander(row['advice']):
            st.caption(row['category'] + ' · ' + row['platform'])
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
        label = scenario['scenario_id'] + ' — ' + scenario['situation']
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
    st.metric('Monthly balance', f'{balance:,.2f} {currency}')
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
