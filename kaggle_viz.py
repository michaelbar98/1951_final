# visualize kaggle data
import numpy as np
import matplotlib.pyplot as plt
import scipy.io
import sqlite3
import os
import matplotlib.colors as colors
import matplotlib
font={'family':'normal',
      'size'  :10}
matplotlib.rc('font', **font)
palette = {
           0: ['darkgreen', 'g', 'seagreen', 'mediumseagreen', 'lightseagreen', 'mediumturquoise'],\
           1: ['maroon', 'firebrick', 'red', 'coral', 'darksalmon', 'lightcoral'],\
           2: ['mediumpurple', 'darkorchid', 'plum', 'm', 'mediumvioletred', 'palevioletred']
           }
def query_count(table, col):
    query = "SELECT genreName, COUNT(genreName) \
             FROM \
             (SELECT revenue_now, budget_now, G.genreName \
             FROM movies \
             JOIN movie_genre as G \
             ON movies.id = G.movieID) as T \
             WHERE T.revenue_now > 0 and T.budget_now > 0 \
             GROUP BY genreName \
             ORDER BY COUNT(genreName) DESC \
             LIMIT 5;"

    conn = sqlite3.connect("./data/movies_clean.db")
    c = conn.cursor()
    query = query.replace('genreName', col)
    query = query.replace('movie_genre', table)
    c.execute(query)
    data = c.fetchall()
    name, count = [], []
    for item in data:
        name.append(item[0])
        count.append(item[1])
    total = 2282 # the total number of movies having nonnegative budgets and revenue
    other = total - sum(count)
    if other < 0:
        count = [int(x/2) for x in count]
    other = total - sum(count)
    name.append("other")
    count.append(other)
    return name, count

def plot_breakdowns(name, count, val):
    fig, ax = plt.subplots(figsize=(9, 3), subplot_kw=dict(aspect="equal"))
    wedges, texts = ax.pie(count, wedgeprops=dict(width=0.5), startangle=-40, colors=palette[val])
    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(xycoords='data', textcoords='data', arrowprops=dict(arrowstyle="-"),
          bbox=bbox_props, zorder=0, va="center")

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1)/2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        ax.annotate(name[i], xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y),
                horizontalalignment=horizontalalignment, **kw)

def main():
    dbdict = {"movie_genre": "genreName", "movie_country": "country_name",\
              "movie_company": "company_name"}
    test = "movie_company"
    i = 0
    for key in dbdict:
        name, count = query_count(key, dbdict[key])
        plot_breakdowns(name, count, i)
        i += 1
        plt.savefig(key+'.png')
    plt.show()

if __name__ == "__main__":
    main()
