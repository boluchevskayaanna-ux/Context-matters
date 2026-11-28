# Curated starting points, not a live vacancy or admissions database.
RESOURCES = {
 'Russia': {
 'job': [('Работа России','https://trudvsem.ru/'),('Роструд','https://rostrud.gov.ru/')],
 'study': [('Поступление в вуз — Госуслуги','https://www.gosuslugi.ru/vuzonline'),('НИУ ВШЭ — бакалавриат','https://ba.hse.ru/'),('МГУ — приёмная комиссия','https://cpk.msu.ru/')],
 'volunteer': [('Добро.рф','https://dobro.ru/')],
 'intern': [('Работа России','https://trudvsem.ru/'),('Федеральное агентство по делам молодёжи','https://fadm.gov.ru/')]},
 'USA': {
 'job': [('CareerOneStop','https://www.careeronestop.org/'),('Youth employment rules','https://www.dol.gov/agencies/whd/youthrules')],
 'study': [('College Scorecard','https://collegescorecard.ed.gov/'),('Federal Student Aid','https://studentaid.gov/'),('City University of New York','https://www.cuny.edu/admissions/')],
 'volunteer': [('AmeriCorps','https://americorps.gov/'),('VolunteerMatch','https://www.volunteermatch.org/')],
 'intern': [('USAJOBS students','https://www.usajobs.gov/Help/working-in-government/unique-hiring-paths/students/'),('CareerOneStop','https://www.careeronestop.org/')]},
 'France': {
 'job': [('France Travail','https://www.francetravail.fr/'),('Service Public','https://www.service-public.fr/particuliers/vosdroits/F1649')],
 'study': [('Parcoursup','https://www.parcoursup.gouv.fr/'),('CROUS','https://www.etudiant.gouv.fr/'),('Université Paris 1','https://www.pantheonsorbonne.fr/'),('Université de Strasbourg','https://www.unistra.fr/')],
 'volunteer': [('JeVeuxAider','https://www.jeveuxaider.gouv.fr/'),('Service Civique','https://www.service-civique.gouv.fr/')],
 'intern': [('1jeune1solution','https://www.1jeune1solution.gouv.fr/'),('Service Public — stages','https://www.service-public.fr/particuliers/vosdroits/F16734')]}}
SKILLS = {
 'Economics and data': ('Build a chart from public economic data and explain its limitations.', 'World Bank Open Data','https://data.worldbank.org/'),
 'Technology': ('Build a small website or database and document your work.', 'CS50 SQL','https://cs50.harvard.edu/sql/'),
 'Society and policy': ('Compare two public policies using official documents.', 'UN CC:e-Learn','https://unccelearn.org/'),
 'Business and organization': ('Draft a hypothetical project budget and research user needs.', 'OpenLearn','https://www.open.edu/openlearn/'),
 'Creative communication': ('Create an infographic and ask a teacher for feedback.', 'OpenLearn','https://www.open.edu/openlearn/'),
 'Science and environment': ('Analyze an open environmental dataset.', 'NASA Earthdata','https://www.earthdata.nasa.gov/')}
GOALS = {'Find a first job':'job','Study with a lower budget':'study','Learn a skill and build experience':'skill','Volunteer':'volunteer','Find an internship':'intern'}
ABROAD = [('Campus France','https://www.campusfrance.org/'),('EducationUSA','https://educationusa.state.gov/'),('DAAD','https://www.daad.de/en/'),('Study in Italy','https://studyinitaly.esteri.it/')]

def recommendations(country, goal, age, interests, abroad=False):
    kind=GOALS[goal]
    links=list(RESOURCES[country].get(kind, []))
    steps=[]
    if kind=='job':
        steps=['Check age, school schedule, work authorization and regional rules before applying.', 'Prepare a one-page CV with real projects and skills.', 'Search the listed portals for part-time or student vacancies in your region.', 'Check employer identity, duties, pay and written contract; never pay to obtain a job.', 'Track suitable applications and review responses with a career adviser.']
    elif kind=='study':
        if abroad: links+=ABROAD
        steps=['Choose a subject and compare entry qualifications and teaching language.', 'Use official admissions pages to shortlist three programs.', 'Record tuition, mandatory fees, housing and transport in one currency.', 'Check scholarship eligibility, citizenship rules and separate deadlines.', 'Compare total costs after confirmed aid against your budget; do not assume funding is guaranteed.', 'Prepare transcripts and language documents and confirm requirements with admissions.']
    elif kind=='skill':
        for name in interests or list(SKILLS)[:2]:
            if name in SKILLS:
                task,title,url=SKILLS[name]; steps.append(task); links.append((title,url))
        steps+=['Check course age requirements, access, fees and certificate terms.', 'Choose a manageable learning schedule and create a small portfolio artifact.', 'Ask a teacher or mentor for feedback and revise your work.']
    elif kind=='volunteer':
        steps=['Choose a cause and search the listed portal by region.', 'Check minimum age, supervision, schedule and any costs with the organizer.', 'Choose an appropriate supervised activity and confirm duties.', 'Keep a record of contributions and request feedback.']
    else:
        steps=['Identify a field and ask your school or university about placements.', 'Check whether the placement accepts your age and education level.', 'Confirm written duties, supervision, compensation and any required agreement.', 'Prepare a CV and apply through official channels.', 'Review the learning objectives with a mentor.']
    if age<18:
        steps.insert(0,'For applicants under 18: confirm eligibility and any required guardian consent with the institution before committing.')
    return steps,links

def open_path(st):
    st.session_state['route_goal']='Learn a skill and build experience'
    st.session_state['page']='Your Path'

def show_path(st, paths, countries, show_sources):
    goals=list(GOALS)
    goal=st.session_state.pop('route_goal',None)
    if goal in goals: st.session_state['path_goal']=goal
    country=st.session_state.pop('route_country',None)
    if country in countries: st.session_state['path_country']=country
    goal=st.selectbox('What do you want to do?',goals,key='path_goal')
    country=st.selectbox('Where do you live?',countries,key='path_country')
    age=st.number_input('Age',min_value=13,max_value=100,value=17,step=1)
    region=st.text_input('Region or city (optional)')
    profile=st.session_state.get('interest_profile',{})
    defaults=[k for k,v in sorted(profile.items(),key=lambda x:-x[1]) if v>0][:2]
    interests=st.multiselect('Areas of interest',list(SKILLS),default=defaults,key='path_interests')
    if profile: st.caption('Your Future Direction results are available as suggested interests. You can change them.')
    abroad=False
    if GOALS[goal]=='study':
        abroad=st.checkbox('Include study abroad resources')
        currency=st.selectbox('Budget currency',['RUB','USD','EUR','Other'])
        budget=st.number_input('Annual budget including living costs (0 = not specified)',min_value=0,value=0,step=100)
        if budget: st.write(f'Your comparison limit: {budget:,} {currency} per year ({budget/12:,.0f} per month). Compare official total costs against this limit.')
    steps,links=recommendations(country,goal,age,interests,abroad)
    st.subheader('Your action plan')
    for i,step in enumerate(steps,1): st.write(f'{i}. {step}')
    st.subheader('Where to look')
    for title,url in links: st.markdown(f'[{title}]({url})')
    st.caption('Curated starting points; current availability, prices and eligibility have not been independently checked.')
    terms={'job':('подработка школьникам','student part-time jobs','emploi étudiant mineur'),'study':('бюджетные места стипендии','college scholarships tuition','bourses études frais inscription'),'skill':('бесплатные курсы','free introductory courses','cours gratuits initiation'),'volunteer':('волонтёрство','youth volunteering','bénévolat jeunes'),'intern':('стажировка учащимся','student internships','stage étudiant')}
    from urllib.parse import quote_plus
    query=terms[GOALS[goal]][countries.index(country)]+' '+(region or country)+' '+str(age)
    st.code(query,language=None)
    st.markdown('[Search the web](https://www.google.com/search?q='+quote_plus(query)+')')
    old=paths[(paths['goal']==goal)&(paths['country']==country)]
    if not old.empty:
        with st.expander('Additional research and sources'):
            for _,row in old.sort_values('step').iterrows():
                st.write(row['title']+': '+row['action'])
                if row['source_ids']: show_sources(row['source_ids'])
