#!/usr/bin/env python3

import sys

import fasttext

_, corpus_file, model_file, *_ = sys.argv

# train
model = fasttext.train_unsupervised(corpus_file, lr=0.025, dim=200, epoch=30, minCount=1)

# save model as model_file
model.save_model(model_file)
