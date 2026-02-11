import streamlit as st
from owlready2 import *
import time


def sesCaluculator(income,homeOwnership,education_level,scant_meal,scant_rent,employementstatus):
    min=0
    max=0
    sesvalue=0
    if income==' ':
        income=0
    else:
        sesvalue=sesvalue+income
        min=min+1
        max=max+8  
    if homeOwnership==' ':
        homeOwnership=0
    else:
        sesvalue=sesvalue+1/homeOwnership
        min=min+1/2
        max=max+1
    if education_level==' ':
        education_level=0
    else:
        sesvalue=sesvalue+education_level
        min=min+1
        max=max+6

    if scant_meal==' ':
        scant_meal=0
    else:
        sesvalue=sesvalue+scant_meal
        min=min+1
        max=max+5
    if scant_rent==' ':
        scant_rent=0   
    else:
        sesvalue=sesvalue+scant_rent
        min=min+1
        max=max+5
    if employementstatus==' ':
        employementstatus=0   
    else:
        sesvalue=sesvalue+1/employementstatus
        min=min+1/8
        max=max+1

    
    #sesvalue=income+(1/(homeOwnership+epsilon))+education_level+scant_meal+scant_rent+(1/(employementstatus+epsilon))
    intervale=max-min
    if sesvalue<0.25*intervale+min and sesvalue !=0:
        return 1
    if sesvalue<0.53*intervale+min and sesvalue>=0.25*intervale+min and sesvalue !=0:
        return 2
    if sesvalue>=0.53*intervale+min and sesvalue !=0:
        return 3
    else:
        return 0


def add_patient(nom,listentry):
    #loading ontology
    onto = get_ontology("ontologie_probabiliste_modifiee.rdf").load()
    classPatient=onto["Patient"]
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


    patient=classPatient(nom)
    if not listentry[0]==' ':
        has_age_group[patient]=[listentry[0]]

    if not listentry[1]==' ':
        has_sex[patient]=[listentry[1]]

    if not listentry[2]==' ':
        has_ethnicity[patient]=[listentry[2]]

    if not listentry[3]==' ':
        do_exercise[patient]=[listentry[3]]

    if not listentry[4]==' ':
        has_income[patient]=[listentry[4]]

    if not listentry[5]==' ':
        has_employ_group[patient]=[listentry[5]]

    if not listentry[6]==' ':
        has_education[patient]=[listentry[6]]

    if not listentry[7]==' ':
        has_scant_rent[patient]=[listentry[7]]

    if not listentry[8]==' ':
        has_scant_meal[patient]=[listentry[8]]

    if not listentry[9]==' ':
        home_own[patient]=[listentry[9]]    

    if not listentry[10]==' ':
        if listentry[10] !=0:
            has_ses_cate[patient]=[listentry[10]]    

    if not listentry[11]==' ':
        has_duration[patient]=[listentry[11]]   

    if not listentry[12]==' ':
        has_bmi[patient]=[listentry[12]]      

    if not listentry[13]==' ':
        has_mental[patient]=[listentry[13]]        

    if not listentry[14]==' ':
        has_depression[patient]=[listentry[14]]           
    has_diabete[patient]=[1]
    onto.save(file = "ontologie_probabiliste_modifiee.rdf")



            


def addPatient_page():
    st.title('Ajouter Patient')
    

    name_input = st.text_input("Nom du Patient")

    col1, col2, col3 = st.columns(3)
    with col1:
        ageGroupe = st.selectbox('Groupe d\'âge', [' ',3,4,5,6,7,8,9,10,11,12,13])
        gender = st.selectbox('Genre', [' ','Femme', 'Homme'])
        
            

        ethnicity = st.selectbox('Ethnicité', [' ',1, 2, 3, 4, 5])
        
        exercise = st.selectbox('Exercice', [' ','Oui', 'Non'])
        
        income = st.selectbox('Revenu', [' ',1,2,3,4,5,6,7,8])
            
    with col2:
        scant_rent = st.selectbox('Location ', [' ',1, 2, 3, 4, 5])
        scant_meal = st.selectbox('Bon Repas',[' ',1, 2, 3, 4, 5])
        homeOwnership = st.selectbox('homeOwnership ', [' ',1,2])
        employementstatus=st.selectbox('employementstatus', [' ',1,2,3,4,5,6,7,8])

        education_level = st.selectbox('Niveau d\'éducation',[' ',1, 2, 3, 4,5,6])
    
    with col3:    
        #SESCategory = st.selectbox('SESCategory ', [' ',1,2,3])
        SESCategory=sesCaluculator(income,homeOwnership,education_level,scant_meal,scant_rent,employementstatus)

        duration = st.selectbox('duration ', [' ','1','2','3','4'])

        BMICategory =st.selectbox('BMICategory ', [' ','0','1','2','3']) 

        mentalhealthcategory =st.selectbox('mentalhealthcategory ', [' ','1','2','3','4','5']) 

        comorbidity =st.selectbox('Comorbidity ', [' ','Non','Oui']) 
        
    SESCategory=1
    #cleaning data
    if gender=='Femme':
        gender=2
    elif gender =='Homme':
        gender=1

    if exercise=='Oui':
        exercise=1
    elif exercise=='Non':
        exercise=0

    if scant_rent =='Oui':
        scant_rent=1
        
    elif scant_rent=='Non':
        scant_rent=2


    if scant_meal =='Oui':
        scant_meal=1
    elif scant_meal=='Non':
        scant_meal=2

    if comorbidity =='Oui':
        comorbidity=1
    elif comorbidity=='Non':
        comorbidity=2
    

    listentry=[ageGroupe,gender,ethnicity,exercise,income,employementstatus,education_level,scant_rent,scant_meal,homeOwnership,SESCategory,duration,BMICategory,mentalhealthcategory,comorbidity]

    if st.button('Ajouter Patient'):
        add_patient(name_input,listentry)
        st.markdown("patient ajoutee avec success !")
    
