# Generatetextdata
# Author: Stiven LaVrenov
# This tool will generate test data for product fail-state testing

import os
import random
import timeit
import logging
import errno
import argparse
import pandas as pd
import nlpaug.augmenter.word as naw
import nlpaug.flow as naf

textoutputdir = os.getcwd() + '/textoutput/'

# Make directory to store original and augmented text outputs
if not os.path.exists(os.path.dirname(textoutputdir)):
    try:
        os.makedirs(os.path.dirname(textoutputdir))
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise

# LOGGING
LOG_FILE = 'cmdltest.log'
LOGGING_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOGGING_LEVEL = logging.INFO
logging.basicConfig(level=LOGGING_LEVEL, format=LOGGING_FORMAT)
logger = logging.getLogger('logger')
logger.setLevel(LOGGING_LEVEL)

def path_creation(pathname):
    if os.path.exists(textoutputdir+pathname):
        print('#####    UPDATED:', pathname, '  #####')
    else:
        print('#####    CREATED:', pathname, '  #####')

def rand_state(data_file):
    return random.randint(0, len(data_file)-1)

def original_text(data_file, labeled):
    """ 
    Writes the original text data given by parameter into a seperate .csv file 

    .csv file should have a "text" and "label" column

    Parameter:
    ----------
    data_file : DataFrame
        Pandas DataFrame read from a given .csv/.txt file

    labeled : boolean
        boolean value to determine if output should contain labels
        Default : False
    """
    original_path = 'originaltext.csv'
    path_creation(original_path)
    text_column = data_file.columns.get_loc("text")
    label_column = data_file.columns.get_loc("label")
    with open(textoutputdir+original_path, 'w') as of:
        write_header(of)
        for x in range(len(data_file)):
            of.write(str(data_file.iloc[x, text_column]))
            if labeled:
                of.write(',')
                of.write(str(data_file.iloc[x, label_column]))
            of.write('\n')
    of.close()

def rand_sample_text(data_file, num, labeled, label_case, rand_samp):
    """
    Writes an N number of randomly chosen text(s) given by parameter into a .csv file

    .csv file should have a "text" and "label" column

    Parameters:
    -----------
    data_file : DataFrame
        Pandas DataFrame read from a given .csv/.txt file

    num : int
        N number of augmented text(s) to be outputted
        Default : 5
    
    labeled : boolean
        Boolean value to determine if output should contain labels
        Default : False

    label_case : str
        String value with boolean-esque properties to either write all negative or positive test cases
        label_case == '0' or label_case == '1'

    augment : boolean
        Boolean value to determine if text data should be augmented
        Default : False

    """
    if rand_samp:
        rand_sample_path = 'randsampletext.csv'
        path_creation(rand_sample_path)

        text_column = data_file.columns.get_loc("text")
        label_column = data_file.columns.get_loc("label")

        pos_case = data_file[data_file.label == 1]
        neg_case = data_file[data_file.label == 0]

        with open(textoutputdir+rand_sample_path, 'w') as rf:
            write_header(rf)
            for _ in range(int(num)):
                if label_case == '1':
                    rand_num = rand_state(pos_case)
                    rf.write(str(pos_case.iloc[rand_num, text_column]))
                    if labeled:
                        write_labeled(rf, pos_case, rand_num, label_column)
                elif label_case == '0':
                    rand_num = rand_state(neg_case)
                    rf.write(str(neg_case.iloc[rand_num, text_column]))
                    if labeled:
                        write_labeled(rf, neg_case, rand_num, label_column)
                else:
                    rand_num = rand_state(data_file)
                    rf.write(str(data_file.iloc[rand_num, text_column]))
                    if labeled:
                        write_labeled(rf, data_file, rand_num, label_column)
                rf.write('\n')
        rf.close()

def augment_data(data_file, num, labeled, label_case, augment):
    """
    Writes and augments an N number of randomly chosen text(s) given by parameter into a .csv file

    .csv file should have a "text" and "label" column

    Parameters:
    -----------
    data_file : DataFrame
        Pandas DataFrame read from a given .csv/.txt file

    num : int
        N number of augmented text(s) to be outputted
        Default : 5
    
    labeled : boolean
        Boolean value to determine if output should contain labels
        Default : False

    label_case : str
        String value with boolean-esque properties to either write all negative or positive test cases
        label_case == '0' or label_case == '1'

    augment : boolean
        Boolean value to determine if text data should be augmented
        Default : False
    """
    
    if augment:
        aug = naf.Sometimes([
                    naw.SpellingAug(aug_max=1),
                    naw.ContextualWordEmbsAug(model_path='roberta-base', action='substitute', aug_max=1)
                    ], aug_p=0.8)

        aug_path = 'augmentedtext.csv'
        path_creation(aug_path)

        text_column = data_file.columns.get_loc("text")
        label_column = data_file.columns.get_loc("label")

        pos_case = data_file[data_file.label == 1]
        neg_case = data_file[data_file.label == 0]

        with open(textoutputdir+aug_path, 'w') as af:
            write_header(af)
            for _ in range(int(num)):
                if label_case == '1':
                    rand_num = rand_state(pos_case)
                    aug_text = aug.augment(pos_case.iloc[rand_num, text_column])
                    af.write(str(aug_text))
                    if labeled:
                        write_labeled(af, pos_case, rand_num, label_column)
                elif label_case == '0':
                    rand_num = rand_state(neg_case)
                    aug_text = aug.augment(neg_case.iloc[rand_num, text_column])
                    af.write(str(aug_text))
                    if labeled:
                        write_labeled(af, neg_case, rand_num, label_column)
                else:
                    rand_num = rand_state(data_file)
                    aug_text = aug.augment(data_file.iloc[rand_num, text_column])
                    af.write(str(aug_text))
                    if labeled:
                        write_labeled(af, data_file, rand_num, label_column)
                af.write('\n')
        af.close()

def custom_text_write(text, num, augment):
    """
    Writes custom text defined in command line into a .csv file

    Parameters:
    -----------
    text : str
        String given in the '--custom' argument

    num : int
        N number of times text will be augmented
        Default : 5
    """
    custom_path = 'customtext.csv'
    path_creation(custom_path)

    with open(textoutputdir+custom_path, 'w') as cf:
        for _ in range(int(num)):
            cf.write(text)
            cf.write('\n')
    cf.close()

    if augment:
        aug_path = 'augmentedtext.csv'
        path_creation(aug_path)
        
        aug = naf.Sometimes([
                naw.SpellingAug(aug_max=1),
                naw.ContextualWordEmbsAug(model_path='roberta-base', action='substitute', aug_max=1)
                ], aug_p=0.8)

        with open(textoutputdir+aug_path, 'w') as af:
            for _ in range(int(num)):
                aug_text = aug.augment(text)
                af.write(str(aug_text))
                af.write('\n')
        af.close()

def scenario_error():
    print('\n', '----------------------------------------------------------------------', '\n')
    print('  UNSUPPORTED SCENARIO WAS CHOSEN |', 'PLEASE CHOOSE A SUPPORTED SCENARIO')
    print('\n', '----------------------------------------------------------------------', '\n')
    print('Available Scenarios:', '\n', '-- secrecy', '\n', '-- ga', '\n', '-- rumor', '\n', '-- cov', '\n')

def write_header(file_name):
    return file_name.write('text,'), file_name.write('label'), file_name.write('\n')

def write_labeled(file_name, data_file, rand_state, label_column):
    return file_name.write(','), file_name.write(str(data_file.iloc[rand_state, label_column]))

def run(args):
    print(args)
    logger.debug('Arguments: %s' % args)

    scenario = args.scenario
    labeled = args.labeled
    label_case = args.labelcase
    input_file = args.inputfile
    custom = args.custom
    num = args.numdata
    augment = args.augment
    randsamp = args.randsamp

    if input_file:
        data_file = pd.read_csv(input_file)
        original_text(data_file, labeled)
        rand_sample_text(data_file, num, labeled, label_case, randsamp)
        augment_data(data_file, num, labeled, label_case, augment)

    if scenario and not input_file:
        if scenario == 'secrecy':
            data_file = pd.read_csv('data/secrecy_corpus.csv')
            original_text(data_file, labeled)
            rand_sample_text(data_file, num, labeled, label_case, randsamp)
            augment_data(data_file, num, labeled, label_case, augment)
        elif scenario == 'ga':
            data_file = pd.read_csv('data/ga_corpus.csv')
            original_text(data_file, labeled)
            rand_sample_text(data_file, num, labeled, label_case, randsamp)
            augment_data(data_file, num, labeled, label_case, augment)
        elif scenario == 'rumor':
            data_file = pd.read_csv('data/rumor_corpus.csv')
            original_text(data_file, labeled)
            rand_sample_text(data_file, num, labeled, label_case, randsamp)
            augment_data(data_file, num, labeled, label_case, augment)
        elif scenario == 'cov':
            data_file = pd.read_csv('data/cov_corpus.csv')
            original_text(data_file, labeled)
            rand_sample_text(data_file, num, labeled, label_case, randsamp)
            augment_data(data_file, num, labeled, label_case, augment)
        else:
            scenario_error()

    if custom:
        custom_text_write(custom, num, augment)

if __name__ == '__main__':
    start = timeit.default_timer()

    logger.info('Parsing Arguments.')
    parser = argparse.ArgumentParser(description='Generate Smart Test Data')
    parser.add_argument('--scenario', default='secrecy', help='Scenario of generated test data desired')
    parser.add_argument('--numdata', default=5, help='Number of test entires to generate.')
    parser.add_argument('--inputfile', default='', help='Input .csv/.txt file for augmentation')
    parser.add_argument('--custom', default='', help='Custom text for data augmentation')
    parser.add_argument('--labelcase', default='', help='Option to choose values that are either 0 or 1')
    parser.add_argument('-l', '--labeled', default=False, action='store_true', help='Output labels along with text data')
    parser.add_argument('-a', '--augment', default=False, action='store_true', help='Option to write augmented text data for given scenario or inputfile')
    parser.add_argument('-r', '--randsamp', default=False, action='store_true', help='Option to write a random sample of text data from a given scenario or inputfile')

    args = parser.parse_args()
    print('\n')
    run(args)
    print('\n')
    logger.info('End.')

    stop = timeit.default_timer()
    print('Time: ', stop - start)