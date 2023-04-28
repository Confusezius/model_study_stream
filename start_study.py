#%%
import numpy as np
import pandas as pd
import streamlit as st
import requests
import os
import s3fs
import datetime

#%%
#%% 
base_path = 'https://shyamgopalawsbucket.s3.eu-north-1.amazonaws.com'
experiments = [
    #SD14 Experiments
    # ['sd14_fixed', 'sd14_tifa'], 
    # ['sd14_tifa', 'sd14_imgreward'],
    # ['ae_14','struct_diff_14', 'comp_14', 'sd14_tifa'], #Comparison between baselines improvements and seed selection on SD14.
    # ['struct_diff_14', 'sd14_tifa'], #Comparison between baselines improvements and seed selection on SD14.
    #SD21 Experiments
    # ['sd21_fixed', 'sd21_tifa'], 
    # ['ae_21', 'sd21_imgreward'], #Comparison A&E21 & TIFA Seed Selection.
    # ['ae_21', 'sd21_tifa'], #Comparison A&E21 & TIFA Seed Selection.
    ['ae_21', 'sd21_imgreward'] #Comparison A&E21 & TIFA Seed Selection.    
]

img_files = [f'{i}.jpg' for i in range(1, 1001)]
text_files = [f'{i}.txt' for i in range(1, 1001)]
prompt_folder = 'prompts'

if 'counter' not in st.session_state:
    # select experiment
    exp_idx = np.random.choice(len(experiments))
    exps = experiments[exp_idx]
    
    st.session_state.prompts = np.array([base_path + '/' + prompt_folder + '/' + x for x in text_files])
    st.session_state.true_indices = np.arange(len(st.session_state.prompts))
    rand_indices = np.random.choice(len(st.session_state.prompts), len(st.session_state.prompts), replace=False)
    st.session_state.prompts = st.session_state.prompts[rand_indices]
    st.session_state.image_dict = {mode: np.array([base_path + '/' + mode + '/' + x for x in img_files])[rand_indices] for mode in exps}
    st.session_state.true_indices = st.session_state.true_indices[rand_indices]
    
    st.session_state.exps = exps
    # print(exps)

layout = 'wide' if len(st.session_state.exps) > 3 else 'centered'
st.set_page_config(layout=layout, page_title="Compare Generated Images")

#%%
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
local_css("style.css")
            

if 'counter' not in st.session_state:     
    st.session_state.counter = 0
    st.session_state.selections = []
    st.session_state.classes = []
    st.session_state.indices = []
    st.session_state.exp_list = []
    counter = 0
    timestr = str(datetime.datetime.now()).replace(' ', '_').replace(':', '-').replace('.', '-')
    st.session_state.path_name = f'results_{timestr}.csv'

with st.sidebar:
    st.markdown("<h3>Some info about yourself:</h3>", unsafe_allow_html=True)
    is_first = st.checkbox("This is my first time doing the study.")
    gender = ["Prefer not to say", "Male", "Female", "Other"]
    sel1 = st.selectbox("Your preferred gender", gender)
    ages = ["Prefer not to say", "18-25", "26-35", "36-45", "45+"]
    sel2 = st.selectbox("Age group", ages)
    st.write('')
    st.markdown("<h3>Some more information about the task:</h3>", unsafe_allow_html=True)
    st.markdown("<p>We are looking for <b>faithful</b> text representation. This means that correctly visualized semantic elements and relations are more important than simply the image quality.</p>", unsafe_allow_html=True)
    st.write('')
    st.markdown('<h3>Example: </h3><p><i>"A chicken on top of a house."</i></p>', unsafe_allow_html=True)
    st.markdown("<p>Here, we should find a chicken and a house in the image. The chicken should also be on top, not e.g. next, to the house. An image of lower quality for which all of this holds is more faithful than a high-quality chicken image.</p>", unsafe_allow_html=True)    


def select_button(val, photo, true_index):
    st.session_state.counter += 1
    st.session_state.selections.append(val)
    model = 'Neither' if photo == 'Neither' else photo.split('/')[-2]
    # print(model)
    st.session_state.classes.append(model)
    st.session_state.indices.append(true_index)
    st.session_state.exp_list.append('__'.join(st.session_state.exps))
    if st.session_state.counter >= len(st.session_state.prompts):
        end_everything()

#AWS: eu-central-1    
def end_everything():
    gender_choice = sel1
    age_choice = sel2
    is_first_time = is_first

    ### Write data to bucket.
    df = pd.DataFrame({
        'experiment': st.session_state.exp_list,
        'selections': st.session_state.selections,
        'indices': st.session_state.indices,
        'classes': st.session_state.classes,
        'gender': [gender_choice for _ in range(len(st.session_state.selections))],
        'age': [age_choice for _ in range(len(st.session_state.selections))],
        'first_time': [is_first_time for _ in range(len(st.session_state.selections))]
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
prompt = st.session_state.prompts[st.session_state.counter]
prompt = f'"{requests.get(prompt).text}"'
photos = [st.session_state.image_dict[exp][st.session_state.counter] for exp in st.session_state.exps]
 
#%%    
# Get list of images in folder
st.markdown("<h2 style='text-align: center;'>Task</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size:20px'>Select which image most <b>faithfully</b> reflects the sentence. If the images are the same, choose one at random. If you are finished, please click <b>[Done]</b>!</p>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>Progress</h2>", unsafe_allow_html=True)
progr = st.progress(st.session_state.counter/len(st.session_state.prompts), text=f'Images seen: {st.session_state.counter} | {len(st.session_state.prompts)}')
sel_val = st.session_state.selections[np.clip(st.session_state.counter-3, 0, None): st.session_state.counter] if st.session_state.counter else []
sel_val = ['Option ' + str(x) for x in sel_val]
st.markdown("<h2 style='text-align: center;'>Text Prompt</h2>", unsafe_allow_html=True)
st.markdown(f"<h4 style='text-align: center; background-color: grey; color: white'>{prompt}</h4>", unsafe_allow_html=True)
st.write('')
st.write('')
st.write('')

cols = st.columns(len(st.session_state.exps), gap="medium")
# Randomly permute columns.
col_idcs = np.random.choice(len(cols), len(cols), replace=False)
cols = [cols[i] for i in col_idcs]

emoji_dict = {
    0: ':one:', 1: ':two:', 2: ':three:', 3: ':four:', 4: ':five:',
    5: ':six:', 6: ':seven:', 7: ':eight:', 8: ':nine:'
}
for i, exp in enumerate(st.session_state.exps):
    cols[i].image(photos[i], caption=None, use_column_width=True)
    _ = cols[i].button(f"{emoji_dict[col_idcs[i]]} I prefer this", on_click=select_button, args=[i, photos[i], true_index], key=f'btt{i}')
btt_done = st.button("**I'm done**", on_click=end_everything, key='btt_done', type='primary')






