import streamlit as st
from pgmpy.readwrite import BIFReader
from pgmpy.inference import VariableElimination
import re
import matplotlib.patches as patches
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time 
from add_patient import addPatient_page
from add_patient import sesCaluculator
from owlready2 import *
from pathlib import Path
import base64
from PIL import Image


favicon_path = "FAVICON.jpg"

# Set the page config with the favicon
st.set_page_config(
    page_title="Assistant d'incertitude medical",
    page_icon=favicon_path
)



def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


img = get_img_as_base64("background.jpg")

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("data:image/png;base64,{img}");
background-size: cover;
background-position: top left;
background-repeat: no-repeat;
background-attachment: local;
}}

[data-testid="stSidebar"] > div:first-child {{
background-image: url("data:image/png;base64,{img}");
background-size: cover;
background-position: center; 
background-repeat: no-repeat;
background-attachment: fixed;
}}

[data-testid="stHeader"] {{
background: rgba(0,0,0,0);
}}

[data-testid="stToolbar"] {{
right: 2rem;
}}


</style>
"""


#loading ontology
onto = get_ontology("ontologie_probabiliste_modifiee.rdf").load()
has_age=onto["AGE"]
has_bmi=onto["BMI"]
has_depression=onto["is_depressed"]
has_diabete=onto["is_diabetic"]
#do_exercise=onto["Do_Exercise"]
has_duration=onto["Duration"]
has_education=onto["EDUCATION"]
has_employ_group=onto["EMPLOY_GROUP"]
has_ethnicity=onto["ETHNICITY"]
do_exercise=onto["EXERCISE"]
home_own=onto["HOME_OWN"]
has_income=onto["INCOME"]
has_mental=onto["MENTHLTH"]
has_scant_meal=onto["SCANT_MEAL"]
has_scant_rent=onto["SCANT_RENT"]
has_ses=onto["SES"]
has_ses_cate=onto["SES_CATE"]
has_sex=onto["SEX"]
has_age_group=onto["AGE_GROUP"]
depressionProba=onto["pr_depression"]
obeseProba=onto["pr_obesity"]
exercisePoroba=onto["pr_exercise"]
longDurationProba=onto["pr_long_duration"]
shortDurationProba=onto["pr_short_duration"]
mediumDurationProba=onto["pr_medium_duration"]
scantRentProba=onto["pr_scant_rent"]
scantMeaProba=onto["pr_scant_meal"]







def plot_progress_circle(result):
    fig, ax = plt.subplots(figsize=(3, 3))  # Adjust the figure size here (width, height)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect('equal', 'box')

    circle = plt.Circle((50, 50), 30, color='lightgrey', fill=False, lw=6)  # Adjust the circle size here
    ax.add_artist(circle)

    start_angle = -90
    angle = result * 360 - 90
    if 0.2>result>0:
        arc = patches.Wedge((50, 50), 30, start_angle, angle, color='green', width=6)  # Adjust the arc size here
    elif 0.4>result>0.2:
        arc = patches.Wedge((50, 50), 30, start_angle, angle, color='yellow', width=6)
    elif 0.6>result>0.4:
        arc = patches.Wedge((50, 50), 30, start_angle, angle, color='orange', width=6)
    else:
        arc = patches.Wedge((50, 50), 30, start_angle, angle, color='red', width=6)
    
    ax.add_artist(arc)

    plt.text(50, 50, f'{int(result*100)}%', ha='center', va='center', fontsize=14)  # Adjust the font size here

    ax.axis('off')
    plt.close(fig)
    return fig



    
    
    


                             

@st.cache_resource()
def setup_done():
    # Do setup tasks here
    #reading bn
    reader = BIFReader('model.bif')
    bayesian_model = reader.get_model()

    return bayesian_model

if not setup_done():
    # Run the setup tasks only if it hasn't been done before
    setup_done() 

bayesian_model=setup_done()    

def calculate_probability(bayesian_model,query_variable, evidencedict):


    #evidencedict = {'ageGroupe':str(listevidence[0]),'gender':str(listevidence[1]),'ethnicity':str(listevidence[2]),'exercise':str(listevidence[3]),'income':str(listevidence[4]),'employementstatus':str(listevidence[5]),'educationlevel':str(listevidence[6]),'scantRent':str(listevidence[7]),'scantMeal':str(listevidence[8]),'homeOwnership':str(listevidence[9]),'SESCategory':str(listevidence[10]),'durationcategory':listevidence[11],'BMICategory':listevidence[12],'mentalhealthcategory':listevidence[13]}  # Dictionnaire des valeurs observées
    inference = VariableElimination(bayesian_model)
    result = inference.query(variables=[query_variable], evidence=evidencedict)
    return result

def calcule_comorbidity(result):
    pattern = r'\b\d+\.\d+\b'
    # Find all matches of the pattern in the text
    matches = re.findall(pattern, str(result))
    return matches[0]

def calcule_exercise(result):
    pattern = r'\b\d+\.\d+\b'
    # Find all matches of the pattern in the text
    matches = re.findall(pattern, str(result))
    return matches[1]

def calcule_obesity(result):
    pattern = r'\b\d+\.\d+\b'
    # Find all matches of the pattern in the text
    matches = re.findall(pattern, str(result))
    return matches[1]

def calcule_short_duration(result):
    pattern = r'\b\d+\.\d+\b'
    # Find all matches of the pattern in the text
    matches = re.findall(pattern, str(result))
    return matches[2]

def calcule_medium_duration(result):
    pattern = r'\b\d+\.\d+\b'
    # Find all matches of the pattern in the text
    matches = re.findall(pattern, str(result))
    return matches[1]

def calcule_long_duration(result):
    pattern = r'\b\d+\.\d+\b'
    # Find all matches of the pattern in the text
    matches = re.findall(pattern, str(result))
    return matches[0]

def calcule_scant_rent(result):
    pattern = r'\b\d+\.\d+\b'
    # Find all matches of the pattern in the text
    matches = re.findall(pattern, str(result))
    return str(float(matches[0])+float(matches[1])+float(matches[2]))

def calcule_scant_meal(result):
    pattern = r'\b\d+\.\d+\b'
    # Find all matches of the pattern in the text
    matches = re.findall(pattern, str(result))
    return str(float(matches[0])+float(matches[1])+float(matches[2]))



# Définir la page d'accueil
def accueil():
    st.title("Application de Gestion d'Incertitude Médicale")
    col1,col2=st.columns(2)
    with col1:

        st.markdown("""
        ## Bienvenue sur notre application de gestion d'incertitude médicale !
        
        Cette application utilise des réseaux bayésiens et des ontologies probabilistes pour aider les médecins à 
        évaluer la comorbidité entre le diabète et la dépression. Voici ce que vous pouvez faire avec notre application :
    
        """)
        st.markdown("""
                    - **Calcul de la comorbidité** : Évaluer la probabilité qu'un patient souffrant de diabète développe également une dépression.
                    - **Durée du diabète** : Calculer la probabilité que le diabète soit de longue, moyenne ou courte durée.
""")

    with col2:
        image = Image.open('depression.jpg')

        st.image(image, use_column_width=True)
    st.markdown("""
        - **Durée du diabète** : Calculer la probabilité que le diabète soit de longue, moyenne ou courte durée.
        - **État socio-économique** : Estimer la difficulté d'un patient à payer ses repas ou ses taxes en fonction de ses coordonnées et de son état socio-économique.
        - **Probabilité de l’obésité** : Calculer la probabilité que le patient a une obésité
        - **Probabilité d'exercise** : Calculer la probabilité que le patient fait des exercise sportifs
     
        Pour commencer, voir les boutons sur la barre de navigation pour aller à la page de Calcul des Inferences.
        """)

def comorbidity_page():
    
    st.title('Comorbidité')
    patientslist = list(onto.Patient.instances())
    classPatient=onto["Patient"]
    patientsname=[" "]
    for patienta in patientslist:
        patientsname.append(patienta.name)
        patientinstance=None

    selected_patient = st.selectbox('Liste des patients',patientsname)
    if selected_patient !=" ":
        evidenceDict={}
        income=' '
        homeOwnership=' '
        education_level=' '
        scant_meal=' '
        scant_rent=' '
        employementstatus=' '
        for patient in patientslist:

            if patient.name == selected_patient:    
               
                patientinstance=patient

                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Patient ID**: {patient.name}")
                    if not has_age_group[patient]==[]:
                        st.write(f"**Age Groupe:** {has_age_group[patient][0]}")
                        evidenceDict['ageGroupe']=str(int(has_age_group[patient][0]))
                    if not has_sex[patient]==[]:
                        st.write(f"**Sex:** {has_sex[patient][0]}")
                        evidenceDict['gender']=str(has_sex[patient][0])
                    if not has_ethnicity[patient]==[]:
                        st.write(f"**Ethnicity:** {has_ethnicity[patient][0]}")
                        evidenceDict['ethnicity']=str(has_ethnicity[patient][0])
                    if not has_bmi[patient]==[]:
                        st.write(f"**BMI:** {has_bmi[patient][0]}")
                        if has_bmi[patient][0]=="Normal_weight":
                            evidenceDict['BMICategory']="Snormal_weight"
                        else:
                            evidenceDict['BMICategory']=has_bmi[patient][0]

                        
                    if not do_exercise[patient]==[]:
                        st.write(f"**Exercise:** {do_exercise[patient][0]}")
                        evidenceDict['exercise']=str(do_exercise[patient][0])
                    if not has_mental[patient]==[]:
                        st.write(f"**Mental Health:** {has_mental[patient][0]}")
                        evidenceDict['mentalhealthcategory']=has_mental[patient][0] 

                    if not has_duration[patient]==[]:
                        st.write(f"**Duration of Diabetes:** {has_duration[patient][0]}")   
                        evidenceDict['durationcategory']=has_duration[patient][0]

                with col2:    
                    if not has_income[patient]==[]:
                        income=has_income[patient][0]
                        st.write(f"**Income:** {has_income[patient][0]}")
                        evidenceDict['income']=str(has_income[patient][0])
                    if not has_employ_group[patient]==[]:
                        st.write(f"**Employ Group:** {has_employ_group[patient][0]}")
                        evidenceDict['employementstatus']=str(has_employ_group[patient][0])
                    if not has_scant_rent[patient]==[]:
                        scant_rent=has_scant_rent[patient][0]
                        st.write(f"**Scant Rent:** {has_scant_rent[patient][0]}")
                        evidenceDict['scantrent']=str(has_scant_rent[patient][0])
                    if not home_own[patient]==[]:
                        homeOwnership=home_own[patient][0]
                        st.write(f"**Home Own:** {home_own[patient][0]}")
                        evidenceDict['homeOwnership']=str(home_own[patient][0])
                    if not has_ses_cate[patient]==[]:
                        st.write(f"**SES Category:** {has_ses_cate[patient][0]}")
                        evidenceDict['SESCategory']=str(has_ses_cate[patient][0])
                    if not has_scant_meal[patient]==[]:
                        scant_meal=has_scant_meal[patient][0]
                        st.write(f"**Scant Meal:** {has_scant_meal[patient][0]}")
                        evidenceDict['scantMeal']=str(has_scant_meal[patient][0])
                    if not has_education[patient]==[]:
                        education_level=has_education[patient][0]
                        st.write(f"**Education:** {has_education[patient][0]}")
                        evidenceDict['educationlevel']=str(has_education[patient][0])
                    #if not has_depression[patient]==[]:
                     #   st.write(f"**Comorbidity :** {has_depression[patient][0]}")
                

    else:
        evidenceDict={}   

        col1, col2, col3 = st.columns(3)
        with col1:
            ageGroupe = st.selectbox('Groupe d\'âge', [' ',3,4,5,6,7,8,9,10,11,12,13])
            if not ageGroupe ==' ':
                evidenceDict['ageGroupe']=str(ageGroupe)

            gender = st.selectbox('Genre', [' ','Femme', 'Homme'])
        
            

            ethnicity = st.selectbox('Ethnicité', [' ','1', '2', '3', '4' , '5'])
            if not ethnicity ==' ':
                evidenceDict['ethnicity']=str(ethnicity)
        
            exercise = st.selectbox('Exercice', [' ','Oui', 'Non'])
            
        
            income = st.selectbox('Revenu', [' ',1,2,3,4,5,6,7,8])
            if not income ==' ':
                evidenceDict['income']=str(income)
            
        with col2:
            scant_rent = st.selectbox('Location ', [' ',1, 2, 3, 4, 5])
            if not scant_rent ==' ':
                evidenceDict['scantrent']=str(scant_rent)
            

            scant_meal = st.selectbox('Bon Repas', [' ',1, 2, 3, 4, 5])
            if not scant_meal ==' ':
                evidenceDict['scantMeal']=str(scant_meal)
            
            

            homeOwnership = st.selectbox('homeOwnership ', [' ',1,2])
            if not homeOwnership ==' ':
                evidenceDict['homeOwnership']=str(homeOwnership)

            employementstatus=st.selectbox('employementstatus', [' ',1,2,3,4,5,6,7,8])
            if not employementstatus ==' ':
                evidenceDict['employementstatus']=str(employementstatus)

            

        with col3:    
            #SESCategory = st.selectbox('SESCategory ', [' ',1,2,3])
            #if not SESCategory ==' ':
            #    evidenceDict['SESCategory']=str(SESCategory)

            duration = st.selectbox('duration ', [' ','1','2','3','4'])
            if not duration ==' ':
                evidenceDict['durationcategory']=duration
    
            BMICategory =st.selectbox('BMICategory ', [' ','0','1','2','3']) 
            if not BMICategory ==' ':
                evidenceDict['BMICategory']=BMICategory

            mentalhealthcategory =st.selectbox('mentalhealthcategory ', [' ','1','2','3','4','5']) 
            if not mentalhealthcategory ==' ':
                evidenceDict['mentalhealthcategory']=mentalhealthcategory
            education_level = st.selectbox('Niveau d\'éducation',[' ',1, 2, 3, 4 , 5,6])
            if not education_level ==' ':
                evidenceDict['educationlevel']=str(education_level)    
       
        #cleaning data
        if gender=='Femme':
            gender='2'
            evidenceDict['gender']=gender
        elif gender=='Homme':
            gender='1'
            evidenceDict['gender']=gender
        if exercise=='Oui':
            exercise='1'
            evidenceDict['exercise']=exercise
        elif exercise=='Non':
            exercise='0'
            evidenceDict['exercise']=exercise
        if scant_rent =='Oui':
            scant_rent='1'
            evidenceDict['scantrent']=scant_rent
        elif scant_rent=='Non':
            scant_rent='2'
            evidenceDict['scantrent']=scant_rent

        if scant_meal =='Oui':
            scant_meal='1'
            evidenceDict['scantMeal']=scant_meal
        elif scant_meal=='Non':
            scant_meal='2'  
            evidenceDict['scantMeal']=scant_meal

    #listentry=[ageGroupe,gender,ethnicity,exercise,income,employementstatus,education_level,scant_rent,scant_meal,homeOwnership,SESCategory,duration,BMICategory,mentalhealthcategory]
    
    if st.button('Calculer la probablite de comorbidite '):
        sesCategoryvalue=sesCaluculator(income,homeOwnership,education_level,scant_meal,scant_rent,employementstatus)
        if sesCategoryvalue !=0:
            evidenceDict['SESCategory']=str(sesCategoryvalue)

        #st.write(evidenceDict)
        result=calcule_comorbidity(calculate_probability(bayesian_model,'comorbidity', evidenceDict))
        st.markdown(result)
        if not patientinstance==None:
            depressionProba[patientinstance]=[float(result)]

        
        #st.markdown("Valeur sauvegardée avec succès ")
        onto.save(file = "ontologie_probabiliste_modifiee.rdf")

        st.header("Resultat de la comorbidite")
        resultpr=float(result)

        
        col1, col2 = st.columns(2) 
        with col1: 
            progress_bar = st.empty()
            for i in np.linspace(0, resultpr, 33):
                progress_bar.pyplot(plot_progress_circle(i))
                time.sleep(0.00001)
        with col2: 
            st.subheader("   ")
            st.subheader("   ")
            st.subheader("   ")
            if float(result)>0.5:
                st.subheader("Le pourcentage de la depression est "+str(float(result)*100)+"%")
            else:
                st.subheader("Le pourcentage de la depression est  "+str(float(result)*100)+"% ")                  

#exercice page final
def exercise_final_page():
    
    st.title('Exercise')
    patientslist = list(onto.Patient.instances())
    classPatient=onto["Patient"]
    patientsname=[" "]
    for patienta in patientslist:
        patientsname.append(patienta.name)
        patientinstance=None

    selected_patient = st.selectbox('Liste des patients',patientsname)
    if selected_patient !=" ":
        evidenceDict={}
        income=' '
        homeOwnership=' '
        education_level=' '
        scant_meal=' '
        scant_rent=' '
        employementstatus=' '
        for patient in patientslist:

            if patient.name == selected_patient:    
               
                patientinstance=patient

                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Patient ID**: {patient.name}")
                    if not has_age_group[patient]==[]:
                        st.write(f"**Age Groupe:** {has_age_group[patient][0]}")
                        evidenceDict['ageGroupe']=str(int(has_age_group[patient][0]))
                    if not has_sex[patient]==[]:
                        st.write(f"**Sex:** {has_sex[patient][0]}")
                        evidenceDict['gender']=str(has_sex[patient][0])
                    if not has_ethnicity[patient]==[]:
                        st.write(f"**Ethnicity:** {has_ethnicity[patient][0]}")
                        evidenceDict['ethnicity']=str(has_ethnicity[patient][0])
                    if not has_bmi[patient]==[]:
                        st.write(f"**BMI:** {has_bmi[patient][0]}")
                        if has_bmi[patient][0]=="Normal_weight":
                            evidenceDict['BMICategory']="Snormal_weight"
                        else:
                            evidenceDict['BMICategory']=has_bmi[patient][0]

                        
                    #if not do_exercise[patient]==[]:
                    #    st.write(f"**Exercise:** {do_exercise[patient][0]}")
                    #evidenceDict['exercise']=str(do_exercise[patient][0])
                        
                    if not has_mental[patient]==[]:
                        st.write(f"**Mental Health:** {has_mental[patient][0]}")
                        evidenceDict['mentalhealthcategory']=has_mental[patient][0] 

                    if not has_duration[patient]==[]:
                        st.write(f"**Duration of Diabetes:** {has_duration[patient][0]}")   
                        evidenceDict['durationcategory']=has_duration[patient][0]

                with col2:    
                    if not has_income[patient]==[]:
                        income=has_income[patient][0]
                        st.write(f"**Income:** {has_income[patient][0]}")
                        evidenceDict['income']=str(has_income[patient][0])
                    if not has_employ_group[patient]==[]:
                        st.write(f"**Employ Group:** {has_employ_group[patient][0]}")
                        evidenceDict['employementstatus']=str(has_employ_group[patient][0])
                    if not has_scant_rent[patient]==[]:
                        scant_rent=has_scant_rent[patient][0]
                        st.write(f"**Scant Rent:** {has_scant_rent[patient][0]}")
                        evidenceDict['scantrent']=str(has_scant_rent[patient][0])
                    if not home_own[patient]==[]:
                        homeOwnership=home_own[patient][0]
                        st.write(f"**Home Own:** {home_own[patient][0]}")
                        evidenceDict['homeOwnership']=str(home_own[patient][0])
                    if not has_ses_cate[patient]==[]:
                        st.write(f"**SES Category:** {has_ses_cate[patient][0]}")
                        evidenceDict['SESCategory']=str(has_ses_cate[patient][0])
                    if not has_scant_meal[patient]==[]:
                        scant_meal=has_scant_meal[patient][0]
                        st.write(f"**Scant Meal:** {has_scant_meal[patient][0]}")
                        evidenceDict['scantMeal']=str(has_scant_meal[patient][0])
                    if not has_education[patient]==[]:
                        education_level=has_education[patient][0]
                        st.write(f"**Education:** {has_education[patient][0]}")
                        evidenceDict['educationlevel']=str(has_education[patient][0])
                    if not has_depression[patient]==[]:
                        st.write(f"**Comorbidity :** {has_depression[patient][0]}")
                

    else:
        evidenceDict={}   

        col1, col2, col3 = st.columns(3)
        with col1:
            ageGroupe = st.selectbox('Groupe d\'âge', [' ',3,4,5,6,7,8,9,10,11,12,13])
            if not ageGroupe ==' ':
                evidenceDict['ageGroupe']=str(ageGroupe)

            gender = st.selectbox('Genre', [' ','Femme', 'Homme'])
        
            

            ethnicity = st.selectbox('Ethnicité', [' ','1', '2', '3', '4' , '5'])
            if not ethnicity ==' ':
                evidenceDict['ethnicity']=str(ethnicity)
        
            #exercise = st.selectbox('Exercice', [' ','Oui', 'Non'])
            education_level = st.selectbox('Niveau d\'éducation',[' ',1, 2, 3, 4 , 5,6])
            if not education_level ==' ':
                evidenceDict['educationlevel']=str(education_level)
            
        
            income = st.selectbox('Revenu', [' ',1,2,3,4,5,6,7,8])
            if not income ==' ':
                evidenceDict['income']=str(income)
            
        with col2:
            scant_rent = st.selectbox('Location ', [' ',1, 2, 3, 4, 5])
            if not scant_rent ==' ':
                evidenceDict['scantrent']=str(scant_rent)
            

            scant_meal = st.selectbox('Bon Repas', [' ',1, 2, 3, 4, 5])
            if not scant_meal ==' ':
                evidenceDict['scantMeal']=str(scant_meal)
            

            homeOwnership = st.selectbox('homeOwnership ', [' ',1,2])
            if not homeOwnership ==' ':
                evidenceDict['homeOwnership']=str(homeOwnership)

            employementstatus=st.selectbox('employementstatus', [' ',1,2,3,4,5,6,7,8])
            if not employementstatus ==' ':
                evidenceDict['employementstatus']=str(employementstatus)

            

        with col3:    
            #SESCategory = st.selectbox('SESCategory ', [' ',1,2,3])
            #if not SESCategory ==' ':
            #    evidenceDict['SESCategory']=str(SESCategory)

            duration = st.selectbox('duration ', [' ','1','2','3','4'])
            if not duration ==' ':
                evidenceDict['durationcategory']=duration
    
            BMICategory =st.selectbox('BMICategory ', [' ','0','1','2','3']) 
            if not BMICategory ==' ':
                evidenceDict['BMICategory']=BMICategory

            mentalhealthcategory =st.selectbox('mentalhealthcategory ', [' ','1','2','3','4','5']) 
            if not mentalhealthcategory ==' ':
                evidenceDict['mentalhealthcategory']=mentalhealthcategory
            comorbidity = st.selectbox('comorbidity', [' ','Oui', 'Non'])    


        #cleaning data
        if gender=='Femme':
            gender='2'
            evidenceDict['gender']=gender
        elif gender=='Homme':
            gender='1'
            evidenceDict['gender']=gender
        #if exercise=='Oui':
        #    exercise='1'
        #    evidenceDict['exercise']=exercise
        #elif exercise=='Non':
        #    exercise='0'
        #    evidenceDict['exercise']=exercise
        if scant_rent =='Oui':
            scant_rent='1'
            evidenceDict['scantrent']=scant_rent
        elif scant_rent=='Non':
            scant_rent='2'
            evidenceDict['scantrent']=scant_rent

        if scant_meal =='Oui':
            scant_meal='1'
            evidenceDict['scantMeal']=scant_meal
        elif scant_meal=='Non':
            scant_meal='2'  
            evidenceDict['scantMeal']=scant_meal
        if comorbidity=='Oui':
            comorbidity='1'
            evidenceDict['comorbidity']=comorbidity
        elif comorbidity=='Non':
            comorbidity='2'
            evidenceDict['comorbidity']=comorbidity           

    #listentry=[ageGroupe,gender,ethnicity,exercise,income,employementstatus,education_level,scant_rent,scant_meal,homeOwnership,SESCategory,duration,BMICategory,mentalhealthcategory]

    if st.button('Calculer la probablite de l\'exercise '):
        #st.write(evidenceDict)
        sesCategoryvalue=sesCaluculator(income,homeOwnership,education_level,scant_meal,scant_rent,employementstatus)
        if sesCategoryvalue !=0:
            evidenceDict['SESCategory']=str(sesCategoryvalue)

        result=calcule_exercise(calculate_probability(bayesian_model,'exercise', evidenceDict))
        onto.save(file = "ontologie_probabiliste_modifiee.rdf")
        st.markdown(result)
        if not patientinstance==None:
            exercisePoroba[patientinstance]=[float(result)]

        
        #st.markdown("Valeur sauvegardée avec succès ")

        st.header("Resultat de la probabilite")
        resultpr=float(result)

        
        col1, col2 = st.columns(2) 
        with col1: 
            progress_bar = st.empty()
            for i in np.linspace(0, resultpr, 33):
                progress_bar.pyplot(plot_progress_circle(i))
                time.sleep(0.00001)
        with col2: 
            st.subheader("   ")
            st.subheader("   ")
            st.subheader("   ")
            if float(result)>0.5:
                st.subheader("Le pourcentage de l\'exercise est "+str(float(result)*100)+"%")
            else:
                st.subheader("Le pourcentage de l\'exercise est  "+str(float(result)*100)+"% ")                  



        


#page obesite
def obesity_page():
    st.markdown(page_bg_img, unsafe_allow_html=True)
    st.title('Obésité')
    patientslist = list(onto.Patient.instances())
    classPatient=onto["Patient"]
    patientsname=[" "]
    for patienta in patientslist:
        patientsname.append(patienta.name)
        patientinstance=None

    selected_patient = st.selectbox('Liste des patients',patientsname)
    if selected_patient !=" ":
        evidenceDict={}
        income=' '
        homeOwnership=' '
        education_level=' '
        scant_meal=' '
        scant_rent=' '
        employementstatus=' '
        for patient in patientslist:

            if patient.name == selected_patient:    
               
                patientinstance=patient

                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Patient ID**: {patient.name}")
                    if not has_age_group[patient]==[]:
                        st.write(f"**Age Groupe:** {has_age_group[patient][0]}")
                        evidenceDict['ageGroupe']=str(int(has_age_group[patient][0]))
                    if not has_sex[patient]==[]:
                        st.write(f"**Sex:** {has_sex[patient][0]}")
                        evidenceDict['gender']=str(has_sex[patient][0])
                    if not has_ethnicity[patient]==[]:
                        st.write(f"**Ethnicity:** {has_ethnicity[patient][0]}")
                        evidenceDict['ethnicity']=str(has_ethnicity[patient][0])
                    #if not has_bmi[patient]==[]:
                    #    st.write(f"**BMI:** {has_bmi[patient][0]}")
                    #    if has_bmi[patient][0]=="Normal_weight":
                    #        evidenceDict['BMICategory']="Snormal_weight"
                    #    else:
                    #        evidenceDict['BMICategory']=has_bmi[patient][0]

                        
                    if not do_exercise[patient]==[]:
                        st.write(f"**Exercise:** {do_exercise[patient][0]}")
                        evidenceDict['exercise']=str(do_exercise[patient][0])
                        
                    if not has_mental[patient]==[]:
                        st.write(f"**Mental Health:** {has_mental[patient][0]}")
                        evidenceDict['mentalhealthcategory']=has_mental[patient][0] 

                    if not has_duration[patient]==[]:
                        st.write(f"**Duration of Diabetes:** {has_duration[patient][0]}")   
                        evidenceDict['durationcategory']=has_duration[patient][0]

                with col2:    
                    if not has_income[patient]==[]:
                        income=has_income[patient][0]
                        st.write(f"**Income:** {has_income[patient][0]}")
                        evidenceDict['income']=str(has_income[patient][0])
                    if not has_employ_group[patient]==[]:
                        st.write(f"**Employ Group:** {has_employ_group[patient][0]}")
                        evidenceDict['employementstatus']=str(has_employ_group[patient][0])
                    if not has_scant_rent[patient]==[]:
                        scant_rent=has_scant_rent[patient][0]
                        st.write(f"**Scant Rent:** {has_scant_rent[patient][0]}")
                        evidenceDict['scantrent']=str(has_scant_rent[patient][0])
                    if not home_own[patient]==[]:
                        homeOwnership=home_own[patient][0]
                        st.write(f"**Home Own:** {home_own[patient][0]}")
                        evidenceDict['homeOwnership']=str(home_own[patient][0])
                    if not has_ses_cate[patient]==[]:
                        st.write(f"**SES Category:** {has_ses_cate[patient][0]}")
                        evidenceDict['SESCategory']=str(has_ses_cate[patient][0])
                    if not has_scant_meal[patient]==[]:
                        scant_meal=has_scant_meal[patient][0]
                        st.write(f"**Scant Meal:** {has_scant_meal[patient][0]}")
                        evidenceDict['scantMeal']=str(has_scant_meal[patient][0])
                    if not has_education[patient]==[]:
                        education_level=has_education[patient][0]
                        st.write(f"**Education:** {has_education[patient][0]}")
                        evidenceDict['educationlevel']=str(has_education[patient][0])
                    if not has_depression[patient]==[]:
                        st.write(f"**Comorbidity :** {has_depression[patient][0]}")
                

    else:
        evidenceDict={}   

        col1, col2, col3 = st.columns(3)
        with col1:
            ageGroupe = st.selectbox('Groupe d\'âge', [' ',3,4,5,6,7,8,9,10,11,12,13])
            if not ageGroupe ==' ':
                evidenceDict['ageGroupe']=str(ageGroupe)

            gender = st.selectbox('Genre', [' ','Femme', 'Homme'])
        
            

            ethnicity = st.selectbox('Ethnicité', [' ','1', '2', '3', '4' , '5'])
            if not ethnicity ==' ':
                evidenceDict['ethnicity']=str(ethnicity)
        
            exercise = st.selectbox('Exercice', [' ','Oui', 'Non'])
            
        
            income = st.selectbox('Revenu', [' ',1,2,3,4,5,6,7,8])
            if not income ==' ':
                evidenceDict['income']=str(income)
            
        with col2:
            scant_rent = st.selectbox('Location ', [' ',1, 2, 3, 4, 5])
            if not scant_rent ==' ':
                evidenceDict['scantrent']=str(scant_rent)
            

            scant_meal = st.selectbox('Bon Repas', [' ',1, 2, 3, 4, 5])
            if not scant_meal ==' ':
                evidenceDict['scantMeal']=str(scant_meal)
            

            homeOwnership = st.selectbox('homeOwnership ', [' ',1,2])
            if not homeOwnership ==' ':
                evidenceDict['homeOwnership']=str(homeOwnership)

            employementstatus=st.selectbox('employementstatus', [' ',1,2,3,4,5,6,7,8])
            if not employementstatus ==' ':
                evidenceDict['employementstatus']=str(employementstatus)

            
        with col3:    
            #SESCategory = st.selectbox('SESCategory ', [' ',1,2,3])
            #if not SESCategory ==' ':
            #evidenceDict['SESCategory']=str(SESCategory)
            comorbidity = st.selectbox('comorbidity', [' ','Oui', 'Non'])        

            duration = st.selectbox('duration ', [' ','1','2','3','4','5'])
            if not duration ==' ':
                evidenceDict['durationcategory']=duration
    
            #BMICategory =st.selectbox('BMICategory ', [' ','overweight','obese','Snormal_weight']) 
            #if not BMICategory ==' ':
            #    evidenceDict['BMICategory']=BMICategory

            mentalhealthcategory =st.selectbox('mentalhealthcategory ', [' ','1','2','3','4','5']) 
            if not mentalhealthcategory ==' ':
                evidenceDict['mentalhealthcategory']=mentalhealthcategory

            education_level = st.selectbox('Niveau d\'éducation',[' ',1, 2, 3, 4 , 5,6])
            if not education_level ==' ':
                evidenceDict['educationlevel']=str(education_level)



        #cleaning data
        if gender=='Femme':
            gender='2'
            evidenceDict['gender']=gender
        elif gender=='Homme':
            gender='1'
            evidenceDict['gender']=gender
        if exercise=='Oui':
            exercise='1'
            evidenceDict['exercise']=exercise
        elif exercise=='Non':
            exercise='0'
            evidenceDict['exercise']=exercise
        if scant_rent =='Oui':
            scant_rent='1'
            evidenceDict['scantrent']=scant_rent
        elif scant_rent=='Non':
            scant_rent='2'
            evidenceDict['scantrent']=scant_rent

        if scant_meal =='Oui':
            scant_meal='1'
            evidenceDict['scantMeal']=scant_meal
        elif scant_meal=='Non':
            scant_meal='2'  
            evidenceDict['scantMeal']=scant_meal

        if comorbidity=='Oui':
            comorbidity='1'
            evidenceDict['comorbidity']=comorbidity
        elif comorbidity=='Non':
            comorbidity='2'
            evidenceDict['comorbidity']=comorbidity       

    #listentry=[ageGroupe,gender,ethnicity,exercise,income,employementstatus,education_level,scant_rent,scant_meal,homeOwnership,SESCategory,duration,BMICategory,mentalhealthcategory]

    if st.button('Calculer la probablite de l\'obésité '):
        #st.write(evidenceDict)
        sesCategoryvalue=sesCaluculator(income,homeOwnership,education_level,scant_meal,scant_rent,employementstatus)
        if sesCategoryvalue !=0:
            evidenceDict['SESCategory']=str(sesCategoryvalue)
        result=calcule_obesity(calculate_probability(bayesian_model,'BMICategory', evidenceDict))
        st.markdown(result)
        if not patientinstance==None:
            obeseProba[patientinstance]=[float(result)]
        
        #st.markdown("Valeur sauvegardée avec succès ")
        onto.save(file = "ontologie_probabiliste_modifiee.rdf")
        st.header("Resultat de la probabilite")
        resultpr=float(result)

        
        col1, col2 = st.columns(2) 
        with col1: 
            progress_bar = st.empty()
            for i in np.linspace(0, resultpr, 33):
                progress_bar.pyplot(plot_progress_circle(i))
                time.sleep(0.00001)
        with col2: 
            st.subheader("   ")
            st.subheader("   ")
            st.subheader("   ")
            if float(result)>0.5:
                st.subheader("Le pourcentage de l\'obésité est "+str(float(result)*100)+"%")
            else:
                st.subheader("Le pourcentage de l\'obésité est  "+str(float(result)*100)+"% ")                  
   


def shortDuration_page():
    st.title('Un diabète de courte durée')
    patientslist = list(onto.Patient.instances())
    classPatient=onto["Patient"]
    patientsname=[" "]
    for patienta in patientslist:
        patientsname.append(patienta.name)
        patientinstance=None

    selected_patient = st.selectbox('Liste des patients',patientsname)
    if selected_patient !=" ":
        evidenceDict={}
        income=' '
        homeOwnership=' '
        education_level=' '
        scant_meal=' '
        scant_rent=' '
        employementstatus=' '
        for patient in patientslist:

            if patient.name == selected_patient:    
               
                patientinstance=patient

                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Patient ID**: {patient.name}")
                    if not has_age_group[patient]==[]:
                        st.write(f"**Age Groupe:** {has_age_group[patient][0]}")
                        evidenceDict['ageGroupe']=str(int(has_age_group[patient][0]))
                    if not has_sex[patient]==[]:
                        st.write(f"**Sex:** {has_sex[patient][0]}")
                        evidenceDict['gender']=str(has_sex[patient][0])
                    if not has_ethnicity[patient]==[]:
                        st.write(f"**Ethnicity:** {has_ethnicity[patient][0]}")
                        evidenceDict['ethnicity']=str(has_ethnicity[patient][0])
                    if not has_bmi[patient]==[]:
                        st.write(f"**BMI:** {has_bmi[patient][0]}")
                        if has_bmi[patient][0]=="Normal_weight":
                            evidenceDict['BMICategory']="Snormal_weight"
                        else:
                            evidenceDict['BMICategory']=has_bmi[patient][0]

                        
                    if not do_exercise[patient]==[]:
                        st.write(f"**Exercise:** {do_exercise[patient][0]}")
                        evidenceDict['exercise']=str(do_exercise[patient][0])
                        
                    if not has_mental[patient]==[]:
                        st.write(f"**Mental Health:** {has_mental[patient][0]}")
                        evidenceDict['mentalhealthcategory']=has_mental[patient][0] 

                    #if not has_duration[patient]==[]:
                        #st.write(f"**Duration of Diabetes:** {has_duration[patient][0]}")   
                        #evidenceDict['durationcategory']=has_duration[patient][0]

                with col2:    
                    if not has_income[patient]==[]:
                        income=has_income[patient][0]
                        st.write(f"**Income:** {has_income[patient][0]}")
                        evidenceDict['income']=str(has_income[patient][0])
                    if not has_employ_group[patient]==[]:
                        st.write(f"**Employ Group:** {has_employ_group[patient][0]}")
                        evidenceDict['employementstatus']=str(has_employ_group[patient][0])
                    if not has_scant_rent[patient]==[]:
                        scant_rent=has_scant_rent[patient][0]
                        st.write(f"**Scant Rent:** {has_scant_rent[patient][0]}")
                        evidenceDict['scantrent']=str(has_scant_rent[patient][0])
                    if not home_own[patient]==[]:
                        homeOwnership=home_own[patient][0]
                        st.write(f"**Home Own:** {home_own[patient][0]}")
                        evidenceDict['homeOwnership']=str(home_own[patient][0])
                    if not has_ses_cate[patient]==[]:
                        st.write(f"**SES Category:** {has_ses_cate[patient][0]}")
                        evidenceDict['SESCategory']=str(has_ses_cate[patient][0])
                    if not has_scant_meal[patient]==[]:
                        scant_meal=has_scant_meal[patient][0]
                        st.write(f"**Scant Meal:** {has_scant_meal[patient][0]}")
                        evidenceDict['scantMeal']=str(has_scant_meal[patient][0])
                    if not has_education[patient]==[]:
                        education_level=has_education[patient][0]
                        st.write(f"**Education:** {has_education[patient][0]}")
                        evidenceDict['educationlevel']=str(has_education[patient][0])
                    #if not has_depression[patient]==[]:
                     #   st.write(f"**Comorbidity :** {has_depression[patient][0]}")
                

    else:
        evidenceDict={}   

        col1, col2, col3 = st.columns(3)
        with col1:
            ageGroupe = st.selectbox('Groupe d\'âge', [' ',3,4,5,6,7,8,9,10,11,12,13])
            if not ageGroupe ==' ':
                evidenceDict['ageGroupe']=str(ageGroupe)

            gender = st.selectbox('Genre', [' ','Femme', 'Homme'])
        
            

            ethnicity = st.selectbox('Ethnicité', [' ','1', '2', '3', '4' , '5'])
            if not ethnicity ==' ':
                evidenceDict['ethnicity']=str(ethnicity)
        
            exercise = st.selectbox('Exercice', [' ','Oui', 'Non'])
            
        
            income = st.selectbox('Revenu', [' ',1,2,3,4,5,6,7,8])
            if not income ==' ':
                evidenceDict['income']=str(income)
            
        with col2:
            scant_rent = st.selectbox('Location ', [' ',1, 2, 3, 4, 5])
            if not scant_rent ==' ':
                evidenceDict['scantrent']=str(scant_rent)
            

            scant_meal = st.selectbox('Bon Repas', [' ',1, 2, 3, 4, 5])
            if not scant_meal ==' ':
                evidenceDict['scantMeal']=str(scant_meal)
            

            homeOwnership = st.selectbox('homeOwnership ', [' ',1,2])
            if not homeOwnership ==' ':
                evidenceDict['homeOwnership']=str(homeOwnership)

            employementstatus=st.selectbox('employementstatus', [' ',1,2,3,4,5,6,7,8])
            if not employementstatus ==' ':
                evidenceDict['employementstatus']=str(employementstatus)

            education_level = st.selectbox('Niveau d\'éducation',[' ',1, 2, 3, 4 , 5,6])
            if not education_level ==' ':
                evidenceDict['educationlevel']=str(education_level)

        with col3:    
            SESCategory = st.selectbox('SESCategory ', [' ',1,2,3])
            if not SESCategory ==' ':
                evidenceDict['SESCategory']=str(SESCategory)
            comorbidity = st.selectbox('comorbidity', [' ','Oui', 'Non'])    

            #duration = st.selectbox('duration ', [' ','short','medium','long'])
            #if not duration ==' ':
               # evidenceDict['durationcategory']=duration
    
            BMICategory =st.selectbox('BMICategory ', [' ','0','1','2','3']) 
            if not BMICategory ==' ':
                evidenceDict['BMICategory']=BMICategory

            mentalhealthcategory =st.selectbox('mentalhealthcategory ', [' ','1','2','3','4','5']) 
            if not mentalhealthcategory ==' ':
                evidenceDict['mentalhealthcategory']=mentalhealthcategory


        #cleaning data
        if gender=='Femme':
            gender='2'
            evidenceDict['gender']=gender
        elif gender=='Homme':
            gender='1'
            evidenceDict['gender']=gender
        if exercise=='Oui':
            exercise='1'
            evidenceDict['exercise']=exercise
        elif exercise=='Non':
            exercise='0'
            evidenceDict['exercise']=exercise
        if scant_rent =='Oui':
            scant_rent='1'
            evidenceDict['scantrent']=scant_rent
        elif scant_rent=='Non':
            scant_rent='2'
            evidenceDict['scantrent']=scant_rent

        if scant_meal =='Oui':
            scant_meal='1'
            evidenceDict['scantMeal']=scant_meal
        elif scant_meal=='Non':
            scant_meal='2'  
            evidenceDict['scantMeal']=scant_meal

        if comorbidity=='Oui':
            comorbidity='1'
            evidenceDict['comorbidity']=comorbidity
        elif comorbidity=='Non':
            comorbidity='2'
            evidenceDict['comorbidity']=comorbidity    

    #listentry=[ageGroupe,gender,ethnicity,exercise,income,employementstatus,education_level,scant_rent,scant_meal,homeOwnership,SESCategory,duration,BMICategory,mentalhealthcategory]

    if st.button('Calculer la probablite d\'un diabète de courte durée '):
        #st.write(evidenceDict)
        sesCategoryvalue=sesCaluculator(income,homeOwnership,education_level,scant_meal,scant_rent,employementstatus)
        if sesCategoryvalue !=0:
            evidenceDict['SESCategory']=str(sesCategoryvalue)
        result=calcule_short_duration(calculate_probability(bayesian_model,'durationcategory', evidenceDict))
        onto.save(file = "ontologie_probabiliste_modifiee.rdf")
        st.markdown(result)
        if not patientinstance==None:
            shortDurationProba[patientinstance]=[float(result)]
        
        #st.markdown("Valeur sauvegardée avec succès ")

        st.header("Resultat de la probabilite")
        resultpr=float(result)

        
        col1, col2 = st.columns(2) 
        with col1: 
            progress_bar = st.empty()
            for i in np.linspace(0, resultpr, 33):
                progress_bar.pyplot(plot_progress_circle(i))
                time.sleep(0.00001)
        with col2: 
            st.subheader("   ")
            st.subheader("   ")
            st.subheader("   ")
            if float(result)>0.5:
                st.subheader("Le pourcentage d'un diabète de courte durée est "+str(float(result)*100)+"%")
            else:
                st.subheader("Le pourcentage d'un diabète de courte durée est  "+str(float(result)*100)+"% ")


def moyenDuration_page():
    st.title('Un diabète de moyenne durée')
    patientslist = list(onto.Patient.instances())
    classPatient=onto["Patient"]
    patientsname=[" "]
    for patienta in patientslist:
        patientsname.append(patienta.name)
        patientinstance=None

    selected_patient = st.selectbox('Liste des patients',patientsname)
    if selected_patient !=" ":
        evidenceDict={}
        income=' '
        homeOwnership=' '
        education_level=' '
        scant_meal=' '
        scant_rent=' '
        employementstatus=' '
        for patient in patientslist:

            if patient.name == selected_patient:    
               
                patientinstance=patient

                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Patient ID**: {patient.name}")
                    if not has_age_group[patient]==[]:
                        st.write(f"**Age Groupe:** {has_age_group[patient][0]}")
                        evidenceDict['ageGroupe']=str(int(has_age_group[patient][0]))
                    if not has_sex[patient]==[]:
                        st.write(f"**Sex:** {has_sex[patient][0]}")
                        evidenceDict['gender']=str(has_sex[patient][0])
                    if not has_ethnicity[patient]==[]:
                        st.write(f"**Ethnicity:** {has_ethnicity[patient][0]}")
                        evidenceDict['ethnicity']=str(has_ethnicity[patient][0])
                    if not has_bmi[patient]==[]:
                        st.write(f"**BMI:** {has_bmi[patient][0]}")
                        if has_bmi[patient][0]=="Normal_weight":
                            evidenceDict['BMICategory']="Snormal_weight"
                        else:
                            evidenceDict['BMICategory']=has_bmi[patient][0]

                        
                    if not do_exercise[patient]==[]:
                        st.write(f"**Exercise:** {do_exercise[patient][0]}")
                        evidenceDict['exercise']=str(do_exercise[patient][0])
                        
                    if not has_mental[patient]==[]:
                        st.write(f"**Mental Health:** {has_mental[patient][0]}")
                        evidenceDict['mentalhealthcategory']=has_mental[patient][0] 

                    #if not has_duration[patient]==[]:
                        #st.write(f"**Duration of Diabetes:** {has_duration[patient][0]}")   
                        #evidenceDict['durationcategory']=has_duration[patient][0]

                with col2:    
                    if not has_income[patient]==[]:
                        income=has_income[patient][0]
                        st.write(f"**Income:** {has_income[patient][0]}")
                        evidenceDict['income']=str(has_income[patient][0])
                    if not has_employ_group[patient]==[]:
                        st.write(f"**Employ Group:** {has_employ_group[patient][0]}")
                        evidenceDict['employementstatus']=str(has_employ_group[patient][0])
                    if not has_scant_rent[patient]==[]:
                        scant_rent=has_scant_rent[patient][0]
                        st.write(f"**Scant Rent:** {has_scant_rent[patient][0]}")
                        evidenceDict['scantrent']=str(has_scant_rent[patient][0])
                    if not home_own[patient]==[]:
                        homeOwnership=home_own[patient][0]
                        st.write(f"**Home Own:** {home_own[patient][0]}")
                        evidenceDict['homeOwnership']=str(home_own[patient][0])
                    if not has_ses_cate[patient]==[]:
                        st.write(f"**SES Category:** {has_ses_cate[patient][0]}")
                        evidenceDict['SESCategory']=str(has_ses_cate[patient][0])
                    if not has_scant_meal[patient]==[]:
                        scant_meal=has_scant_meal[patient][0]
                        st.write(f"**Scant Meal:** {has_scant_meal[patient][0]}")
                        evidenceDict['scantMeal']=str(has_scant_meal[patient][0])
                    if not has_education[patient]==[]:
                        education_level=has_education[patient][0]
                        st.write(f"**Education:** {has_education[patient][0]}")
                        evidenceDict['educationlevel']=str(has_education[patient][0])
                    #if not has_depression[patient]==[]:
                     #   st.write(f"**Comorbidity :** {has_depression[patient][0]}")
                

    else:
        evidenceDict={}   

        col1, col2, col3 = st.columns(3)
        with col1:
            ageGroupe = st.selectbox('Groupe d\'âge', [' ',3,4,5,6,7,8,9,10,11,12,13])
            if not ageGroupe ==' ':
                evidenceDict['ageGroupe']=str(ageGroupe)

            gender = st.selectbox('Genre', [' ','Femme', 'Homme'])
        
            

            ethnicity = st.selectbox('Ethnicité', [' ','1', '2', '3', '4' , '5'])
            if not ethnicity ==' ':
                evidenceDict['ethnicity']=str(ethnicity)
        
            exercise = st.selectbox('Exercice', [' ','Oui', 'Non'])
            
        
            income = st.selectbox('Revenu', [' ',1,2,3,4,5,6,7,8])
            if not income ==' ':
                evidenceDict['income']=str(income)
            
        with col2:
            scant_rent = st.selectbox('Location ', [' ',1, 2, 3, 4, 5])
            if not scant_rent ==' ':
                evidenceDict['scantrent']=str(scant_rent)
            

            scant_meal = st.selectbox('Bon Repas', [' ',1, 2, 3, 4, 5])
            if not scant_meal ==' ':
                evidenceDict['scantMeal']=str(scant_meal)
            

            homeOwnership = st.selectbox('homeOwnership ', [' ',1,2])
            if not homeOwnership ==' ':
                evidenceDict['homeOwnership']=str(homeOwnership)

            employementstatus=st.selectbox('employementstatus', [' ',1,2,3,4,5,6,7,8])
            if not employementstatus ==' ':
                evidenceDict['employementstatus']=str(employementstatus)

            education_level = st.selectbox('Niveau d\'éducation',[' ',1, 2, 3, 4 , 5,6])
            if not education_level ==' ':
                evidenceDict['educationlevel']=str(education_level)

        with col3:    
            SESCategory = st.selectbox('SESCategory ', [' ',1,2,3])
            if not SESCategory ==' ':
                evidenceDict['SESCategory']=str(SESCategory)
            comorbidity = st.selectbox('comorbidity', [' ','Oui', 'Non'])    

            #duration = st.selectbox('duration ', [' ','short','medium','long'])
            #if not duration ==' ':
               # evidenceDict['durationcategory']=duration
    
            BMICategory =st.selectbox('BMICategory ', [' ','0','1','2','3']) 
            if not BMICategory ==' ':
                evidenceDict['BMICategory']=BMICategory

            mentalhealthcategory =st.selectbox('mentalhealthcategory ', [' ','1','2','3','4','5']) 
            if not mentalhealthcategory ==' ':
                evidenceDict['mentalhealthcategory']=mentalhealthcategory


        #cleaning data
        if gender=='Femme':
            gender='2'
            evidenceDict['gender']=gender
        elif gender=='Homme':
            gender='1'
            evidenceDict['gender']=gender
        if exercise=='Oui':
            exercise='1'
            evidenceDict['exercise']=exercise
        elif exercise=='Non':
            exercise='0'
            evidenceDict['exercise']=exercise
        if scant_rent =='Oui':
            scant_rent='1'
            evidenceDict['scantrent']=scant_rent
        elif scant_rent=='Non':
            scant_rent='2'
            evidenceDict['scantrent']=scant_rent

        if scant_meal =='Oui':
            scant_meal='1'
            evidenceDict['scantMeal']=scant_meal
        elif scant_meal=='Non':
            scant_meal='2'  
            evidenceDict['scantMeal']=scant_meal

        if comorbidity=='Oui':
            comorbidity='1'
            evidenceDict['comorbidity']=comorbidity
        elif comorbidity=='Non':
            comorbidity='2'
            evidenceDict['comorbidity']=comorbidity    

    #listentry=[ageGroupe,gender,ethnicity,exercise,income,employementstatus,education_level,scant_rent,scant_meal,homeOwnership,SESCategory,duration,BMICategory,mentalhealthcategory]

    if st.button('Calculer la probablite d\'un diabète de moyenne durée '):
        #st.write(evidenceDict)
        sesCategoryvalue=sesCaluculator(income,homeOwnership,education_level,scant_meal,scant_rent,employementstatus)
        if sesCategoryvalue !=0:
            evidenceDict['SESCategory']=str(sesCategoryvalue)
        result=calcule_medium_duration(calculate_probability(bayesian_model,'durationcategory', evidenceDict))
        st.markdown(result)
        if not patientinstance==None:
            mediumDurationProba[patientinstance]=[float(result)]

        
        #st.markdown("Valeur sauvegardée avec succès ")
        onto.save(file = "ontologie_probabiliste_modifiee.rdf")
        st.header("Resultat de la probabilite")
        resultpr=float(result)

        
        col1, col2 = st.columns(2) 
        with col1: 
            progress_bar = st.empty()
            for i in np.linspace(0, resultpr, 33):
                progress_bar.pyplot(plot_progress_circle(i))
                time.sleep(0.00001)
        with col2: 
            st.subheader("   ")
            st.subheader("   ")
            st.subheader("   ")
            if float(result)>0.5:
                st.subheader("Le pourcentage d'un diabète de mpyenne durée est "+str(float(result)*100)+"%")
            else:
                st.subheader("Le pourcentage d'un diabète de moyenne durée est  "+str(float(result)*100)+"% ")


def longDuration_page():
    
    st.title('Un diabète de longue durée')
    patientslist = list(onto.Patient.instances())
    classPatient=onto["Patient"]
    patientsname=[" "]
    for patienta in patientslist:
        patientsname.append(patienta.name)
        patientinstance=None

    selected_patient = st.selectbox('Liste des patients',patientsname)
    if selected_patient !=" ":
        evidenceDict={}
        income=' '
        homeOwnership=' '
        education_level=' '
        scant_meal=' '
        scant_rent=' '
        employementstatus=' '
        for patient in patientslist:

            if patient.name == selected_patient:    
               
                patientinstance=patient

                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Patient ID**: {patient.name}")
                    if not has_age_group[patient]==[]:
                        st.write(f"**Age Groupe:** {has_age_group[patient][0]}")
                        evidenceDict['ageGroupe']=str(int(has_age_group[patient][0]))
                    if not has_sex[patient]==[]:
                        st.write(f"**Sex:** {has_sex[patient][0]}")
                        evidenceDict['gender']=str(has_sex[patient][0])
                    if not has_ethnicity[patient]==[]:
                        st.write(f"**Ethnicity:** {has_ethnicity[patient][0]}")
                        evidenceDict['ethnicity']=str(has_ethnicity[patient][0])
                    if not has_bmi[patient]==[]:
                        st.write(f"**BMI:** {has_bmi[patient][0]}")
                        if has_bmi[patient][0]=="Normal_weight":
                            evidenceDict['BMICategory']="Snormal_weight"
                        else:
                            evidenceDict['BMICategory']=has_bmi[patient][0]

                        
                    if not do_exercise[patient]==[]:
                        st.write(f"**Exercise:** {do_exercise[patient][0]}")
                        evidenceDict['exercise']=str(do_exercise[patient][0])
                        
                    if not has_mental[patient]==[]:
                        st.write(f"**Mental Health:** {has_mental[patient][0]}")
                        evidenceDict['mentalhealthcategory']=has_mental[patient][0] 

                    #if not has_duration[patient]==[]:
                        #st.write(f"**Duration of Diabetes:** {has_duration[patient][0]}")   
                        #evidenceDict['durationcategory']=has_duration[patient][0]

                with col2:    
                    if not has_income[patient]==[]:
                        income=has_income[patient][0]
                        st.write(f"**Income:** {has_income[patient][0]}")
                        evidenceDict['income']=str(has_income[patient][0])
                    if not has_employ_group[patient]==[]:
                        st.write(f"**Employ Group:** {has_employ_group[patient][0]}")
                        evidenceDict['employementstatus']=str(has_employ_group[patient][0])
                    if not has_scant_rent[patient]==[]:
                        scant_rent=has_scant_rent[patient][0]
                        st.write(f"**Scant Rent:** {has_scant_rent[patient][0]}")
                        evidenceDict['scantRent']=str(has_scant_rent[patient][0])
                    if not home_own[patient]==[]:
                        homeOwnership=home_own[patient][0]
                        st.write(f"**Home Own:** {home_own[patient][0]}")
                        evidenceDict['homeOwnership']=str(home_own[patient][0])
                    if not has_ses_cate[patient]==[]:
                        st.write(f"**SES Category:** {has_ses_cate[patient][0]}")
                        evidenceDict['SESCategory']=str(has_ses_cate[patient][0])
                    if not has_scant_meal[patient]==[]:
                        scant_meal=has_scant_meal[patient][0]
                        st.write(f"**Scant Meal:** {has_scant_meal[patient][0]}")
                        evidenceDict['scantMeal']=str(has_scant_meal[patient][0])
                    if not has_education[patient]==[]:
                        education_level=has_education[patient][0]
                        st.write(f"**Education:** {has_education[patient][0]}")
                        evidenceDict['educationlevel']=str(has_education[patient][0])
                    #if not has_depression[patient]==[]:
                     #   st.write(f"**Comorbidity :** {has_depression[patient][0]}")
                

    else:
        evidenceDict={}   

        col1, col2, col3 = st.columns(3)
        with col1:
            ageGroupe = st.selectbox('Groupe d\'âge', [' ',3,4,5,6,7,8,9,10,11,12,13])
            if not ageGroupe ==' ':
                evidenceDict['ageGroupe']=str(ageGroupe)

            gender = st.selectbox('Genre', [' ','Femme', 'Homme'])
            ethnicity = st.selectbox('Ethnicité', [' ','1', '2', '3', '4' , '5'])
            if not ethnicity ==' ':
                evidenceDict['ethnicity']=str(ethnicity)
        
            exercise = st.selectbox('Exercice', [' ','Oui', 'Non'])
            #evidenceDict['exercise']=str(do_exercise[patient][0])
            
            income = st.selectbox('Revenu', [' ',1,2,3,4,5,6,7,8])
            if not income ==' ':
                evidenceDict['income']=str(income)
            
        with col2:
            scant_rent = st.selectbox('Location ', [' ',1, 2, 3, 4, 5])
            if not scant_rent ==' ':
                evidenceDict['scantRent']=str(scant_rent)
            

            scant_meal = st.selectbox('Bon Repas', [' ',1, 2, 3, 4, 5])
            if not scant_meal ==' ':
                evidenceDict['scantMeal']=str(scant_meal)
            
            

            homeOwnership = st.selectbox('homeOwnership ', [' ',1,2])
            if not homeOwnership ==' ':
                evidenceDict['homeOwnership']=str(homeOwnership)

            employementstatus=st.selectbox('employementstatus', [' ',1,2,3,4,5,6,7,8])
            if not employementstatus ==' ':
                evidenceDict['employementstatus']=str(employementstatus)

            

        with col3:    
            #SESCategory = st.selectbox('SESCategory ', [' ',1,2,3])
            #if not SESCategory ==' ':
             #   evidenceDict['SESCategory']=str(SESCategory)
            comorbidity = st.selectbox('comorbidity', [' ','Oui', 'Non'])    

            #duration = st.selectbox('duration ', [' ','short','medium','long'])
            #if not duration ==' ':
               # evidenceDict['durationcategory']=duration
    
            BMICategory =st.selectbox('BMICategory ', [' ','0','1','2','3']) 
            if not BMICategory ==' ':
                evidenceDict['BMICategory']=BMICategory

            mentalhealthcategory =st.selectbox('mentalhealthcategory ', [' ','1','2','3','4','5']) 
            if not mentalhealthcategory ==' ':
                evidenceDict['mentalhealthcategory']=mentalhealthcategory

            education_level = st.selectbox('Niveau d\'éducation',[' ',1, 2, 3, 4 , 5,6])
            if not education_level ==' ':
                evidenceDict['educationlevel']=str(education_level)    


        #cleaning data
        if gender=='Femme':
            gender='2'
            evidenceDict['gender']=gender
        elif gender=='Homme':
            gender='1'
            evidenceDict['gender']=gender
        if exercise=='Oui':
            exercise='1'
            evidenceDict['exercise']=exercise
        elif exercise=='Non':
            exercise='0'
            evidenceDict['exercise']=exercise
        if scant_rent =='Oui':
            scant_rent='1'
            evidenceDict['scantrent']=scant_rent
        elif scant_rent=='Non':
            scant_rent='2'
            evidenceDict['scantrent']=scant_rent

        if scant_meal =='Oui':
            scant_meal='1'
            evidenceDict['scantMeal']=scant_meal
        elif scant_meal=='Non':
            scant_meal='2'  
            evidenceDict['scantMeal']=scant_meal

        if comorbidity=='Oui':
            comorbidity='1'
            evidenceDict['comorbidity']=comorbidity
        elif comorbidity=='Non' :
            comorbidity='2'
            evidenceDict['comorbidity']=comorbidity    

    #listentry=[ageGroupe,gender,ethnicity,exercise,income,employementstatus,education_level,scant_rent,scant_meal,homeOwnership,SESCategory,duration,BMICategory,mentalhealthcategory]

    if st.button('Calculer la probablite d\'un diabète de longue durée '):
        st.write(evidenceDict)
        sesCategoryvalue=sesCaluculator(income,homeOwnership,education_level,scant_meal,scant_rent,employementstatus)
        if sesCategoryvalue !=0:
            evidenceDict['SESCategory']=str(sesCategoryvalue)
        result=calcule_long_duration(calculate_probability(bayesian_model,'durationcategory', evidenceDict))
        st.markdown(result)
        if not patientinstance==None:
            longDurationProba[patientinstance]=[float(result)]

        
        #st.markdown("Valeur sauvegardée avec succès ")
        onto.save(file = "ontologie_probabiliste_modifiee.rdf")

        st.header("Resultat de la comorbidite")
        resultpr=float(result)

        
        col1, col2 = st.columns(2) 
        with col1: 
            progress_bar = st.empty()
            for i in np.linspace(0, resultpr, 33):
                progress_bar.pyplot(plot_progress_circle(i))
                time.sleep(0.00001)
        with col2: 
            st.subheader("   ")
            st.subheader("   ")
            st.subheader("   ")
            if float(result)>0.5:
                st.subheader("Le pourcentage d'un diabète de longue durée est "+str(float(result)*100)+"%")
            else:
                st.subheader("Le pourcentage d'un diabète de longue durée est  "+str(float(result)*100)+"% ")


def scantRent_page():
    
    st.title('Une difficulté à payer les taxes')
    patientslist = list(onto.Patient.instances())
    classPatient=onto["Patient"]
    patientsname=[" "]
    for patienta in patientslist:
        patientsname.append(patienta.name)
        patientinstance=None

    selected_patient = st.selectbox('Liste des patients',patientsname)
    if selected_patient !=" ":
        evidenceDict={}
        income=' '
        homeOwnership=' '
        education_level=' '
        scant_meal=' '
        scant_rent=' '
        employementstatus=' '
        for patient in patientslist:

            if patient.name == selected_patient:    
               
                patientinstance=patient

                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Patient ID**: {patient.name}")
                    if not has_age_group[patient]==[]:
                        st.write(f"**Age Groupe:** {has_age_group[patient][0]}")
                        evidenceDict['ageGroupe']=str(int(has_age_group[patient][0]))
                    if not has_sex[patient]==[]:
                        st.write(f"**Sex:** {has_sex[patient][0]}")
                        evidenceDict['gender']=str(has_sex[patient][0])
                    if not has_ethnicity[patient]==[]:
                        st.write(f"**Ethnicity:** {has_ethnicity[patient][0]}")
                        evidenceDict['ethnicity']=str(has_ethnicity[patient][0])
                    if not has_bmi[patient]==[]:
                        st.write(f"**BMI:** {has_bmi[patient][0]}")
                        if has_bmi[patient][0]=="Normal_weight":
                            evidenceDict['BMICategory']="Snormal_weight"
                        else:
                            evidenceDict['BMICategory']=has_bmi[patient][0]

                        
                    if not do_exercise[patient]==[]:
                        st.write(f"**Exercise:** {do_exercise[patient][0]}")
                        evidenceDict['exercise']=str(do_exercise[patient][0])

                    if not has_mental[patient]==[]:
                        st.write(f"**Mental Health:** {has_mental[patient][0]}")
                        evidenceDict['mentalhealthcategory']=has_mental[patient][0] 

                    if not has_duration[patient]==[]:
                        st.write(f"**Duration of Diabetes:** {has_duration[patient][0]}")   
                        evidenceDict['durationcategory']=has_duration[patient][0]

                with col2:    
                    if not has_income[patient]==[]:
                        income=has_income[patient][0]
                        st.write(f"**Income:** {has_income[patient][0]}")
                        evidenceDict['income']=str(has_income[patient][0])
                    if not has_employ_group[patient]==[]:
                        st.write(f"**Employ Group:** {has_employ_group[patient][0]}")
                        evidenceDict['employementstatus']=str(has_employ_group[patient][0])
                    #if not has_scant_rent[patient]==[]:
                      #  st.write(f"**Scant Rent:** {has_scant_rent[patient][0]}")
                     #   evidenceDict['scantRent']=str(has_scant_rent[patient][0])
                    if not home_own[patient]==[]:
                        homeOwnership=home_own[patient][0]
                        st.write(f"**Home Own:** {home_own[patient][0]}")
                        evidenceDict['homeOwnership']=str(home_own[patient][0])
                    if not has_ses_cate[patient]==[]:
                        st.write(f"**SES Category:** {has_ses_cate[patient][0]}")
                        evidenceDict['SESCategory']=str(has_ses_cate[patient][0])
                    if not has_scant_meal[patient]==[]:
                        scant_meal=has_scant_meal[patient][0]
                        st.write(f"**Scant Meal:** {has_scant_meal[patient][0]}")
                        evidenceDict['scantMeal']=str(has_scant_meal[patient][0])
                    if not has_education[patient]==[]:
                        education_level=has_education[patient][0]
                        st.write(f"**Education:** {has_education[patient][0]}")
                        evidenceDict['educationlevel']=str(has_education[patient][0])
                    #if not has_depression[patient]==[]:
                     #   st.write(f"**Comorbidity :** {has_depression[patient][0]}")
                

    else:
        evidenceDict={}   
        income=' '
        homeOwnership=' '
        education_level=' '
        scant_meal=' '
        scant_rent=' '
        employementstatus=' '

        col1, col2, col3 = st.columns(3)
        with col1:
            ageGroupe = st.selectbox('Groupe d\'âge', [' ',3,4,5,6,7,8,9,10,11,12,13])
            if not ageGroupe ==' ':
                evidenceDict['ageGroupe']=str(ageGroupe)

            gender = st.selectbox('Genre', [' ','Femme', 'Homme'])
        
            

            ethnicity = st.selectbox('Ethnicité', [' ','1', '2', '3', '4' , '5'])
            if not ethnicity ==' ':
                evidenceDict['ethnicity']=str(ethnicity)
        
            exercise = st.selectbox('Exercice', [' ','Oui', 'Non'])
            
            
        
            income = st.selectbox('Revenu', [' ',1,2,3,4,5,6,7,8])
            if not income ==' ':
                evidenceDict['income']=str(income)
            
        with col2:
            #scant_rent = st.selectbox('Location ', [' ','Non', 'Oui'])
            

            scant_meal = st.selectbox('Bon Repas', [' ',1, 2, 3, 4, 5])
            if not scant_meal ==' ':
                evidenceDict['scantMeal']=str(scant_meal)
            

            homeOwnership = st.selectbox('homeOwnership ', [' ',1,2])
            if not homeOwnership ==' ':
                evidenceDict['homeOwnership']=str(homeOwnership)

            employementstatus=st.selectbox('employementstatus', [' ',1,2,3,4,5,6,7,8])
            if not employementstatus ==' ':
                evidenceDict['employementstatus']=str(employementstatus)

            education_level = st.selectbox('Niveau d\'éducation',[' ',1, 2, 3, 4 , 5,6])
            if not education_level ==' ':
                evidenceDict['educationlevel']=str(education_level)

        with col3:    
            #SESCategory = st.selectbox('SESCategory ', [' ',1,2,3])
            #if not SESCategory ==' ':
               # evidenceDict['SESCategory']=str(SESCategory)
            comorbidity = st.selectbox('comorbidity', [' ','Oui', 'Non'])    

            duration = st.selectbox('duration ', [' ','1','2','3','4'])
            if not duration ==' ':
                evidenceDict['durationcategory']=duration
    
            BMICategory =st.selectbox('BMICategory ', [' ','0','1','2','3']) 
            if not BMICategory ==' ':
                evidenceDict['BMICategory']=BMICategory

            mentalhealthcategory =st.selectbox('mentalhealthcategory ', [' ','1','2','3','4','5']) 
            if not mentalhealthcategory ==' ':
                evidenceDict['mentalhealthcategory']=mentalhealthcategory


        #cleaning data
        if gender=='Femme':
            gender='2'
            evidenceDict['gender']=gender
        elif gender=='Homme':
            gender='1'
            evidenceDict['gender']=gender
        if exercise=='Oui':
            exercise='1'
            evidenceDict['exercise']=exercise
        elif exercise=='Non':
            exercise='0'
            evidenceDict['exercise']=exercise
      #  if scant_rent =='Oui':
        #   scant_rent='1'
         #   evidenceDict['scantrent']=scant_rent
        #elif scant_rent=='Non':
          #  scant_rent='2'
          #  evidenceDict['scantrent']=scant_rent

        if scant_meal =='Oui':
            scant_meal='1'
            evidenceDict['scantMeal']=scant_meal
        elif scant_meal=='Non':
            scant_meal='2'  
            evidenceDict['scantMeal']=scant_meal

        if comorbidity=='Oui':
            comorbidity='1'
            evidenceDict['comorbidity']=comorbidity
        elif comorbidity=='Non':
            comorbidity='2'
            evidenceDict['comorbidity']=comorbidity    

    #listentry=[ageGroupe,gender,ethnicity,exercise,income,employementstatus,education_level,scant_rent,scant_meal,homeOwnership,SESCategory,duration,BMICategory,mentalhealthcategory]

    if st.button('Calculer la probablite d\'une difficulté à payer les taxes '):
        
        sesCategoryvalue=sesCaluculator(income,homeOwnership,education_level,scant_meal,scant_rent,employementstatus)
        if sesCategoryvalue !=0:
            evidenceDict['SESCategory']=str(sesCategoryvalue)
        st.write(evidenceDict)    
        result=calcule_scant_rent(calculate_probability(bayesian_model,'scantrent', evidenceDict))
        st.markdown(result)
        if not patientinstance==None:
            scantRentProba[patientinstance]=[float(result)]
        
        #st.markdown("Valeur sauvegardée avec succès ")
        onto.save(file = "ontologie_probabiliste_modifiee.rdf")
        st.header("Resultat de la probablite")
        resultpr=float(result)

        
        col1, col2 = st.columns(2) 
        with col1: 
            progress_bar = st.empty()
            for i in np.linspace(0, resultpr, 33):
                progress_bar.pyplot(plot_progress_circle(i))
                time.sleep(0.00001)
        with col2: 
            st.subheader("   ")
            st.subheader("   ")
            st.subheader("   ")
            if float(result)>0.5:
                st.subheader("Le pourcentage d'une difficulté à payer les taxes "+str(float(result)*100)+"%")
            else:
                st.subheader("Le pourcentage d'une difficulté à payer les taxes  "+str(float(result)*100)+"% ")

def scantMeal_page():
    
    st.title('Une difficulté à payer le repas')
    patientslist = list(onto.Patient.instances())
    classPatient=onto["Patient"]
    patientsname=[" "]
    for patienta in patientslist:
        patientsname.append(patienta.name)
        patientinstance=None

    selected_patient = st.selectbox('Liste des patients',patientsname)
    if selected_patient !=" ":
        evidenceDict={}
        income=' '
        homeOwnership=' '
        education_level=' '
        scant_meal=' '
        scant_rent=' '
        employementstatus=' '  
        for patient in patientslist:

            if patient.name == selected_patient:    
               
                patientinstance=patient

                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Patient ID**: {patient.name}")
                    if not has_age_group[patient]==[]:
                        st.write(f"**Age Groupe:** {has_age_group[patient][0]}")
                        evidenceDict['ageGroupe']=str(int(has_age_group[patient][0]))
                    if not has_sex[patient]==[]:
                        st.write(f"**Sex:** {has_sex[patient][0]}")
                        evidenceDict['gender']=str(has_sex[patient][0])
                    if not has_ethnicity[patient]==[]:
                        st.write(f"**Ethnicity:** {has_ethnicity[patient][0]}")
                        evidenceDict['ethnicity']=str(has_ethnicity[patient][0])
                    if not has_bmi[patient]==[]:
                        st.write(f"**BMI:** {has_bmi[patient][0]}")
                        if has_bmi[patient][0]=="Normal_weight":
                            evidenceDict['BMICategory']="Snormal_weight"
                        else:
                            evidenceDict['BMICategory']=has_bmi[patient][0]

                        
                    if not do_exercise[patient]==[]:
                        st.write(f"**Exercise:** {do_exercise[patient][0]}")
                        evidenceDict['exercise']=str(do_exercise[patient][0])
                        
                    if not has_mental[patient]==[]:
                        st.write(f"**Mental Health:** {has_mental[patient][0]}")
                        evidenceDict['mentalhealthcategory']=has_mental[patient][0] 

                    if not has_duration[patient]==[]:
                        st.write(f"**Duration of Diabetes:** {has_duration[patient][0]}")   
                        evidenceDict['durationcategory']=has_duration[patient][0]

                with col2:    
                    if not has_income[patient]==[]:
                        income=has_income[patient][0]
                        st.write(f"**Income:** {has_income[patient][0]}")
                        evidenceDict['income']=str(has_income[patient][0])
                    if not has_employ_group[patient]==[]:
                        st.write(f"**Employ Group:** {has_employ_group[patient][0]}")
                        evidenceDict['employementstatus']=str(has_employ_group[patient][0])
                    if not has_scant_rent[patient]==[]:
                        scant_rent=has_scant_rent[patient][0]
                        st.write(f"**Scant Rent:** {has_scant_rent[patient][0]}")
                        evidenceDict['scantrent']=str(has_scant_rent[patient][0])
                    if not home_own[patient]==[]:
                        homeOwnership=home_own[patient][0]
                        st.write(f"**Home Own:** {home_own[patient][0]}")
                        evidenceDict['homeOwnership']=str(home_own[patient][0])
                    if not has_ses_cate[patient]==[]:
                        st.write(f"**SES Category:** {has_ses_cate[patient][0]}")
                        evidenceDict['SESCategory']=str(has_ses_cate[patient][0])
                    #if not has_scant_meal[patient]==[]:
                       # st.write(f"**Scant Meal:** {has_scant_meal[patient][0]}")
                      #  evidenceDict['scantMeal']=str(has_scant_meal[patient][0])
                    if not has_education[patient]==[]:
                        education_level=has_education[patient][0]
                        st.write(f"**Education:** {has_education[patient][0]}")
                        evidenceDict['educationlevel']=str(has_education[patient][0])
                    #if not has_depression[patient]==[]:
                     #   st.write(f"**Comorbidity :** {has_depression[patient][0]}")
                

    else:
        evidenceDict={}   
        income=' '
        homeOwnership=' '
        education_level=' '
        scant_meal=' '
        scant_rent=' '
        employementstatus=' '

        col1, col2, col3 = st.columns(3)
        with col1:
            ageGroupe = st.selectbox('Groupe d\'âge', [' ',3,4,5,6,7,8,9,10,11,12,13])
            if not ageGroupe ==' ':
                evidenceDict['ageGroupe']=str(ageGroupe)

            gender = st.selectbox('Genre', [' ','Femme', 'Homme'])
        
            

            ethnicity = st.selectbox('Ethnicité', [' ','1', '2', '3', '4' , '5'])
            if not ethnicity ==' ':
                evidenceDict['ethnicity']=str(ethnicity)
        
            exercise = st.selectbox('Exercice', [' ','Oui', 'Non'])
            
        
            income = st.selectbox('Revenu', [' ',1,2,3,4,5,6,7,8])
            if not income ==' ':
                evidenceDict['income']=str(income)
            
        with col2:
            scant_rent = st.selectbox('Location ', [' ',1, 2, 3, 4, 5])
            if not scant_rent ==' ':
                evidenceDict['scantrent']=str(scant_rent)
            

            #scant_meal = st.selectbox('Bon Repas', [' ','Non', 'Oui'])
            

            homeOwnership = st.selectbox('homeOwnership ', [' ',1,2])
            if not homeOwnership ==' ':
                evidenceDict['homeOwnership']=str(homeOwnership)

            employementstatus=st.selectbox('employementstatus', [' ',1,2,3,4,5,6,7,8])
            if not employementstatus ==' ':
                evidenceDict['employementstatus']=str(employementstatus)

            education_level = st.selectbox('Niveau d\'éducation',[' ',1, 2, 3, 4 , 5,6])
            if not education_level ==' ':
                evidenceDict['educationlevel']=str(education_level)
            mentalhealthcategory =st.selectbox('mentalhealthcategory ', [' ','1','2','3','4','5']) 
            if not mentalhealthcategory ==' ':
                evidenceDict['mentalhealthcategory']=mentalhealthcategory
    

        with col3:    
            SESCategory = st.selectbox('SESCategory ', [' ',1,2,3])
            if not SESCategory ==' ':
                evidenceDict['SESCategory']=str(SESCategory)
            comorbidity = st.selectbox('comorbidity', [' ','Oui', 'Non'])    

            duration = st.selectbox('duration ', [' ','1','2','3','4'])
            if not duration ==' ':
                evidenceDict['durationcategory']=duration
    
            BMICategory =st.selectbox('BMICategory ', [' ','0','1','2','3']) 
            if not BMICategory ==' ':
                evidenceDict['BMICategory']=BMICategory

            


        #cleaning data
        if gender=='Femme':
            gender='2'
            evidenceDict['gender']=gender
        elif gender=='Homme':
            gender='1'
            evidenceDict['gender']=gender
        if exercise=='Oui':
            exercise='1'
            evidenceDict['exercise']=exercise
        elif exercise=='Non':
            exercise='0'
            evidenceDict['exercise']=exercise
        if scant_rent =='Oui':
           scant_rent='1'
           evidenceDict['scantrent']=scant_rent
        elif scant_rent=='Non':
            scant_rent='2'
            evidenceDict['scantrent']=scant_rent

        #if scant_meal =='Oui':
          #  scant_meal='1'
          #  evidenceDict['scantMeal']=scant_meal
      #  elif scant_meal=='Non':
          #  scant_meal='2'  
          #  evidenceDict['scantMeal']=scant_meal

        if comorbidity=='Oui':
            comorbidity='1'
            evidenceDict['comorbidity']=comorbidity
        elif comorbidity=='Non':
            comorbidity='2'
            evidenceDict['comorbidity']=comorbidity    

    #listentry=[ageGroupe,gender,ethnicity,exercise,income,employementstatus,education_level,scant_rent,scant_meal,homeOwnership,SESCategory,duration,BMICategory,mentalhealthcategory]

    if st.button('Calculer la probablite d\'une difficulté à payer le repas '):
        #st.write(evidenceDict)
        sesCategoryvalue=sesCaluculator(income,homeOwnership,education_level,scant_meal,scant_rent,employementstatus)
        if sesCategoryvalue !=0:
            evidenceDict['SESCategory']=str(sesCategoryvalue)
        result=calcule_scant_rent(calculate_probability(bayesian_model,'scantMeal', evidenceDict))
        st.markdown(result)
        if not patientinstance==None:
            scantMeaProba[patientinstance]=[float(result)]
        
        #st.markdown("Valeur sauvegardée avec succès ")
        onto.save(file = "ontologie_probabiliste_modifiee.rdf")

        st.header("Resultat de la probablite")
        resultpr=float(result)

        
        col1, col2 = st.columns(2) 
        with col1: 
            progress_bar = st.empty()
            for i in np.linspace(0, resultpr, 33):
                progress_bar.pyplot(plot_progress_circle(i))
                time.sleep(0.00001)
        with col2: 
            st.subheader("   ")
            st.subheader("   ")
            st.subheader("   ")
            if float(result)>0.5:
                st.subheader("Le pourcentage d\'une difficulté à payer le repas est "+str(float(result)*100)+"%")
            else:
                st.subheader("Le pourcentage d\'une difficulté à payer le repas est  "+str(float(result)*100)+"% ")



#page liste des patients
def patients_page():
    
    st.title('Liste des patients')
    patientslist = list(onto.Patient.instances())
    classPatient=onto["Patient"]
    
    
    patientsname=[]
    for patienta in patientslist:
        patientsname.append(patienta.name)

    selected_patient = st.selectbox('Liste des patients',patientsname)
    for patient in patientslist:
        if patient.name == selected_patient:    
            col1, col2 ,col3 = st.columns(3)
            with col1:
                st.write(f"**Patient ID**: {patient.name}")
                if not has_age_group[patient]==[]:
                    st.write(f"**Age Groupe:** {has_age_group[patient][0]}")
                if not has_sex[patient]==[]:
                    st.write(f"**Sex:** {has_sex[patient][0]}")
                if not has_ethnicity[patient]==[]:
                    st.write(f"**Ethnicity:** {has_ethnicity[patient][0]}")
                if not has_bmi[patient]==[]:
                    st.write(f"**BMI:** {has_bmi[patient][0]}")
                if not do_exercise[patient]==[]:
                    st.write(f"**Exercise:** {do_exercise[patient][0]}")
                if not has_mental[patient]==[]:
                    st.write(f"**Mental Health:** {has_mental[patient][0]}")       
                if not has_age_group[patient]==[]:
                    st.write(f"**Age Group:** {has_age_group[patient][0]}")
                if not has_duration[patient]==[]:
                    st.write(f"**Duration of Diabetes:** {has_duration[patient][0]}")   
            with col2:    
                if not has_income[patient]==[]:
                    st.write(f"**Income:** {has_income[patient][0]}")

                if not has_employ_group[patient]==[]:
                    st.write(f"**Employ Group:** {has_employ_group[patient][0]}")
                if not has_scant_rent[patient]==[]:
                    st.write(f"**Scant Rent:** {has_scant_rent[patient][0]}")
                if not home_own[patient]==[]:
                    st.write(f"**Home Own:** {home_own[patient][0]}")
                if not has_ses_cate[patient]==[]:
                    st.write(f"**SES Category:** {has_ses_cate[patient][0]}")
                if not has_scant_meal[patient]==[]:
                    st.write(f"**Scant Meal:** {has_scant_meal[patient][0]}")
                if not has_education[patient]==[]:
                    st.write(f"**Education:** {has_education[patient][0]}")
                if not has_depression[patient]==[]:
                    st.write(f"**Comorbidity :** {has_depression[patient][0]}")
            with col3:        
                st.write("**Les propriétés probabilistes**")
                if not depressionProba[patient]==[] :
                    st.write(f"**Probabilité de Dépression :** {depressionProba[patient][0]}")
                    
                if not obeseProba[patient]==[] :
                    st.write(f"**Probabilité de l'obésité :** {obeseProba[patient][0]}")
                
                if not exercisePoroba[patient]==[] :
                    st.write(f"**Probabilité de l'exercise sportif :** {exercisePoroba[patient][0]}")
                if not shortDurationProba[patient]==[] :
                    st.write(f"**probabilité d’un diabète de courte durée :** {shortDurationProba[patient][0]}")
                if not mediumDurationProba[patient]==[] :
                    st.write(f"**probabilité d’un diabète de moyenne durée :** {mediumDurationProba[patient][0]}")  
                if not longDurationProba[patient]==[] :
                    st.write(f"**probabilité d’un diabète de longue durée :** {longDurationProba[patient][0]}") 
                if not scantRentProba[patient]==[] :
                    st.write(f"**probabilité ’une difficulté à payer le repas :** {scantRentProba[patient][0]}") 
                if not scantMeaProba[patient]==[] :
                    st.write(f"**probabilité d’une difficulté à payer les taxes :** {scantMeaProba[patient][0]}")         
                                 

    





def main():
    pageswitch="add" 
    st.markdown(page_bg_img, unsafe_allow_html=True)

    
    st.sidebar.title("Sidebar")
 

    
    

    #Navigation principale
    main_page = st.sidebar.radio("Choisir une page", ("Accueil","Ajouter un patient", "Liste des patients", "Calcul des Inferences",))
    calcul_page = st.sidebar.selectbox("Calcul des probabilités",("Comorbidite", "obesite", "exercise","Un diabète de courte durée","Un diabète de moyenne durée","Un diabète de longue durée","Une difficulté à payer le repas","Une difficulté à payer les taxes"))

    # Affichage des pages en fonction de la sélection
    if main_page == "Ajouter un patient":
        addPatient_page()
    elif main_page == "Liste des patients":
        patients_page()
    elif main_page =="Accueil":
        accueil()    
    
    elif main_page == "Calcul des Inferences":


        # Affichage des pages de calcul en fonction de la sélection
        if calcul_page == "Comorbidite":
            comorbidity_page()
        elif calcul_page == "obesite":
            obesity_page()
        elif calcul_page == "exercise":
            exercise_final_page()
        elif calcul_page == "Un diabète de courte durée":
            shortDuration_page()
        elif calcul_page == "Un diabète de longue durée":
            longDuration_page()    
        elif calcul_page=="Une difficulté à payer le repas":
            scantMeal_page()
        elif calcul_page=="Une difficulté à payer les taxes":
            scantRent_page()  
        elif calcul_page=="Un diabète de moyenne durée":
            moyenDuration_page()    



if __name__ == "__main__":
    
    main()
