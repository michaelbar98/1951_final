import collections
import sqlite3
from sqlite3 import Error
from collections import Counter
import numpy as np
from sklearn.decomposition import TruncatedSVD
# sklearn modules for classification
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
# sklearn modules for clustering
import math
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class ActorNLP():

    def __init__(self, sqlfile = "data/movies_clean.db"):
        conn = self.create_connection(sqlfile)
        self.conn = conn
        self.c = conn.cursor()
        documents, document_word_counts, word_ids, labels = self.read_data()
        topics = self.lsa(documents, document_word_counts, word_ids)
        knn_score, decision_tree_score, svm_score, mlp_score = self.classify_documents(topics, labels)
        print('\n===== CLASSIFIER PERFORMANCE =====')
        print('K-Nearest Neighbors Accuracy: %.3f' % knn_score)
        print('Decision Tree Accuracy: %.3f' % decision_tree_score)
        print('SVM Accuracy: %.3f' % svm_score)
        print('Multi-Layer Perceptron Accuracy: %.3f' % mlp_score)
        print('\n')

        # Cluster the data
        clusters, centers = self.cluster_documents(topics)
        self.plot_clusters(topics, clusters, centers)



    def classify_documents(self, topics, labels):

        def classify(classifier):
            """
            Trains a classifier and tests its performance.

            NOTE: since this is an inner function within
            classify_documents, this function will have access
            to the variables within the scope of classify_documents,
            including the train and test data, so we don't need to pass
            them in as arguments to this function.

            Args:
                classifier: an sklearn classifier
            Returns:
                The score of the classifier on the test data.
            """
            # TODO: fit the classifier on X_train and y_train
            # and return the score on X_test and y_test

            classifier.fit(X_train, y_train)
            return classifier.score(X_test, y_test)

        # TODO: use topics and labels to create X and y

        X = []
        y = []

        for i in range(len(topics)):
            currTopic = list(topics[i])
            X.append(currTopic)

        for i in range(len(labels)):
            y.append(labels[i])


        # TODO: modify the call to train_test_split to use
        # 90% of the data for training and 10% for testing.
        # Make sure to also shuffle and set a random state of 0!
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.10,
            random_state=0,
            shuffle=True
        )

        # TODO: create a KNeighborsClassifier that uses 3 neighbors to classify
        knn = KNeighborsClassifier(n_neighbors=3)
        knn_score = classify(knn)

        # TODO: create a DecisionTreeClassifier with random_state=0
        decision_tree = DecisionTreeClassifier(random_state=0)
        decision_tree_score = classify(decision_tree)

        # TODO: create an SVC with random_state=0
        svm = SVC(gamma='auto', random_state=0)
        svm_score = classify(svm)

        # TODO: create an MLPClassifier with random_state=0
        mlp = MLPClassifier(random_state=0)
        mlp_score = classify(mlp)

        return knn_score, decision_tree_score, svm_score, mlp_score

    def cluster_documents(self, topics, num_clusters=4):
        """
        Clusters documents based on their topics.

        Args:
            document_topics: a dictionary that maps document IDs to topics.
        Returns:
            1. the predicted clusters for each document. This will be a list
            in which the first element is the cluster index for the first document
            and so on.
            2. the centroid for each cluster.
        """
        k_means = KMeans(n_clusters=num_clusters, random_state=0)


        # TODO: Use k_means to cluster the documents and return the clusters and centers
        return k_means.fit_predict(list(topics.values())), k_means.cluster_centers_


    def plot_clusters(self, document_topics, clusters, centers):
        """
        Uses matplotlib to plot the clusters of documents

        Args:
            document_topics: a dictionary that maps document IDs to topics.
            clusters: the predicted cluster for each document.
            centers: the coordinates of the center for each cluster.
        """
        topics = np.array([x for x in document_topics.values()])

        ax = plt.figure().add_subplot(111, projection='3d')
        ax.scatter(topics[:, 0], topics[:, 1], topics[:, 2], c=clusters, alpha=0.3)  # Plot the documents
        ax.scatter(centers[:, 0], centers[:, 1], centers[:, 2], c='black', alpha=1)  # Plot the centers

        plt.tight_layout()
        plt.show()


    def lsa(self, documents, document_word_counts, word_ids):

        num_documents = len(documents.keys())
        num_words = len(word_ids.keys())

        tf_idf = np.zeros([num_documents, num_words])

        # TODO: calculate the values in tf_idf

        for document in documents.keys():
            for word in documents[document]:
                tf = documents[document][word]/sum(documents[document].values())
                idf = np.log(num_documents/document_word_counts[word])
                tfidf = tf * idf

                tf_idf[document][word_ids[word]] = tfidf


        # Rows represent documents and columns represent topics
        document_topic_matrix = TruncatedSVD(200, random_state=0).fit_transform(tf_idf)

        topicDict = {}
        for i in range(0, len(document_topic_matrix)):
            ind = (-document_topic_matrix[i]).argsort()[:3]
            topicDict[i] = list(ind)

        # TODO: return a dictionary that maps document IDs to a list of each one's top 3 topics
        return topicDict

    def create_connection(self, db_file):
        """ create a database connection to a SQLite database """
        try:
            conn = sqlite3.connect(db_file)
            return conn;
        except Error as e:
            print(e)
        finally:

            pass
        return

    def read_data(self):

        documents = {}  # Mapping from document IDs to a bag of words
        document_word_counts = Counter()  # Mapping from words to number of documents it appears in
        word_ids = {}  # Mapping from words to unique integer IDs
        labels = {}  # Mapping from document IDs to labels

        docid = 0
        wordid = 0

        movies = self.c.execute('''select distinct id, revenue from movies WHERE revenue>0''')

        movIds = list(movies)

        for k in movIds:
            sql = "select actorName from movie_actor where movieID = ?"
            output = self.c.execute(sql, [k[0]])
            actors = list(output)

            labels[docid] = math.floor(float(k[1]/2787965087)*10)

            bag = {}

            for actor in actors:
                actorName = actor[0]

                if actorName in bag.keys():
                    bag[actorName] = bag[actorName] + 1
                else:
                    bag[actorName] = 1
                    #Increment Counter for word occurence
                    document_word_counts[actorName] += 1

                #If word has been mapped to id, then move on. Otherwise map and increment current wordid.
                if actorName in word_ids.keys():
                    continue
                else:
                    word_ids[actorName] = wordid
                    wordid += 1

            documents[docid] = bag
            docid += 1
        return documents, document_word_counts, word_ids, labels




def main():
    a = ActorNLP()

if __name__ == '__main__':
    main()