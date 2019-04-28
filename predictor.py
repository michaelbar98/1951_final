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
colors_list = list(colors._colors_full_map.values())

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

def read_data(fname, query):
    conn = sqlite3.connect(fname)
    c = conn.cursor()
    c.execute(query)
    data = c.fetchall()
    x, y = [], []
    for item in data:
        x.append([float(e) for e  in item[2:]])
        y.append(item[1])
    return np.array(x), np.array(y)

def read_genre(fname, query):
    conn = sqlite3.connect(fname)
    c = conn.cursor()
    c.execute(query)
    data = c.fetchall()
    x, y = [], []
    for item in data:
        x.append([float(e) for e  in item[:-1]])
        y.append(int(item[-1]))
    return np.array(x), np.array(y)

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

def regression():
    fname = 'data/movies_clean.db'
    script = "test.sql"
    with open(script, 'r') as infile:
        query = infile.readlines()
    query = ''.join([x for x in query])
    x, y = read_data(fname, query)
    meanx, stdx = np.mean(x, axis = 0), np.std(x, axis = 0)
    meany, stdy = np.mean(y), np.std(y)
    # normalize data for more accuarate training 
    newx = normalize(x)
    newy = np.reshape(y, [-1, 1])
    newy = normalize(newy)
    
    x_train, x_test, y_train, y_test = train_test_split(newx, newy)

    model = build_model(len(x_train[0]))
    epochs = 1000
    b_size = 2000
    #his = model.fit(x_train, y_train, epochs = epochs, verbose = 2,\
    #        validation_split = 0.2)
    his = model.fit(x_train, y_train, epochs = epochs, batch_size = b_size, verbose = 2,\
            validation_split = 0.2)
    ypred = model.predict(x_test)

    #xpred = rescale(x_test, meanx, stdx)
    #ypred = rescale(ypred, meany, stdy)
    
    fig1 = plt.figure()
    plt.plot(his.history["loss"])
    plt.plot(his.history["val_loss"])
    plt.xlabel('epoch')
    plt.ylabel('loss')
    plt.legend(['train', 'validation'])

    y_test = np.reshape(y_test, [1, -1])
    fig2 = plt.figure()
    plt.hist(y_test - ypred, label='error distribution')
    plt.ylabel('counts')
    plt.xlabel('y_test - NN_test')
    plt.savefig('error_dis.png')

    for i in range(len(x[0])):
        fig = plt.figure()
        plt.scatter(x_test[:, i], y_test,\
                facecolors='none', edgecolors='b', label = 'test data')
        plt.scatter(x_test[:, i], ypred,\
                facecolors='none', edgecolors='k', label='prediction by NN on test data')
        plt.ylabel('normalized revenue')
        plt.xlabel('normalized factor #' + str(i))
        plt.savefig(str(i) + 'factor.png')
        plt.legend()
    plt.show()

def genre_viz():
    fname = 'data/movies_clean.db'
    script = "genre.sql"
    with open(script, 'r') as infile:
        query = infile.readlines()
    query = ''.join([x for x in query])
    x, y = read_genre(fname, query)
    x = normalize(x)
    x = np.sin(x)
    genreid = set(y)
    colorid = list(range(len(genreid)))
    print("Current number of genres =", len(colorid))
    colordict = dict(zip(genreid, colorid))
    for i in range(len(x)):
        row = x[i]
        plt.scatter(row[0], row[1], color=colors_list[colordict[y[i]]])
    plt.ylabel('normalized revenue')
    plt.xlabel('normalized budget')
    plt.show()

def main():
    #regression()
    genre_viz()

if __name__ == "__main__":
    main()
