#%%
import numpy as np
import pandas as pd
import streamlit as st
import requests
import csv
import os

#%%  
st.set_page_config(layout="wide", page_title="Compare Generated Images")

#%% 
filename = 'sd_vs_bestseed.csv'
if 'counter' not in st.session_state: 
    st.session_state.counter = 0
    st.session_state.selections = []
    st.session_state.classes = []
    st.session_state.indices = []
    counter = 0
    path_name = f'results_{filename.split(".")[0]}_{counter}.csv'
    while os.path.exists(path_name):
        counter += 1
        path_name = f'results_{filename.split(".")[0]}_{counter}.csv'
    
    st.session_state.path_name = path_name
    
    with open(st.session_state.path_name, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(['Index', 'Method'])

col1, col2, col3, col4 = st.columns([3, 3, 3, 3], gap="medium")

base_file = f'assets/{filename}'
base_file = pd.read_csv(base_file)

prompts = list(base_file['prompt'])
image_1 = list(base_file['image_url_1'])
image_2 = list(base_file['image_url_2'])


def select_button(val, photo, prompt):
    st.session_state.counter += 1
    st.session_state.selections.append(val)
    model = 'Neither' if photo == 'Neither' else photo.split('/')[-2]
    st.session_state.classes.append(model)
    st.session_state.indices.append(st.session_state.counter - 1)
    if st.session_state.counter >= len(image_1):
        import sys
        sys.exit()

    with open(st.session_state.path_name, 'a') as file:
        writer = csv.writer(file)
        writer.writerow([st.session_state.counter, model])

def end_everything():
    st.success("Finished! If you want to evaluate more images, just reload this page :).")
    import sys
    sys.exit()
    
#%%    
# Get list of images in folder
col1.subheader("Progress")
progr = col1.progress(st.session_state.counter/len(image_1), text=f'Images seen: {st.session_state.counter}')
sel_val = st.session_state.selections[np.clip(st.session_state.counter-3, 0, None): st.session_state.counter] if st.session_state.counter else []
sel_val = ['Option ' + str(x) for x in sel_val]
col1.write('**Last selections:**')
col1.write('{0}'.format(' > '.join(sel_val)))

#%%     
photo1 = image_1[st.session_state.counter]
photo2 = image_2[st.session_state.counter]
prompt = prompts[st.session_state.counter]
prompt = requests.get(prompt).text

col1.write('**Text Prompt:**')
col1.write(prompt)
col1.write('')
col1.write('')
col1.write('')
btt1 = col1.button("**I'm done**", on_click=end_everything, key='btt1', type='primary')
col2.image(photo1, caption='Option 1')
btt2 = col2.button("I prefer this", on_click=select_button, args=[1, photo1, prompt], key='btt2')
col3.image(photo2, caption='Option 2')
col4.image('assets/question.png', caption='No preference')
btt3 = col3.button("I prefer this", on_click=select_button, args=[2, photo2, prompt], key='btt3')
btt4 = col4.button("No preference", on_click=select_button, args=[-1, 'Neither', prompt], key='btt4')







