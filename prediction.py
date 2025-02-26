import funcHelper
import streamlit as st
import numpy as np # type: ignore
from numpy import ndarray
import pandas as pd # type: ignore
from pandas import DataFrame
import seaborn as sns # type: ignore
from sklearn.model_selection import train_test_split # type: ignore
from sklearn.linear_model import LogisticRegression # type: ignore
from sklearn.preprocessing import StandardScaler # type: ignore
from sklearn.neighbors import KNeighborsClassifier # type: ignore
from sklearn.neural_network import MLPClassifier # type: ignore
from sklearn.model_selection import GridSearchCV, RepeatedStratifiedKFold #type: ignore 
from sklearn.svm import SVC # type: ignore
from sklearn.decomposition import PCA # type: ignore
from pycaret.classification import setup, compare_models, pull, predict_model, get_config # type: ignore
from sklearn.metrics import confusion_matrix, accuracy_score, mean_squared_error, precision_score, recall_score #type:ignore
from xgboost import XGBClassifier, plot_importance
from catboost import CatBoostClassifier # type: ignore
from sklearn.pipeline import Pipeline # type: ignore
from sklearn.compose import ColumnTransformer # type: ignore
from sklearn.preprocessing import OneHotEncoder # type: ignore
from sklearn.impute import SimpleImputer # type: ignore
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.tree import DecisionTreeClassifier
import matplotlib.pyplot as plt # type: ignore
plt.rcParams.update({'font.family': 'Tahoma'})
plt.rcParams.update({'font.size': 10})
plt.rcParams.update({'axes.titlesize': 10})
plt.rcParams.update({'axes.labelsize': 10})
plt.rcParams.update({'xtick.labelsize': 5})
plt.rcParams.update({'ytick.labelsize': 5})
plt.rcParams.update({'figure.titlesize': 14})

if 'df' not in st.session_state:
    st.session_state.df = None

if 'df_2025' not in st.session_state:
    st.session_state.df_2025 = None

if 'train_size' not in st.session_state:
    st.session_state.train_size = 0.75

if 'best_model' not in st.session_state:
    st.session_state.best_model = None

#####################################################################################################
# helper methods
#####################################################################################################
# write a model parameter in a dictinary
def getParams(modelcall : str) -> dict:
    result = dict()
    try:
        modelcall = modelcall.strip()
        strings = modelcall[modelcall.index('(') + 1:].split(',')
        for item in strings:
            key_value_pair = item.strip().split('=')
            if len(key_value_pair) == 2:
                result[key_value_pair[0]] = key_value_pair[1]

    except Exception as e:
        print(str(e))

    return result

# load dataset witch contains all data from 1960- 2024    
def load_dataset() -> DataFrame: 
   
    df_2025 = pd.read_csv(f"Datasets/movies_data_2025.csv", delimiter=',') # relative path from folder of the executed main.py
    df_2025.drop('Unnamed: 0', axis=1, inplace=True)
    st.session_state.df_2025 = df_2025

    df = pd.read_csv(f"Datasets/movies_data.csv", delimiter=',') # relative path from folder of the executed main.py
    df.drop('Unnamed: 0', axis=1, inplace=True)
    st.session_state.train_size = 0.75
    st.session_state.df = df
    return df

# let the user decide, what he wants to predict
def set_outcome_to_predict(categories: list[str]):

    st.sidebar.header('What should be predicted')
    option = st.sidebar.radio("Select model outcome:", categories)
    return option

# process user option
def get_selected_outcome(option, categories: list[str])-> DataFrame:

    if option == categories[0]:
        return st.session_state.df['oscars'].apply(funcHelper.handle_oscar_nominations)
    elif option == categories[1]:
        return st.session_state.df['nominations'].apply(funcHelper.handle_award_nominations)
    else:
        return st.session_state.df['wins'].apply(funcHelper.handle_award_winners)

# let the user decide, which predection mode should we use   
def set_prediction_mode(mode: list[str]):

    st.sidebar.header('In which mode schould be predicted')
    option = st.sidebar.radio("Select prediction mode:", mode, index=1)
    return option

# plots data for machine learning analyse 
def plot_analyse_data():
    '''
    plots data for machine learning analyse
    '''
    container = st.container()
    container.header('Feature plots:', divider='gray')

    fig_01, ax = plt.subplots(1,3, figsize=(18,3)) 
    sns.histplot(data=st.session_state.df, x='oscars', hue='outcome', bins=33, ax=ax[0])
    sns.histplot(data=st.session_state.df, x='Rating', hue='outcome', bins=33, ax=ax[1])
    sns.histplot(data=st.session_state.df, x='Votes',  hue='outcome', bins=33, ax=ax[2])
    container.pyplot(fig_01, use_container_width=True)

    fig_02, ax = plt.subplots(1,2, figsize=(18,3)) 
    sns.scatterplot(data=st.session_state.df, x='Rating', y='Votes', hue='outcome', ax=ax[0], palette="deep", marker='.')
    sns.histplot(data=st.session_state.df.sort_values('genres_count', axis=0, ascending=True), x='genres', hue='outcome', ax=ax[1])
    container.pyplot(fig_02, use_container_width=True)
    
# data predication (automatic with pycareT library or manually  depending on selected ML model) 
def handle_prediction_mode(option, mode: list[str], data: np.array, col_names:list[str], y: DataFrame):
    
    print(st.session_state.train_size)
    if st.session_state.train_size:
        container = st.container()
               
        if option == mode[0]:
            # seach for the best 3 models
            model = setup(data=data, target=y, session_id=33, train_size=st.session_state.train_size)
            best_model = compare_models(n_select=3)
            protocol = pull()

            st.sidebar.write('Info from automatic best model search')
            st.session_state.best_model = best_model
            st.sidebar.write(protocol)
            ####################################################################################################
            # get data from best modell found
            ####################################################################################################
            y_pred = predict_model(best_model[0], get_config('X_test'))
            X_train, X_test = get_config('X_train'), get_config('X_test')
            y_train, y_test = get_config('y_train'), get_config('y_test')
    
            st.sidebar.write(f'best parameters: {getParams(str(best_model[0]))}')

            ####################################################################################################
            # plot predictaion data
            ####################################################################################################        
            container.header('Prediction plots:', divider='gray')
            
            fig, ax = plt.subplots(1, 3, figsize=(18,3))
            sns.scatterplot(data=X_test, marker='.',
                            x = col_names[0], 
                            y = col_names[1], 
                            hue=y_pred['prediction_label'], ax=ax[0])
            plt.sca(ax[0])
            plt.title('data prediction on PCA (n_components = 2)')
            
            c = confusion_matrix(y_test, y_pred['prediction_label'])
            s=sns.heatmap(c/np.sum(c,axis=1), annot=True,cbar = True,fmt=".2%", cmap='summer', ax=ax[1])
            s.set_xlabel("predicted label")
            s.set_ylabel("real label")
            s.set_title("confusion matrix")
            
            sns.scatterplot(data=X_test, marker='.',
                            x = col_names[0], 
                            y = col_names[1], 
                            hue=y_pred['prediction_label'], ax=ax[2])
            h=0.2
            x_min, x_max = X_test.iloc[:, 0].min() - 1, X_test.iloc[:, 0].max() + 1
            y_min, y_max = X_test.iloc[:, 1].min() - 1, X_test.iloc[:, 1].max() + 1

            xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
            prediction = predict_model(best_model[0], pd.DataFrame(data=np.c_[xx.ravel(), yy.ravel()], columns=col_names))
            Z = np.array(prediction['prediction_label']).reshape(xx.shape)
            
            plt.sca(ax[2])
            plt.title('data prediction with spatial separation')
            plt.contourf(xx, yy, Z, alpha=0.4, cmap='tab10')
            container.pyplot(fig, use_container_width=True)
            
        else:
            model_names = ['', 'KNN', 'SVC', 'MLP', 'LogisticRegression', 'CatBoost-Classifier','DecisionTree-Classifier']
            models = [None, KNeighborsClassifier(), SVC(), MLPClassifier(), LogisticRegression(), CatBoostClassifier(), DecisionTreeClassifier()] 
            X_train, X_test, y_train, y_test = train_test_split(data, y, train_size=st.session_state.train_size, random_state=33)
            selectBoxOption = st.sidebar.selectbox('Select classifier model', options=model_names)

            if selectBoxOption != '':
                params = getParameters(selectBoxOption)
                model = models[model_names.index(selectBoxOption)]
                print(f'******************************************')
                print(f'model {str(model)} is running ')
                print(f'******************************************')

                ####################################################################################################
                # using gridSearch for hyperparameter tuning with cross-value-validation
                ####################################################################################################
                cv = RepeatedStratifiedKFold(n_splits = 2, n_repeats = 2, random_state=0)
                grid = GridSearchCV(model, params, cv=cv, n_jobs=5)
                
                grid.fit(X_train, y_train)
                y_pred = grid.predict(X_test)

                ####################################################################################################
                # show accuracy, precision, recall and mse
                ####################################################################################################
                contr = st.sidebar.container()
                c1, c2, c3, c4 = contr.columns(4)
                c1.write("accuracy") 
                c2.write(f"precision") 
                c3.write(f"recall")       
                c4.write(f"mse")    
                c1.write(f" {accuracy_score(y_test, y_pred):.3f}")   
                c2.write(f"{precision_score(y_test, y_pred):.3f}") 
                c3.write(f"{recall_score(y_test, y_pred):.3f}")       
                c4.write(f"{mean_squared_error(y_test, y_pred):.3f}")    

                st.sidebar.write(f'best parameters: {grid.best_params_}') 
                
                ####################################################################################################
                # plot predictaion data
                #################################################################################################### 
                container.header('Prediction plots:', divider='gray')         
                
                fig, ax = plt.subplots(1, 3, figsize=(18,3))
                sns.scatterplot(data=pd.DataFrame(X_test, columns=col_names), 
                                x = col_names[0], marker='.',
                                y = col_names[1], 
                                hue=y_pred, ax=ax[0])
                plt.sca(ax[0])
                plt.title('data prediction on PCA (n_components = 2)')
    
                c = confusion_matrix(y_test, y_pred)
                s=sns.heatmap(c/np.sum(c,axis=1), annot=True,cbar = True,fmt=".2%", cmap='summer', ax=ax[1])
                s.set_xlabel("predicted label")
                s.set_ylabel("real label")
                s.set_title("confusion matrix")
                
                sns.scatterplot(data=pd.DataFrame(X_test, columns=col_names), 
                                x = col_names[0], marker='.',
                                y = col_names[1], 
                                hue=y_pred, ax=ax[2])
                h=0.2
                x_min, x_max = X_test[:, 0].min() - 1, X_test[:, 0].max() + 1
                y_min, y_max = X_test[:, 1].min() - 1, X_test[:, 1].max() + 1

                xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
                prediction = grid.predict(np.c_[xx.ravel(), yy.ravel()])
                Z = prediction.reshape(xx.shape)

                plt.sca(ax[2])
                plt.title('data prediction with spatial separation')
                plt.contourf(xx, yy, Z, alpha=0.4, cmap='tab10')
                container.pyplot(fig, use_container_width=True)

# get hyperparameter for manually ML models tuning
def getParameters(classifier_name: str):
    params = dict()
    if classifier_name == "KNN": 
        params= {'n_neighbors': list(range(1, 33)),
                'weights': ['uniform', 'distance'],
                'metric' : ['minkowski','euclidean','manhattan']             
                }    
    elif classifier_name == 'MLP':
        params = {
        'hidden_layer_sizes': [(25, 25, 25, 25, 25), (35,35,35, 35),(45,45,45), (55,55), (65,)],
        'activation': ['relu'],
        'solver': ['adam'],
        'alpha': [0.05],
        'learning_rate': ['adaptive']
        }
    elif classifier_name == "SVC":
        params = {"C":[899, 987, 1033],
            "gamma":  [0.0001],
            "kernel": ['rbf']
        }
    elif classifier_name == "LogisticRegression": 
        params = {
            'penalty': ['l1', 'l2', 'elasticnet'],
            'tol': [0.00001, 0.0001, 0.001 ],
            'C': [0.01, 0.1, 0, 1, 10, 100], 
            'solver': ['lbfgs', 'liblinear', 'newton-cg', 'newton-cholesky', 'sag', 'saga'],
            'max_iter': [1, 10, 100, 300],
            }
    elif classifier_name =='CatBoost-Classifier':
        params = {
            "iterations": [99],
            "learning_rate": [0.01, 0.1],
            "depth": [5, 10],
            "subsample": [1.0],
            "colsample_bylevel": [1.0],
            "min_data_in_leaf": [1, 100],
        }
    else:             # DecisionTree-Classifier
        params = {
            "criterion": ['gini', 'entropy', 'log_loss'],
            "splitter": ['best', 'random'],
            "max_depth": [7, 13, 33, 99],
            "max_features": ['sqrt', 'log2'],
        }

    return params

# predict movies for 2015
def predict_movies_data_2025(num_attr: list[str], cat_attr: list[str]):

    if st.session_state.best_model:

        st.header('predication for oscar nominations 2025', divider='gray')
        container = st.container(height=199)

        df_predict = st.session_state.df_2025
        pca = PCA(n_components = 2, svd_solver='arpack', random_state=33)

        prediction_data = df_predict.loc[:, [
            'Rating', 'Votes', 'grossWorldWide', 'gross_US_Canada', 'opening_weekend_Gross', 
            'budget', 'Duration', 'Year', 
            'stars', 'genres']]
        prediction_data_pipeline = get_pipeline(num_attr, cat_attr).fit_transform(prediction_data)
        prediction_data_pca = pca.fit_transform(prediction_data_pipeline)
        
        predications = st.session_state.best_model[0].predict(prediction_data_pca)
        df_predict['outcome'] = predications
        df_predict = df_predict[ df_predict['outcome'] >0]
        df_predict.drop(['stars', 'genres'], axis=1, inplace=True)

        df_predict = df_predict.drop_duplicates()
        df_predict = df_predict.reset_index(drop=True)
        container.dataframe(
            DataFrame(data=df_predict, columns=df_predict.columns).sort_values(by=['Title', 'Rating', 'Votes', 'oscars']), 
            use_container_width=True, )

# get defined pipeline for data cleaning
def get_pipeline(num_attr: list[str], cat_attr: list[str]) -> ColumnTransformer:
    num_pipeline = Pipeline([
        ("NAN", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())])
    full_pipeline = ColumnTransformer([
        ("num", num_pipeline, num_attr),
        ("cat", OneHotEncoder(), cat_attr)
    ])
    
    return full_pipeline

#####################################################################################################
# main page
#####################################################################################################
if st.session_state.df is None:
    load_dataset()

def startProcess():
    df = load_dataset()

    container = st.container(height=199)
    container.write("Predict whether a movie has the potential to win an Oscar!")
    container.dataframe(data=df, use_container_width=True, hide_index=True)

    categories = ["oscar nominations", 'award nomations', 'award winners']
    outcome_option = set_outcome_to_predict(categories=categories)
    st.session_state.df['outcome'] = get_selected_outcome(option=outcome_option, categories=categories)
    #####################################################################################################
    # lösche nicht verwendete Spalten 
    #####################################################################################################
    num_attr = ['Rating', 'Votes', 'grossWorldWide', 'gross_US_Canada', 'opening_weekend_Gross', 
                'budget', 'Duration', 'Year']
    cat_attr = ['stars', 'genres']

    data = st.session_state.df.loc[:, [
        'Rating', 'Votes', 'grossWorldWide', 'gross_US_Canada', 'opening_weekend_Gross', 
        'budget', 'Duration', 'Year', 
        'stars', 'genres']]
    y = st.session_state.df['outcome']

    #####################################################################################################
    # use pipeline for preparing data (standard scaler, OnhotEncoder, ...)
    #####################################################################################################
    data_pipeline = get_pipeline(num_attr, cat_attr).fit_transform(data)
    
    #####################################################################################################
    # Use PCA inorder to reduce features to 2 components (feature_1, feature2)
    #####################################################################################################
    pca = PCA(n_components = 2, svd_solver='arpack', random_state=33)
    data_pca = pca.fit_transform(data_pipeline)
    pca_col_names = ['feature_1', 'feature_2']
    
    #####################################################################################################
    # analyzing some plots for existing features and outcome before predication 
    #####################################################################################################
    plot_analyse_data()
    
    #####################################################################################################
    # set prediction modus: automatic or manuell
    #####################################################################################################
    mode = ["automatic", 'manual']
    prediction_option = set_prediction_mode(mode=mode)
    handle_prediction_mode(prediction_option, mode, data_pca, pca_col_names, y)

    #####################################################################################################
    # unsupervised ML
    # make a prediction for year 2025 [autonatic mode and oscars selected as outcome]
    #####################################################################################################
    if prediction_option == mode[0] and outcome_option==categories[0]:
        predict_movies_data_2025(num_attr, cat_attr)



