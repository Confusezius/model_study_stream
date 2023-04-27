#%%
import numpy as np
import pandas as pd
import streamlit as st
import requests
import os
import s3fs
import datetime

#%%  
st.set_page_config(page_title="Compare Generated Images")

#%%
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
local_css("style.css")
            
#%% 
filename = 'sd_vs_bestseed.csv'
if 'counter' not in st.session_state:     
    st.session_state.counter = 0
    st.session_state.selections = []
    st.session_state.classes = []
    st.session_state.indices = []
    counter = 0
    timestr = str(datetime.datetime.now()).replace(' ', '_').replace(':', '-').replace('.', '-')
    st.session_state.path_name = f'results_{timestr}.csv'

    base_file = f'assets/{filename}'
    base_file = pd.read_csv(base_file)
    st.session_state.prompts = np.array(list(base_file['prompt']))
    st.session_state.image_1 = np.array(list(base_file['image_url_1']))
    st.session_state.image_2 = np.array(list(base_file['image_url_2']))
    st.session_state.true_indices = np.arange(len(st.session_state.prompts))
    rand_indices = np.random.choice(len(st.session_state.prompts), len(st.session_state.prompts), replace=False)

    st.session_state.true_indices = st.session_state.true_indices[rand_indices]
    st.session_state.prompts = st.session_state.prompts[rand_indices]
    st.session_state.image_1 = st.session_state.image_1[rand_indices]
    st.session_state.image_2 = st.session_state.image_2[rand_indices]


with st.sidebar:
    st.markdown("<h3>Some info about yourself:</h3>", unsafe_allow_html=True)
    gender = ["Prefer not to say", "Male", "Female", "Other"]
    sel1 = st.selectbox("Your preferred gender", gender)
    ages = ["Prefer not to say", "18-25", "26-35", "36-45", "45+"]
    sel2 = st.selectbox("Age group", ages)
    


def select_button(val, photo, true_index):
    st.session_state.counter += 1
    st.session_state.selections.append(val)
    model = 'Neither' if photo == 'Neither' else photo.split('/')[-2]
    st.session_state.classes.append(model)
    st.session_state.indices.append(true_index)
    if st.session_state.counter >= len(st.session_state.image_1):
        import sys
        sys.exit()

#AWS: eu-central-1    
def end_everything():
    gender_choice = sel1
    age_choice = sel2

    ### Write data to bucket.
    df = pd.DataFrame({
        'selections': st.session_state.selections,
        'indices': st.session_state.indices,
        'classes': st.session_state.classes,
        'gender': [gender_choice for _ in range(len(st.session_state.selections))],
        'age': [age_choice for _ in range(len(st.session_state.selections))]
    })
    
    s3 = s3fs.S3FileSystem(anon=False)
    with s3.open('studystorage/' + st.session_state.path_name, 'w') as f:
        df.to_csv(f)

    ### Complete everything.
    st.success("Finished! If you want to evaluate more images, just reload this page :).")
    import sys
    sys.exit()
   
#%%     
true_index = st.session_state.true_indices[st.session_state.counter]
photo1 = st.session_state.image_1[st.session_state.counter]
photo2 = st.session_state.image_2[st.session_state.counter]
prompt = st.session_state.prompts[st.session_state.counter]
prompt = requests.get(prompt).text
 
#%%    
# Get list of images in folder
st.markdown("<h2 style='text-align: center;'>Task</h2>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center;'>Given a sentence, select which image closest reflects it. If the images are the same, choose one at random. If you are finished, please click [Done]!</h5>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>Progress</h2>", unsafe_allow_html=True)
progr = st.progress(st.session_state.counter/len(st.session_state.image_1), text=f'Images seen: {st.session_state.counter}')
sel_val = st.session_state.selections[np.clip(st.session_state.counter-3, 0, None): st.session_state.counter] if st.session_state.counter else []
sel_val = ['Option ' + str(x) for x in sel_val]
st.markdown("<h2 style='text-align: center;'>Text Prompt</h2>", unsafe_allow_html=True)
st.markdown(f"<h4 style='text-align: center; background-color: grey; color: white'>{prompt}</h4>", unsafe_allow_html=True)
st.write('')
st.write('')
st.write('')

col2, col3 = st.columns([3, 3], gap="medium")

    
col2.image(photo1, caption=None)
btt2 = col2.button(":one: I prefer this", on_click=select_button, args=[1, photo1, true_index], key='btt2')
col3.image(photo2, caption=None)
btt3 = col3.button(":two: I prefer this", on_click=select_button, args=[2, photo2, true_index], key='btt3')
btt1 = st.button("**I'm done**", on_click=end_everything, key='btt1', type='primary')






