import attendence_service as attendence_service
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import sqlite3
import plotly.express as px
import pandas as pd
import datetime
# import logging
# logging.basicConfig(filename='logs/app.log', filemode='a', format='%(asctime)s - %(message)s', level=logging.DEBUG)

# Set page config
st.set_page_config (
    page_title='Attendence Manager', 
    layout = 'centered', 
    initial_sidebar_state = 'auto',
    menu_items=None,
    page_icon='icon.png'
)

# Load config
with open('users.yaml') as file:
    config = yaml.load(file, Loader = SafeLoader)
    
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    # config['preauthorized']
)

# Set Session State
# if 'key_name' not in st.session_state:
#     st.session_state.key = uuid.uuid4().hex

# Login Page
name, authentication_status, username = authenticator.login('Login to Attendence Manager', 'main')

# Verify login
if authentication_status == True:
    st.title(f'Welcome {name}')
    
    # Database Connection
    srm_username = config['credentials']['usernames'][username]['evarsity_username']
    srm_password = config['credentials']['usernames'][username]['evarsity_password']
    st.write(f'SRM Username: {srm_username}')
    conn = sqlite3.connect(f'databases/{srm_username}.sqlite')
    
    # Get all subjects
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    subjects = [row[0] for row in cur.fetchall()]
    
    # Select Subject Tabs
    subject_tabs = st.tabs(subjects)
    
    attendance = {}
    
    # Data Visualization for each subject
    for (subject_name, subject_tab) in zip(subjects, subject_tabs):
        with subject_tab:
            data = cur.execute(f'SELECT Date, Percentage FROM "{subject_name}"').fetchall()
            (total_classes, attended_classes) = cur.execute(f'SELECT Total_Classes, Attended FROM "{subject_name}"').fetchall()[-1]
            data = pd.DataFrame(data, columns=['date', 'attendance'])
            # st.header(f'Current Attendance in {subject_name} : {data["attendance"].iloc[-1]}%')
            st.markdown(f'''
                        <h1 style="color: {'red' if data["attendance"].iloc[-1] < 75.0 else 'green'}; text-align: center; font-size: 30px;">
                        Current Attendance in {subject_name} : {data["attendance"].iloc[-1]}%</h1>''', 
                        unsafe_allow_html=True
                        )
            
            st.markdown(f'''
                        <h1 style="color: {'red' if data["attendance"].iloc[-1] < 75.0 else 'green'}; text-align: center; font-size: 30px;">
                        Total_Classes : {total_classes} <br>
                        Attended_Classes : {attended_classes} </h1>''', 
                        unsafe_allow_html=True
                        )
            
            fig = px.line(data, x='date', y='attendance', title=None)
            fig.update_layout(
                xaxis={
                    'title':'Date',
                    # 'range' : [datetime.datetime.strptime(data['date'].iloc[0], r"%Y-%m-%d").date(), (datetime.datetime.strptime(data['date'].iloc[-1], r"%Y-%m-%d") + datetime.timedelta(days=1)).date()],
                    'fixedrange':True
                    },
                yaxis={
                    'title':'Attendance (%)',
                    'fixedrange':True
                    }
                )
            
            st.plotly_chart(fig, 
                            use_container_width=True, 
                            config={'displayModeBar': False, 
                                    'scrollZoom': False, 
                                    'displaylogo': False, 
                                    'editable': False
                                    },
                            sharing='streamlit',
                            theme='streamlit'
                            )
            attendance[subject_name] = data["attendance"].iloc[-1]
            
            # Now show how much classes can be bunked / should be attended
            def calc(total_hours, attended_hours):
                # print('Current attendance: ', attended_hours/total_hours*100, '%')
                if attended_hours/total_hours >= 0.75:  # 75% attendance is fullfilled
                    # print('Now you can bunk classes')
                    bunkable_hours = 0
                    while True:
                        if attended_hours/total_hours >= 0.75:
                            bunkable_hours += 1
                            total_hours += 1
                        else:
                            return bunkable_hours - 1
                else:   # 75% attendance is not fullfilled
                    # print('You need to attend classes')
                    if attended_hours/total_hours < 0.75:
                        to_be_attended = 0
                        while True:
                            if attended_hours/total_hours < 0.75:
                                total_hours += 1
                                attended_hours += 1
                                to_be_attended -= 1
                            else:
                                # print('New attendance: ', attended_hours/total_hours*100, '%')
                                return to_be_attended
            
            # data = cur.execute(f'SELECT Total_Classes, Attended FROM "{subject_name}"').fetchall()[-1]
            # total_classes, attended_classes = data[0], data[1]
            
            if attended_classes/total_classes >= 0.75:
                st.markdown(f'''
                            <h1 style="color: green; text-align: center; font-size: 30px;">
                            Congratulations! You can bunk {calc(total_classes, attended_classes)} classes </h1>''', 
                            unsafe_allow_html=True
                            )
            else:
                st.markdown(f'''
                            <h1 style="color: red; text-align: center; font-size: 30px;">
                            You need to attend {calc(total_classes, attended_classes)*-1} classes </h1>''', 
                            unsafe_allow_html=True
                            )
            
                
    
    # Display overall attendance Summary
    x = 0
    st.header(r"Subjects with less than 75% attendance")
    for subject_name, attendance in attendance.items():
        data = cur.execute(f'SELECT Total_Classes, Attended FROM "{subject_name}"').fetchall()[-1]
        total_classes, attended_classes = data[0], data[1]
        if attendance < 75.0:
            st.error(f'{subject_name}: {attendance}% (You need to attend {calc(total_classes, attended_classes)*-1} classes)')
            x += 1
    if x == 0:
        st.success(r"All subjects have more than 75% attendance")
           
    # Force Update Attendance
    if st.button('Force Update Attendance'):
        attendence_service.refresh_user(srm_username, srm_password)
        st.balloons()
        st.info('Attendance Updated')
        
        
     
    # Logout
    conn.close()
    authenticator.logout('Logout', 'main')
    
    
    
elif authentication_status == False:
    st.error('Username/password is incorrect')
    
elif authentication_status == None:
    st.warning('Please enter your username and password')