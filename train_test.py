import db_cleaner
import sqlite3
from sqlite3 import Error
import json
import csv
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import itertools as it
import operator
from sklearn import tree
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor

'''
NOTE:
Run this file to see the regression results
'''



def create_connection(db_file = "data/movies_clean.db"):
    """ create a database connection to a SQLite database """
    try:
        conn = sqlite3.connect(db_file)
        return conn;
    except Error as e:
        print(e)
    finally:

        pass
    return


def normalize(x, x_max, x_min):
    #print(x)
    top = x -  x_min
    bot = x_max - x_min
    return top/bot


def regression(model, x_train, y_train, x_test, y_test, model_name):

   model.fit(x_train, y_train)
   predictions = model.predict(x_test)
   errors = abs(predictions - y_test)

   plt.hist(predictions - y_test, alpha = .7, label = model_name)


   mean_error = np.mean(errors)
   error_var = errors - mean_error
   error_var = error_var**2
   error_deviation = np.sqrt(np.mean(error_var))
   print('Mean Absolute Error:', round((np.mean(errors))/1000000, 2), 'Millions.')
   print('R squared:', r2_score(y_test, predictions))
   print('mse:',  round(mean_squared_error(y_test, predictions)/1000000,2), 'Millions.')
   print('error std deviation:',  round(error_deviation/1000000,2), 'Millions.')
   #print("weights:", model.coef_)

   print("")

conn = create_connection("data/movies_clean.db")
c = conn.cursor()

#features = ["m.original_title", "m.id", "m.budget_now", "m.cast_score", "yc.views", "yc.likes", "yc.dislikes", "mt.count", "mt.like", "mt.retweet", "m.revenue_now"]
features = ["m.budget_now", "m.cast_score","(yc.views * (yc.likes / yc.dislikes))", "yc.views","yc.likes / yc.dislikes", "yc.likes", "yc.dislikes", "mt.count", "mt.like", "mt.retweet"]
features_combinations = {}
results = []
#for i in range(3, len(features)+1):
for i in range(10, 11):
    curr_list_features = list(it.combinations(features, i))
    for curr_features in curr_list_features:
        print("FEATURES ", curr_features)
        curr_features_sql = ",".join(curr_features)
        #print(curr_features_sql)

        all_input = "select " + curr_features_sql + ", m.revenue_now from movies as m, youtube_clean as yc, movies_twitter as mt where m.original_title = yc.name and mt.title = yc.name and m.budget != 0 and yc.dislikes != 0 and m.cast_score is not null"
        #print(all_input)

        out = c.execute(all_input)

        x = []
        y = []
        count = 0


        for row in out:
            x.append(list(row[:-1]))
            y.append(row[-1])

        if 'm.cast_score' in curr_features:
            index = curr_features.index("m.cast_score")
            max_ = max(l[index] for l in x)
            min_ = min(l[index] for l in x)
            #print(max_, min_)
            for i in range(len(x)):
                data = x[i]
                #print(data)
                #print(index)
                data[index] = normalize(data[index], max_, min_)


        x_train, x_test, y_train, y_test = train_test_split(x, y)
        print("Linear Regressor")
        regression(LinearRegression(), x_train, y_train, x_test, y_test,"Linear Regressor")
        print("Decision Tree Regressor")
        regression(tree.DecisionTreeRegressor(), x_train, y_train, x_test, y_test,"Decision Tree Regressor")
        print("Random Forest Regressor")
        mod = RandomForestRegressor(n_estimators=94)
        regression(mod, x_train, y_train, x_test, y_test,"Random Forest Regressor")
        id = 5
        predict = mod.predict(np.array([x_test[id]]))
        act = y_test[id]

plt.legend()
plt.title("Different Regression Histograms")
plt.xlabel("Normalized Error")
plt.ylabel("Number of predicted movies")

plt.show()
