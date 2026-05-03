import streamlit as st

def home_header():
    logo_url = "https://thumbs.dreamstime.com/b/white-graduate-graduation-cap-icon-isolated-background-orange-pink-gradient-circle-vector-452966099.jpg"    
    st.markdown(f"""
                <div style="display:flex; flex-direction:column; align-item:center;justify-content:center; margin-bottom:30px; margin-top:30px">
                <img src = '{logo_url}', style = 'height:100px'/>
                <h1 style='text-align:center; color:#E0E3FF'>SNAP</br>CLASS</h1>
                </div>
    """, unsafe_allow_html=True)



def header_dashboard():
    logo_url = "https://thumbs.dreamstime.com/b/white-graduate-graduation-cap-icon-isolated-background-orange-pink-gradient-circle-vector-452966099.jpg"    
    st.markdown(f"""
                <div style="display:flex; align-item:left; justify-content: center ">
                <img src = '{logo_url}', style = 'height:70px'/>
                <h2 style='text-align:left; color:#5865F2'>SNAP</br>CLASS</h1>
                </div>
    """, unsafe_allow_html=True)


