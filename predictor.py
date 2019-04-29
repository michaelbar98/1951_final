import numpy as np
import matplotlib.pyplot as plt
import scipy.io
import csv
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, optimizers
from sklearn.model_selection import train_test_split
import sqlite3
import os
import matplotlib.colors as colors
import matplotlib
colors_list = list(colors._colors_full_map.values())
EPOCH = 2000
BATCH_SIZE = 500
font={'family':'normal',
      'size'  :18}
matplotlib.rc('font', **font)
genre_id = dict()

def build_model(ndim):
    '''
    regression using NN
    '''
    l1, l2, l3 = 64, 64, 128
    dy = 1 # output dimension, since we are doing regression
    model = keras.Sequential([\
    layers.Dense(l1, activation=tf.nn.tanh, input_shape=[ndim]),\
    layers.Dense(l2, activation=tf.nn.tanh),\
    layers.Dense(l3, activation=tf.nn.tanh),\
    layers.Dense(dy)])

    adam = optimizers.Adam(lr=0.0001)
    model.compile(loss='mean_squared_error',\
                optimizer=adam,\
                metrics=['mean_absolute_error', 'mean_squared_error'])
    return model

def query_float(dbfile, query):
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
    c.execute(query)
    data = c.fetchall()
    x, y = [], []
    for item in data:
        x.append([float(f) for f in item[:-1]])
        y.append(float(item[-1]))
    return np.array(x), np.array(y)

def query_genre(dbfile, query):
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
    c.execute(query)
    data = c.fetchall()
    x, y = [], []
    for item in data:
        x.append([float(e) for e  in item[:-1]])
        y.append(int(item[-1]))
    return np.array(x), np.array(y)

def fill_genre_id():
    with open("./data/id_genre.txt", 'r') as infile:
        data = infile.readlines()
    for row in data:
        row = row.strip()
        arr = row.split(',')
        genre_id[int(arr[0])] = arr[1]

def normalize(x):
    nc = len(x[0])
    newx = np.zeros_like(x)
    means, stds = [], []
    for i in range(nc):
        col = x[:, i]
        col = (col - np.mean(col)) / np.std(col)
        newx[:, i] = col
        means.append(np.mean(col))
        stds.append(np.std(col))
    return newx

def rescale(x, mean, std):
    return np.multiply(x, std) + mean

def query_movies_clean():
    dbfile = 'data/movies_clean.db'
    script = "whole.sql"
    with open(script, 'r') as infile:
        query = infile.readlines()
    query = ''.join([x for x in query])
    x, y = query_float(dbfile, query)
    return x, y

def regression(x, y):
    if len(x) < 300:
        return 0
    meanx, stdx = np.mean(x, axis = 0), np.std(x, axis = 0)
    meany, stdy = np.mean(y), np.std(y)
    # normalize data for more accuarate training 
    newx = normalize(x)
    newy = np.reshape(y, [-1, 1])
    newy = normalize(newy)
    
    x_train, x_test, y_train, y_test = train_test_split(newx, newy)

    model = build_model(len(x_train[0]))
    epochs = EPOCH
    b_size = BATCH_SIZE
    #his = model.fit(x_train, y_train, epochs = epochs, verbose = 2,\
    #        validation_split = 0.2)
    his = model.fit(x_train, y_train, epochs = epochs, batch_size = b_size, verbose = 0,\
            validation_split = 0.2)
    return model, x_test, y_test, his

def check_overfit(his):
    fig1 = plt.figure()
    plt.plot(his.history["loss"])
    plt.plot(his.history["val_loss"])
    plt.xlabel('epoch')
    plt.ylabel('loss')
    plt.legend(['train', 'validation'])
    plt.show()

def plot_err_hist(y_ture, y_pred):
    fig = plt.figure()
    plt.hist(y_true - y_pred, label='error distribution')
    plt.ylabel('counts')
    plt.xlabel('True-Predict')
    plt.show()

def predict(model, x_test, y_test, topic):
    node = 100
    x_cont = np.linspace(min(x_test), max(x_test), node)
    ypred = model.predict(x_cont)
    
    y_test = np.reshape(y_test, [1, -1])
    for i in range(len(x_test[0])):
        fig = plt.figure()
        plt.gcf().subplots_adjust(bottom=0.2)
        plt.scatter(x_test[:, i], y_test,\
                facecolors='none', edgecolors='b', label = 'test data')
        plt.plot(x_cont, ypred, 'k--', label='NN regression')
        plt.ylabel('normalized revenue')
        plt.xlabel('normalized budget')
        plt.title(topic)
        plt.savefig('./nn_regression/'+topic+'.png')
        plt.legend()

def genre_viz():
    dbfile = 'data/movies_clean.db'
    script = "genre.sql"
    with open(script, 'r') as infile:
        query = infile.readlines()
    query = ''.join([x for x in query])
    x, y = query_genre(dbfile, query)
    x = normalize(x)
    genreid = set(y)
    group = dict()
    for i in genreid:
        group[i] = []
    for i, j in zip(x, y):
        group[j].append(i)
    for i in genreid:
        group[i] = np.array(group[i])
    return group

def run():
    x, y = query_movies_clean()
    model, x_test, y_test, his = regression(x, y)
    predict(model, x_test, y_test, "whole")
    '''
    data = genre_viz()
    count = 0
    for key in data.keys():
        count += 1
        print(count, "th genre")
        print("Feeding genre:", genre_id[key])
        x = data[key][:, 0]
        x = np.reshape(x, [-1, 1])
        y = data[key][:, 1]
        try:
            model, x_test, y_test, his = regression(x, y)
        except:
            model = None
        if model:
            predict(model, x_test, y_test, genre_id[key])
    '''
    plt.show()

def main():
    #genre_viz()
    fill_genre_id()
    run()

if __name__ == "__main__":
    main()
