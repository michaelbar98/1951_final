# Numerical Features have been min max scaled by fitting to minmaxscaler  
# Random Forest Regression and Decision Tree Regression.
# 5 Fold Cross Validation performed
# Evaluation Metrics: Mean Absolute Error, Mean Squared Error, Median Absolute Error, Explained Var Score, R^2 score

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn import tree
from sklearn import linear_model
from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor
from sklearn import metrics
from sklearn.metrics import mean_absolute_error, mean_squared_error, median_absolute_error, explained_variance_score, r2_score
from sklearn import preprocessing
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer, HashingVectorizer

global minval
global maxval
global min_max_scaler
global number_features

min_max_scaler = preprocessing.MinMaxScaler()
# text_features = ['original_title'] #include other text features like genre 
number_features = ['cast_score','budget_now', 'revenue_now','views', '(yc.views * (yc.likes / yc.dislikes))', 'yc.likes / yc.dislikes','likes','dislikes','count','like','retweet'] #include twitter data and youtube data
all_selected_features = ['original_title','cast_score','budget_now', 'revenue_now','views', '(yc.views * (yc.likes / yc.dislikes))', 'yc.likes / yc.dislikes','likes','dislikes','count','like','retweet']
eliminate_if_empty_list = ['revenue_now', 'views']

def data_clean(path):
    read_data = pd.read_csv(path)
    select_data = read_data[all_selected_features]
    data = select_data.dropna(axis = 0, how = 'any', subset = eliminate_if_empty_list)
    data = data.reset_index(drop = True)
    for y in number_features:
        data[y] = data[y].fillna(0.0).astype(np.float)
    return data

def preprocessing_numerical_minmax(data):
    global min_max_scaler
    scaled_data = min_max_scaler.fit_transform(data)
    return scaled_data

def regression_without_cross_validation(model, train_data, train_target, test_data): 
    model.fit(train_data, train_target)
    prediction = model.predict(test_data)
    return prediction

def regression_with_cross_validation(model, data, target, n_fold, model_name, pred_type):
    print(pred_type, " (Regression Model: ", model_name)
    cross_val_score_mean_abs_err  = cross_val_score(model, data, target, scoring = 'neg_mean_absolute_error', cv = n_fold) 
    print("\nCross Validation Score (Mean Absolute Error)        : \n", -cross_val_score_mean_abs_err)
    print("\nCross Validation Score (Mean Absolute Error) (Mean) : \n", -cross_val_score_mean_abs_err.mean())
    cross_val_score_mean_sqr_err  = cross_val_score(model, data, target, scoring = 'neg_mean_squared_error', cv = n_fold)  
    print("\nCross Validation Score (Mean Squared Error)         : \n", -cross_val_score_mean_sqr_err)
    print("\nCross Validation Score (Mean Squared Error)  (Mean) : \n", -cross_val_score_mean_sqr_err.mean())
    
def regression_scores(original_val, predicted_val, model_name):
    print("Regression Model Name: ", model_name)
    mean_abs_error = mean_absolute_error(original_val, predicted_val) 
    mean_sqr_error = mean_squared_error(original_val, predicted_val)
    median_abs_error = median_absolute_error(original_val, predicted_val)
    explained_var_score = explained_variance_score(original_val, predicted_val)
    r2__score = r2_score(original_val, predicted_val)
    
    print("\n")
    print("\nRegression Scores(train_test_split):\n")
    print("Mean Absolute Error    :", mean_abs_error)
    print("Mean Squared Error     :", mean_sqr_error)
    print("Median Absolute Error  :", median_abs_error)
    print("Explained Var Score    :", explained_var_score)
    print("R^2 Score              :", r2__score)
    print("\n\n")
   
def inverse_scaling(scaled_val):
    unscaled_val = min_max_scaler.inverse_transform(scaled_val.reshape(-1,1))
    return unscaled_val

def roundval(value):  
    return value.round()

def to_millions(value):   
    return value / 10000000

#plotting actual vs predicted for all data
def prediction_performance_plot(original_val, predicted_val, model_name, start, end, n, plot_type, prediction_type):
    #inverse transform and convert to millions
    original_val = to_millions(inverse_scaling(original_val)) 
    predicted_val = to_millions(inverse_scaling(predicted_val))
    print("\n")
    plt.title("\n"+ prediction_type + "Performance using " + model_name + "(Actual Vs. Predicted) "+plot_type + "\n")
    if plot_type=="all":
        plt.plot(original_val, c = 'g', label = "Actual")
        plt.plot(predicted_val, c = 'b', label = "Prediction")
    if plot_type=="seq":
        plt.plot(original_val[start : end + 1], c = 'g', label = "Actual")
        plt.plot(predicted_val[start : end + 1], c = 'b', label = "Prediction")
    if plot_type=="random":
        original_val_list = []
        predicted_val_list = []
        for k in range(n):
            i = random.randint(0, len(predicted_val) - 1)
            original_val_list.append(original_val[i])
            predicted_val_list.append(predicted_val[i])
        plt.plot(original_val_list, c = 'g', label = "Actual")
        plt.plot(predicted_val_list, c = 'b', label = "Prediction")
    plt.legend(["Actual", "Predicted"], loc = 'center left', bbox_to_anchor = (1, 0.8))
    plt.ylabel('Prediction (In Millions)', fontsize = 14)
    plt.grid()
    plt.show()

#printing actual vs predicted in a range 
def print_original_vs_predicted(original_val, predicted_val, i, j, n, model_name, print_type, prediction_type):
    #inverse transform and convert to millions
    original_val = to_millions(inverse_scaling(original_val)) 
    predicted_val = to_millions(inverse_scaling(predicted_val))
    
    print("\n"+prediction_type + " Comparision of Actual Vs. Predicted "+print_type+"\n")
    if print_type=="seq":
        if j<len(predicted_val):
            for k in range(i, j + 1):
                print("Actual" + prediction_type+" : ", original_val[k], ",   Predicted " +prediction_type," : ", predicted_val[k])
    if print_type=="random":
        for k in range(n):
            i = random.randint(0, len(predicted_val) - 1)
            print("Actual ", prediction_type, " : ", original_val[i], ",   Predicted " +prediction_type+" : ", predicted_val[i])
                        
#plotting actual vs predicted randomly using a bar chart          
def bar_plot_original_vs_predicted_rand(original_val, predicted_val, n, model_name, pred_type):  
    #inverse transform and convert to millions
    original_val = to_millions(inverse_scaling(original_val)) 
    predicted_val = to_millions(inverse_scaling(predicted_val))
    original_val_list = []
    predicted_val_list = []
    for k in range(n):
        i = random.randint(0, len(predicted_val) - 1)
        original_val_list.append(original_val[i])
        predicted_val_list.append(predicted_val[i])
    
    original_val_df = pd.DataFrame(original_val_list)
    predicted_val_df = pd.DataFrame(predicted_val_list)
    
    actual_vs_predicted = pd.concat([original_val_df, predicted_val_df], axis = 1)
    
    actual_vs_predicted.plot(kind = "bar", fontsize = 12, color = ['g','b'], width= 0.7)
    plt.title("\nUsing Numerical Features\n" + model_name + " : Actual "+ pred_type+ "Vs. Predicted "+ pred_type+"(Random)")
    plt.ylabel('Gross (In Millions)', fontsize = 14)
    plt.ylabel('Gross (In M', fontsize = 14)
    plt.xticks([])
    plt.legend(["Actual ", "Predicted"], loc = 'center left', bbox_to_anchor = (1, 0.8))
    plt.grid()
    plt.show()
        
#Plot features
    
def plot(data, kind, title, n_rows):
    plt.title(title, fontsize = 15)
    data[:n_rows].plot(kind = kind)
    plt.show()
    
def show_features(database):
    print("\n","--------------------------------------------------------------------------------------------------------")
    database.info()
    print("\n","--------------------------------------------------------------------------------------------------------")
    
def preprocessing_numerical(data):
    data_list_numerical = list(zip(data['cast_score'],data['budget_now'],data['views'],data['(yc.views * (yc.likes / yc.dislikes))'],data['yc.likes / yc.dislikes'],data['likes'],data['dislikes'],data['count'],data['like'],data['retweet']))
    data_numerical = np.array(data_list_numerical)
    data_numerical = preprocessing_numerical_minmax(data_numerical)
    return data_numerical

def preprocessed_aggregated_data(database): 
    numerical_data = preprocessing_numerical(database)
    return numerical_data

def regr_without_cross_validation_train_test_perform_plot(model, data, target, model_name, pred_type):
    train_data, test_data, train_target, test_target = train_test_split(data, target, test_size = 0.3, random_state = 0) 
    predicted_gross = regression_without_cross_validation(model, train_data, train_target, test_data)
    regression_scores(test_target, predicted_gross, model_name)
    prediction_performance_plot(test_target, predicted_gross, model_name, 200, 250, 0, "seq", pred_type)
    prediction_performance_plot(test_target, predicted_gross, model_name, 0, 0, 100, "random", pred_type)
    print_original_vs_predicted(test_target, predicted_gross, 0, 0, 10, model_name, "random", pred_type)
    bar_plot_original_vs_predicted_rand(test_target, predicted_gross, 20, model_name, pred_type)

path = "moviescleaned.csv"
data =data_clean(path)
target_gross = data['revenue_now']
database = data.drop('revenue_now', 1)
preprocessed_data = preprocessed_aggregated_data(database)
target_gross = np.array(list(target_gross))
target_gross = preprocessing_numerical_minmax(target_gross.reshape(-1,1))
print("feature calculation complete\n")
randomForestRegressorModel = RandomForestRegressor()
regression_with_cross_validation(randomForestRegressorModel, preprocessed_data, target_gross, 5, "Random Forest Regression", "Movie Revenue Prediction ")
regr_without_cross_validation_train_test_perform_plot(randomForestRegressorModel, preprocessed_data, target_gross,"Random Forest Regression", "Movie Revenue Prediction ")

DecisionTreeRegressorModel = tree.DecisionTreeRegressor()
regression_with_cross_validation(DecisionTreeRegressorModel, preprocessed_data, target_gross, 5, "Decision Tree Regression", "Movie Revenue Prediction ")
regr_without_cross_validation_train_test_perform_plot(DecisionTreeRegressorModel, preprocessed_data, target_gross, "Decision Tree Regression", "Movie Revenue Prediction ")

corr = data.corr()
c = plt.matshow(corr)
plt.colorbar(c)
plt.show()