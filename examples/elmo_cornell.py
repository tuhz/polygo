"""
Cornell dataset from training to saving.
"""
import argparse
import os

import numpy as np

from polygo.utils import load_data_and_labels, load_glove, filter_embeddings
from polygo.models import ELModel
from polygo.preprocessing import ELMoTransformer
from polygo.trainer import Trainer

def main(args):
    print('Loading dataset...')
    x_train, y_train = load_data_and_labels(args.train_data)
    x_valid, y_valid = load_data_and_labels(args.valid_data)
    x_test, y_test = load_data_and_labels(args.test_data)
    x_train = np.r_[x_train, x_valid]
    y_train = np.r_[y_train, y_valid]

    print('Transforming datasets...')
    p = ELMoTransformer()
    p.fit(x_train, y_train)

    print('Building a model.')
    model = ELModel(char_embedding_dim=args.char_emb_size,
                    word_embedding_dim=args.word_emb_size,
                    char_lstm_size=args.char_lstm_units,
                    word_lstm_size=args.word_lstm_units,
                    char_vocab_size=p.char_vocab_size,
                    word_vocab_size=p.word_vocab_size,
                    num_labels=p.label_size,
                    dropout=args.dropout)
    
    model, loss = model.build()
    model.compile(loss=loss, optimizer='adam')

    print('Training the model...')
    trainer = Trainer(model, preprocessor=p)
    trainer.train(x_train, y_train, x_test, y_test)

    print('Saving the model...')
    model.save(args.weights_file,args.params_file)

if __name__ == '__main__':
    DATA_DIR = os.path.join(os.path.dirname(__file__),'../data/conll2003/en/ner')
    EMBEDDING_PATH = os.path.join(os.path.dirname(__file__),'../data/glove.6B/glove.6B.100d.txt')
    parser = argparse.ArgumentParser(description='Training a model')
    parser.add_argument('--train_data', default=os.path.join(DATA_DIR,'train.txt'))
    parser.add_argument('--valid_data', default=os.path.join(DATA_DIR,'valid.txt'))
    parser.add_argument('--test_data', default=os.path.join(DATA_DIR,'test.txt'))
    parser.add_argument('--weights_file', default='weights.h5')
    parser.add_argument('--params_file', default='params.json')
    parser.add_argument('--preprocessor_file', default='preprocessor.json')
    # Training parameters
    parser.add_argument('--optimizer',default='adam')
    parser.add_argument('--max_epoch',type=int,default=15)
    parser.add_argument('--batch_size',type=int,default=32)
    parser.add_argument('--checkpoint_path',default=None)
    parser.add_argument('--log_dir',default=None)
    parser.add_argument('--early_stopping',action='store_true')
    # Model parameters
    parser.add_argument('--char_emb_size', type=int, default=25, help='character embedding size')
    parser.add_argument('--word_emb_size', type=int, default=100, help='word embedding size')
    parser.add_argument('--char_lstm_units', type=int, default=25, help='num of character lstm units')
    parser.add_argument('--word_lstm_units', type=int, default=100, help='num of word lstm units')
    parser.add_argument('--dropout', type=float, default=0.5, help='dropout rate')

    args = parser.parse_args()
    main(args)