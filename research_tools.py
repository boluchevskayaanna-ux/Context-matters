import streamlit as st
from engine import analyze_advice
from internships import analyze_internship
from entrepreneurship import analyze_business
from data_loader import read_csv


def show_result(result):
    st.write('Evidence-based status: ' + result['status'])
    if 'preliminary_status' in result:
        st.write('Preliminary assessment: ' + result['preliminary_status'])
    for reason in result.get('reasons', []):
        st.write(reason)
    if 'rule' in result:
        st.write(result['rule'])
    if 'weekly_limit' in result:
        st.write('National weekly limit:', result['weekly_limit'] if result['weekly_limit'] is not None else 'Not established in this dataset')
    if result.get('regional'):
        st.write('Regional weekly limit:', result['regional'].get('weekly_limit', 'Unknown'))
    if 'minimum_eur' in result:
        st.write('Illustrative minimum compensation (2026 benchmark):', result['minimum_eur'], 'EUR')
    st.caption(result.get('evidence', 'Verification pending'))
    ids = result.get('source_ids', result.get('source', ''))
    ids += ';' + (result.get('regional') or {}).get('source_ids', '')
    for source in read_csv('sources.csv'):
        if source['source_id'] in [x.strip() for x in ids.split(';')]:
            st.write(source['source_id'], source.get('title', ''))
            if source.get('url', '').startswith('https://'):
                st.markdown('[Open source](' + source['url'] + ')')
    st.caption('Source coverage is incomplete. This is a research illustration, not a legal eligibility decision.')


def research_tools():
    st.subheader('Rule-based research tools')
    st.caption('Compare hypothetical cases using preliminary legal data. Existing research profiles remain separate.')
    topic = st.selectbox('Research topic', ['Employment', 'Internships', 'Entrepreneurship'], key='tool_topic')
    country = st.selectbox('Research country', ['Russia', 'USA', 'France'], key='tool_country')
    if topic == 'Employment':
        age = st.number_input('Hypothetical age', 14, 17, 15, key='tool_age')
        period = st.radio('Research period', ['School', 'Holiday'], key='tool_period')
        state = None
        if country == 'USA':
            state = st.selectbox('State', [r['state'] for r in read_csv('regional_rules.csv')])
        schedule = []
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            schedule.append(st.number_input(day + ' hours', 0.0, 24.0, 0.0, step=0.5))
        show_result(analyze_advice(country, age, period, schedule, state=state))
    elif topic == 'Internships':
        kinds = [r['kind'] for r in read_csv('internship_rules.csv') if r['country'] == country]
        kind = st.selectbox('Placement type', kinds)
        hours = None
        if country == 'France':
            hours = st.number_input('Total placement hours', 0, 2000, 0)
        show_result(analyze_internship(country, kind, hours))
    else:
        kinds = [r['kind'] for r in read_csv('entrepreneurship_rules.csv') if r['country'] == country]
        kind = st.selectbox('Business form', kinds)
        age = st.number_input('Hypothetical age', 14, 17, 16, key='business_age')
        show_result(analyze_business(country, kind, age))
