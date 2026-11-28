"""Topic-specific evidence leads, not live search or eligibility decisions."""
from urllib.parse import quote_plus

# IDs refer to the existing Sources worksheet. Destination sources are labelled.
TOPICS = {
 'A001': ('business', 'digital service freelance work'), 'A002': ('business', 'second-hand resale business'),
 'A003': ('study', 'tuition fees international undergraduate admission Germany Greece Northern Cyprus'),
 'A004': ('cern', 'CERN openlab summer student eligibility funding'),
 'A005': ('housing', 'rental housing legal capacity living costs'), 'A006': ('study', 'gap year university admission'),
 'A007': ('work', 'first job employment requirements'), 'A008': ('work', 'student professional networking'),
 'A009': ('budget', 'household budget essential expenses'), 'A010': ('study', 'high school research opportunities'),
 'A011': ('studentwork', 'international student work authorization'), 'A012': ('volunteer', 'youth volunteering first job'),
 'A013': ('internship', 'unpaid internship legal compensation'), 'A014': ('internship', 'paid student work internship'),
 'A015': ('study', 'scholarship application requirements'), 'A016': ('study', 'local university scholarships'),
 'A017': ('skills', 'free programming courses projects'), 'A018': ('business', 'freelance business registration'),
 'A019': ('business', 'freelance tax registration'), 'A020': ('work', 'student working hours'),
 'A021': ('work', 'remote work employment eligibility'), 'A022': ('work', 'student jobs working hours'),
 'A023': ('business', 'youth freelance income rules'), 'A024': ('business', 'online creator income tax rules'),
 'A025': ('study', 'government scholarships application deadlines'), 'A026': ('study', 'public university fees Italy Austria Germany'),
 'A027': ('study', 'US university international financial aid'), 'A028': ('study', 'university specific scholarship eligibility'),
 'A029': ('study', 'Italy regional scholarships award compatibility'), 'A030': ('volunteer', 'international volunteering age visa accommodation'),
 'A031': ('budget', 'financial literacy investment risks'), 'A032': ('internship', 'student internship eligibility'),
 'A033': ('work', 'job application employment services'), 'A034': ('volunteer', 'skills based volunteering student projects'),
 'A035': ('budget', 'saving budgeting financial literacy'),
}
IDS = {
 'Russia': {'business':'S001 S002 S003 S031','work':'S008 S009','studentwork':'S026','internship':'S172 S173','study':'S022','housing':'S036 S040','budget':'S034 S036','skills':'S024'},
 'USA': {'business':'S171','work':'S006 S007 S055 S056','studentwork':'S027','internship':'S020 S006','study':'S016 S019 S025','housing':'S043 S044','budget':'S014 S038','skills':'S024'},
 'France': {'business':'S004 S046','work':'S005','studentwork':'S013','internship':'S021 S168','study':'S010 S017 S018 S023','housing':'S029 S030 S037','budget':'S029 S030','skills':'S024'},
}
# Official starting portals; individual pages and current eligibility not independently rechecked in this update.
PORTALS = {
 'Russia': {'work':('Работа России','https://trudvsem.ru/'),'business':('ФНС','https://www.nalog.gov.ru/'),'study':('Минобрнауки','https://minobrnauki.gov.ru/'),'volunteer':('Добро.рф','https://dobro.ru/'),'budget':('Финансовая культура Банка России','https://fincult.info/'),'housing':('Госуслуги','https://www.gosuslugi.ru/'),'internship':('Роструд','https://rostrud.gov.ru/'),'studentwork':('Роструд','https://rostrud.gov.ru/')},
 'USA': {'work':('CareerOneStop','https://www.careeronestop.org/'),'business':('SBA','https://www.sba.gov/'),'study':('EducationUSA','https://educationusa.state.gov/'),'volunteer':('AmeriCorps','https://americorps.gov/'),'budget':('CFPB','https://www.consumerfinance.gov/consumer-tools/'),'housing':('HUD','https://www.hud.gov/'),'internship':('Department of Labor','https://www.dol.gov/'),'studentwork':('Study in the States','https://studyinthestates.dhs.gov/')},
 'France': {'work':('France Travail','https://www.francetravail.fr/'),'business':('Service Public Entreprendre','https://entreprendre.service-public.gouv.fr/'),'study':('Campus France','https://www.campusfrance.org/'),'volunteer':('JeVeuxAider','https://www.jeveuxaider.gouv.fr/'),'budget':('Mes questions d’argent','https://www.mesquestionsdargent.fr/'),'housing':('ANIL','https://www.anil.org/'),'internship':('Service Public','https://www.service-public.gouv.fr/'),'studentwork':('Service Public','https://www.service-public.gouv.fr/')},
}
LOCAL = {'Russia':{'work':'трудоустройство требования возраст','business':'регистрация бизнеса налоги возраст','study':'поступление стипендии условия','volunteer':'волонтёрство возраст регистрация','housing':'аренда жилья условия возраст','budget':'личный бюджет финансовая грамотность','internship':'стажировка оплата трудовой договор','studentwork':'работа иностранных студентов разрешение','skills':'бесплатные курсы программирования'},'France':{'work':'emploi conditions âge','business':'création entreprise conditions âge','study':'admission bourses conditions','volunteer':'bénévolat conditions âge','housing':'location logement conditions âge','budget':'budget personnel dépenses','internship':'stage convention gratification','studentwork':'travail étudiant étranger autorisation','skills':'cours programmation gratuits'}}

def find_guidance(country, advice_id, sources, age=None, region='', residency=''):
    topic, detail = TOPICS[advice_id]
    ids = IDS.get(country, {}).get(topic, '').split()
    if topic == 'cern': ids = ['S047','S048','S049']
    if advice_id == 'A003': ids += ['S050','S051','S052','S053','S054']
    rows = sources[sources['source_id'].isin(ids)].to_dict('records')
    portal = PORTALS.get(country, {}).get(topic)
    if topic == 'skills': portal = ('CS50','https://cs50.harvard.edu/')
    if topic == 'cern': portal = ('CERN Careers','https://careers.cern/')
    location = ' '.join(str(x) for x in (country,region) if x)
    age_text = str(age) if age is not None else ''
    queries = [f'{detail} {location} {age_text} {residency}'.strip()]
    local = LOCAL.get(country, {}).get(topic, detail)
    queries.append(f'{local} {location} {age_text}'.strip())
    if portal: queries.append(f'{local} site:{portal[1].split("/")[2]} {age_text}'.strip())
    return rows, portal, list(dict.fromkeys(queries))

def show_guidance(st, country, advice_id, sources, age=None, region='', residency=''):
    rows, portal, queries = find_guidance(country, advice_id, sources, age, region, residency)
    st.markdown('**Where to verify your situation**')
    st.caption('Topic-matched research leads, not a live search or a personal eligibility determination. Check the scope and date of each source.')
    for row in rows:
        url = row.get('url','')
        if url.startswith(('https://','http://')):
            st.markdown(f"[{row['title']}]({url}) — {row['institution']} ({row['country']})")
            st.caption(row.get('verification_status','Verification pending'))
    if portal:
        st.markdown(f'[{portal[0]}]({portal[1]}) — starting portal; specific current requirements not checked here.')
    st.markdown('**Search suggestions**')
    for query in queries:
        st.code(query, language=None)
        st.markdown('[Search the web](https://www.google.com/search?q='+quote_plus(query)+')')
    st.markdown('**Next steps**')
    st.write('1. Open the topic-specific source above and check its jurisdiction, eligibility conditions and date.')
    st.write('2. Use the search terms with your exact region, age or destination if the source does not cover your circumstances.')
    st.write('3. Confirm any remaining eligibility questions with the relevant institution before applying or making commitments.')
