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

from sklearn.ensemble import RandomForestRegressor



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


def regression(model, x_train, y_train, x_test, y_test):
   # rf = RandomForestRegressor(n_estimators=1000, random_state=42)
    # Train the model on training data
   model.fit(x_train, y_train)
   predictions = model.predict(x_test)
   errors = abs(predictions - y_test)
   mean_error = np.mean(errors)
   error_var = errors - mean_error
   error_var = error_var**2
   error_deviation = np.sqrt(np.mean(error_var))
   print('Mean Absolute Error:', round((np.mean(errors))/1000000, 2), 'Millions.')
   print('R squared:', r2_score(y_test, predictions))
   print('mse:',  round(mean_squared_error(y_test, predictions)/1000000,2), 'Millions.')
   print('error std deviation:',  round(error_deviation/1000000,2), 'Millions.')

   print("")
   #mape = 100 * (errors / y_test)
   #accuracy = 100 - np.mean(mape)
   #print('Accuracy:', round(accuracy, 2), '%.')

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
        #print(curr_features)
        curr_features_sql = ",".join(curr_features)
        #print(curr_features_sql)

        all_input = "select " + curr_features_sql + ", m.revenue_now from movies as m, youtube_clean as yc, movies_twitter as mt where m.original_title = yc.name and mt.title = yc.name and m.budget != 0 and yc.dislikes != 0 and m.cast_score is not null"
        #print(all_input)

        out = c.execute(all_input)

        x = []
        y = []
        count = 0


        for row in out:
            for item in row:
                if item == None:
                    count+=1
            x.append(list(row[:-1]))
            y.append(row[-1])
        #print(count)
        #print(len(x), len(y))
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

        '''max_ = max(l for l in y)
        min_ = min(l for l in y)
        # print(max_, min_)
        for i in range(len(y)):
            y[i] = normalize(y[i], max_, min_)
        '''
        x_train, x_test, y_train, y_test = train_test_split(x, y)
        print("Linear Regressor")
        regression(LinearRegression(), x_train, y_train, x_test, y_test)
        print("Decision Tree Regressor")
        regression(tree.DecisionTreeRegressor(), x_train, y_train, x_test, y_test)
        print("Random Forest Regressor")
        mod = RandomForestRegressor(n_estimators=94)
        regression(mod, x_train, y_train, x_test, y_test)
        id = 5
        print(x_test[id])
        predict = mod.predict(np.array([x_test[id]]))
        act = y_test[id]
        #name =
        print(predict[0]/100000, act/1000000)
        '''mse_avg = 0
        r2_avg = 0
        for i in range(10):

            reg = LinearRegression()
            #print(all_input)

            reg.fit(x_train, y_train)
            y_predicted = reg.predict(x_test)
            #for i1, i2 in zip(y_predicted, y_test):
                #print((int) (i1), (int) (i2), (int)(i1-i2),((int)(i1-i2))/i2)
            mse = mean_squared_error(y_test, y_predicted)
            r2 = r2_score(y_test, y_predicted)
            mse_avg += mse
            r2_avg += r2
        results.append([mse_avg/10, r2_avg/10, curr_features])'''

print("sorted by mse")
results.sort(key=operator.itemgetter(0))
for result in results:
    print(result)
print("sorted by r2")
results.sort(key=operator.itemgetter(1))
for result in results:
    print(result)