
from __future__ import print_function
import numpy as np
import datetime

np.random.seed(1337)  # for reproducibility

from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Convolution2D, MaxPooling2D
from keras.utils import np_utils
import os
import subprocess
data_file = 'july_10_2016-data/data_set.npz'
if os.path.isfile(data_file):
    data = np.load(data_file)
else:
    subprocess.call('python 2d_seg.py', shell=True)
    data = np.load(data_file)

X_train = data['X_train']
X_test = data['X_test'] 
y_train = data['y_train']
y_test = data['y_test']


now = datetime.datetime.now

batch_size = 128
nb_classes = 2
nb_epoch = 500

# input image dimensions
img_rows, img_cols = 20, 20
# number of convolutional filters to use
nb_filters = 13#2
# size of pooling area for max pooling
nb_pool = 2
# convolution kernel size
nb_conv = 2


def train_model(model, train, test, nb_classes):
    X_train = train[0].reshape(train[0].shape[0], 1, img_rows, img_cols)
    X_test = test[0].reshape(test[0].shape[0], 1, img_rows, img_cols)
    X_train = X_train.astype('float32')
    X_test = X_test.astype('float32')
    X_train /= 255
    X_test /= 255
    print('X_train shape:', X_train.shape)
    print(X_train.shape[0], 'train samples')
    print(X_test.shape[0], 'test samples')

    # convert class vectors to binary class matrices
    Y_train = np_utils.to_categorical(train[1], nb_classes)
    Y_test = np_utils.to_categorical(test[1], nb_classes)

    model.compile(loss='categorical_crossentropy',
                  optimizer='adadelta',
                  metrics=['accuracy'])

    t = now()
    model.fit(X_train, Y_train,
              batch_size=batch_size, nb_epoch=nb_epoch,
              verbose=1,
              validation_data=(X_test, Y_test))
    print('Training time: %s' % (now() - t))
    score = model.evaluate(X_test, Y_test, verbose=0)
    print('Test score:', score[0])
    print('Test accuracy:', score[1])


# the data, shuffled and split between train and test sets
#(X_train, y_train), (X_test, y_test) = mnist.load_data()

# create two datasets one with digits below 5 and one with 5 and above
X_train_lt5 = X_train
y_train_lt5 = y_train
X_test_lt5 = X_test
y_test_lt5 = y_test

#X_train_gte5 = X_train[y_train >= 5]
#y_train_gte5 = y_train[y_train >= 5] - 5  # make classes start at 0 for
#X_test_gte5 = X_test[y_test >= 5]         # np_utils.to_categorical
#y_test_gte5 = y_test[y_test >= 5] - 5

# define two groups of layers: feature (convolutions) and classification (dense)
feature_layers = [
    Convolution2D(nb_filters, nb_conv, nb_conv,
                  border_mode='valid',
                  input_shape=(1, img_rows, img_cols)),
    #Activation('relu'),
    #Convolution2D(nb_filters, nb_conv, nb_conv),
    #Activation('relu'),
    #MaxPooling2D(pool_size=(nb_pool, nb_pool)),
    #Dropout(0.25),
    Flatten(),
]
classification_layers = [
    #Dense(128),
    Activation('relu'),
    Dropout(0.5),
    Dense(nb_classes),
    Activation('softmax')
]

# create complete model
model = Sequential()
for l in feature_layers + classification_layers:
    model.add(l)

# train model for 5-digit classification [0..4]
train_model(model,
            (X_train_lt5, y_train_lt5),
            (X_test_lt5, y_test_lt5), nb_classes)

# freeze feature layers and rebuild model
#for l in feature_layers:
#    l.trainable = False

# transfer: train dense layers for new classification task [5..9]
#train_model(model,
#            (X_train_gte5, y_train_gte5),
#            (X_test_gte5, y_test_gte5), nb_classes)
