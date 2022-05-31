# Generateemaildata
# Author: Stiven LaVrenov
# This tool will generate email test data for product fail-state testing

import os
import time
import timeit
import logging
import hashlib
import errno
import random
import argparse
import pandas as pd
import nlpaug.augmenter.word as naw
import nlpaug.flow as naf

from tools.generateemail import create_message, html, make_reply

emails = os.getcwd() + '/emailoutput/emails/'
rand_samp_emails = os.getcwd() + '/emailoutput/randsampemails/'
augmented_emails = os.getcwd() + '/emailoutput/augmentedemails/'

# Make directory to store email outputs
if not os.path.exists(os.path.dirname(emails)):
    try:
        os.makedirs(os.path.dirname(emails))
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise

if not os.path.exists(os.path.dirname(augmented_emails)):
    try:
        os.makedirs(os.path.dirname(augmented_emails))
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise

if not os.path.exists(os.path.dirname(rand_samp_emails)):
    try:
        os.makedirs(os.path.dirname(rand_samp_emails))
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

def scenario_error():
    print('\n', '----------------------------------------------------------------------', '\n')
    print('  UNSUPPORTED SCENARIO WAS CHOSEN |', 'PLEASE CHOOSE A SUPPORTED SCENARIO')
    print('\n', '----------------------------------------------------------------------', '\n')
    print('Available Scenarios:', '\n', '-- secrecy', '\n', '-- ga', '\n', '-- rumor', '\n', '-- cov', '\n')

def create_hash(subject, sender, recipients):
    hash = hashlib.md5(
            str(subject)
            .join(str(sender))
            .join(str(recipients))
            .join(str(time.time()))
            .encode('utf-8')).hexdigest()

    return hash

def rand_state(input_file):
    return random.randint(0, len(input_file)-1)

def augmenter():
    return naf.Sometimes([
            naw.SpellingAug(aug_max=1),
            naw.ContextualWordEmbsAug(model_path='roberta-base', action='substitute', aug_max=1)],
            aug_p=0.8)

def write_email(subject, sender, recipients, cc_recipients, bcc_recipients, body, attachments, language, charset, num, augment):
    """
    Creates an email based off the given parameters

    No given values will result in an email with default values

    Parameters:
    -----------
    subject : String
        A given string to define the subject line of the email
        Default : "Default Subject"

    sender : String
        A given string to define the sender // From: [sender]
        Default : "sender@test.com"

    recipients : List
        A given list of strings to define the recipients of the email
        Default : "recipient@test.com"

    cc_recipients : List
        A given list of strings to define the cc_recipients of the email

    bcc_recipients : List
        A given list of strings to define the bcc_recipients of the email

    body : String
        A given string to define the body of the email
        Default : "Lorem ipsum dolor sit amet"

    attachments : Dictionary
        A given dictionary to define the attachments included in the email
        *** WIP *** kinda works but puts attachments in a seperate .eml that is attached to the main .eml

    language : str
        A given string to specify the language in the header
        Default : 'en'

    charset : str
        A given string to specify the charset in the header
        Default : 'utf-8'

    num : int
        A given integer to create an N number of .eml files
        Default : 1

    augment : Boolean
        A Boolean value to determine if the body will be augmented
        Default : False
    """
    print('\n')
    for _ in range(int(num)):
        hash = create_hash(subject, sender, recipients)

        with open(emails+hash+'.eml', 'w') as ef:
            email = create_message(subject=subject,
                                    sender=sender,
                                    recipients=recipients,
                                    cc_recipients=cc_recipients,
                                    bcc_recipients=bcc_recipients,
                                    text=body,
                                    html=html(body),
                                    attachments=attachments,
                                    language=language,
                                    charset=charset,
                                    )
            ef.write(str(email))
            ef.write('\n')
        ef.close()
        print('#####    CREATED:', hash + '.eml  #####')

        if augment:
            aug = augmenter()
            aug_text = aug.augment(body)

            with open(augmented_emails+hash+'.eml', 'w') as af:
                email = create_message(subject=subject,
                                    sender=sender,
                                    recipients=recipients,
                                    cc_recipients=cc_recipients,
                                    bcc_recipients=bcc_recipients,
                                    text=aug_text,
                                    html=html(aug_text),
                                    attachments=attachments,
                                    language=language,
                                    charset=charset,
                                    )
                af.write(str(email))
                af.write('\n')
            af.close()
            print('#####    AUGMENTED:', hash + '.eml   #####')
    print('\n')

def write_rand_email(subject, sender, recipients, cc_recipients, bcc_recipients, data_file, language, charset, num, label_case, augment):
    """
    skipping out on attachments for now for ease of use

    Creates an email based off the given parameters

    An inputfile must be given in order for this function to run

    Parameters:
    -----------
    subject : String
        A given string to define the subject line of the email
        Default : "Default Subject"

    sender : String
        A given string to define the sender // From: [sender]
        Default : "sender@test.com"

    recipients : List
        A given list of strings to define the recipients of the email
        Default : "recipient@test.com"

    cc_recipients : List
        A given list of strings to define the cc_recipients of the email

    bcc_recipients : List
        A given list of strings to define the bcc_recipients of the email

    data_file : DataFrame
        A Pandas DataFrame from a given input file

    language : str
        A given string to specify the language in the header
        Default : 'en'

    charset : str
        A given string to specify the charset in the header
        Default : 'utf-8'

    num : int
        A given integer to create an N number of .eml files
        Default : 1

    label_case : str
        A Boolean-esque value to determine if the body will contain all positive or all negative cases

    augment : Boolean
        A Boolean value to determine if the body will be augmented
        Default : False
    """
    text_column = data_file.columns.get_loc("text")
    #label_column = data_file.columns.get_loc("label") // Not needed for now

    pos_case = data_file[data_file.label == 1]
    neg_case = data_file[data_file.label == 0]

    print('\n')
    for _ in range(int(num)):
        hash = create_hash(subject, sender, recipients)

        if label_case == '1':
            rand_num = rand_state(pos_case)
            body = pos_case.iloc[rand_num, text_column]
        elif label_case == '0':
            rand_num = rand_state(neg_case)
            body = neg_case.iloc[rand_num, text_column]
        else:
            rand_num = rand_state(data_file)
            body = data_file.iloc[rand_num, text_column]

        with open(rand_samp_emails+hash+'.eml', 'w') as rf:
            email = create_message(subject=subject,
                                    sender=sender,
                                    recipients=recipients,
                                    cc_recipients=cc_recipients,
                                    bcc_recipients=bcc_recipients,
                                    text=body,
                                    html=html(body),
                                    language=language,
                                    charset=charset,
                                    )
            rf.write(str(email))
            rf.write('\n')
        rf.close()
        print('#####    CREATED:', hash + '.eml    #####')

        if augment:
            aug = augmenter()
            aug_text = aug.augment(body)

            with open(augmented_emails+hash+'.eml', 'w') as af:
                email = create_message(subject=subject,
                                    sender=sender,
                                    recipients=recipients,
                                    cc_recipients=cc_recipients,
                                    bcc_recipients=bcc_recipients,
                                    text=aug_text,
                                    html=html(aug_text),
                                    language=language,
                                    charset=charset,
                                    )
                af.write(str(email))
                af.write('\n')
            af.close()
            print('#####    AUGMENTED:', hash + '.eml   #####')
    print('\n')

def write_reply(subject, sender, recipients, cc_recipients, bcc_recipients, data_file, language, charset, num):
    """
    Creates an email reply based off the given parameters

    An inputfile must be given in order for this function to run

    Parameters:
    -----------
    subject : String
        A given string to define the subject line of the email
        Default : "Default Subject"

    sender : String
        A given string to define the sender // From: [sender]
        Default : "sender@test.com"

    recipients : List
        A given list of strings to define the recipients of the email
        Default : "recipient@test.com"

    cc_recipients : List
        A given list of strings to define the cc_recipients of the email

    bcc_recipients : List
        A given list of strings to define the bcc_recipients of the email

    data_file : DataFrame
        A Pandas DataFrame from a given input file

    language : str
        A given string to specify the language in the header
        Default : 'en'

    charset : str
        A given string to specify the charset in the header
        Default : 'utf-8'

    num : int
        A given integer to create an N number of .eml files
        Default : 1
    """
    text_column = data_file.columns.get_loc("text")
    #label_column = data_file.columns.get_loc("label")

    print('\n')
    for _ in range(int(num)):
        hash = create_hash(subject, sender, recipients)

        rand_num = rand_state(data_file)
        body = data_file.iloc[rand_num, text_column]
        email1 = create_message(subject=subject, sender=sender, recipients=recipients, cc_recipients=cc_recipients,
                                bcc_recipients=bcc_recipients, text=body, html=html(body), language=language, charset=charset)
    
        rand_num = rand_state(data_file)
        body = data_file.iloc[rand_num, text_column]
        email2 = create_message(subject=subject, sender=sender, recipients=recipients, cc_recipients=cc_recipients,
                                bcc_recipients=bcc_recipients, text=body, html=html(body), language=language, charset=charset)

        with open(rand_samp_emails + hash + '.eml', 'w') as rf:
            rf.write(str(make_reply(email2, email1)))
            rf.write('\n')
        rf.close()
        print('#####    CREATED:', hash + '.eml reply    #####')
    print('\n')

def write_thread(subject, sender, recipients, cc_recipients, bcc_recipients, data_file, language, charset, num):
    """
    Creates an email thread based off the given parameters

    An inputfile must be given in order for this function to run

    Parameters:
    -----------
    subject : String
        A given string to define the subject line of the email
        Default : "Default Subject"

    sender : String
        A given string to define the sender // From: [sender]
        Default : "sender@test.com"

    recipients : List
        A given list of strings to define the recipients of the email
        Default : "recipient@test.com"

    cc_recipients : List
        A given list of strings to define the cc_recipients of the email

    bcc_recipients : List
        A given list of strings to define the bcc_recipients of the email

    data_file : DataFrame
        A Pandas DataFrame from a given input file

    language : str
        A given string to specify the language in the header
        Default : 'en'

    charset : str
        A given string to specify the charset in the header
        Default : 'utf-8'

    num : int
        A given integer to create an N number of .eml files
        Default : 1
    """
    text_column = data_file.columns.get_loc("text")
    #label_column = data_file.columns.get_loc("label")

    hash = create_hash(subject, sender, recipients)

    print('\n')
    for _ in range(int(num)):
        rand_num = rand_state(data_file)
        body = data_file.iloc[rand_num, text_column]

        with open(rand_samp_emails + hash + '.eml', 'a') as tf:
            email = create_message(subject=subject,
                                    sender=sender,
                                    recipients=recipients,
                                    cc_recipients=cc_recipients,
                                    bcc_recipients=bcc_recipients,
                                    text=body,
                                    html=html(body),
                                    language=language,
                                    charset=charset,
                                    )
            tf.write(str(email))
            tf.write('\n')
        tf.close()
    print('#####    CREATED:', hash + '.eml thread    #####')
    print('\n')

def run(args):
    print(args)
    logger.debug('Arguments: %s' % args)

    recipients = []
    cc_recipients = []
    bcc_recipients = []
    attachments = []

    # I don't know why but this makes it not output as a list in the actual email
    if recipients:
        recipients.append(args.recipients)
    else:
        recipients = args.recipients
    if cc_recipients:
        cc_recipients.append(args.cc_recipients)
    else:
        cc_recipients = args.cc_recipients
    if bcc_recipients:
        bcc_recipients.append(args.bcc_recipients)
    else:
        bcc_recipients = args.bcc_recipients

    subject = args.subject
    sender = args.sender
    body = args.body
    attachments = args.attachments
    language = args.lang
    charset = args.charset

    scenario = args.scenario
    reply = args.reply
    thread = args.thread
    num = args.numdata
    augment = args.augment
    inputfile = args.inputfile
    label_case = args.labelcase
    custom = args.custom
    
    if custom:
        write_email(subject, sender, recipients, cc_recipients, bcc_recipients, body, attachments, language, charset, num, augment)

    if inputfile and not (thread or reply):
        data_file = pd.read_csv(inputfile)
        write_rand_email(subject, sender, recipients, cc_recipients, bcc_recipients, data_file, language, charset, num, label_case, augment)

    if reply:
        data_file = pd.read_csv(inputfile)
        write_reply(subject, sender, recipients, cc_recipients, bcc_recipients, data_file, language, charset, num)

    if thread:
        data_file = pd.read_csv(inputfile)
        write_thread(subject, sender, recipients, cc_recipients, bcc_recipients, data_file, language, charset, num)

    if scenario and not inputfile:
        if scenario == 'cov':
            data_file = pd.read_csv('data/cov_corpus.csv')
            write_rand_email(subject, sender, recipients, cc_recipients, bcc_recipients, data_file, language, charset, num, label_case, augment)
        elif scenario == 'ga':
            data_file = pd.read_csv('data/ga_corpus.csv')
            write_rand_email(subject, sender, recipients, cc_recipients, bcc_recipients, data_file, language, charset, num, label_case, augment)
        elif scenario == 'rumor':
            data_file = pd.read_csv('data/rumor_corpus.csv')
            write_rand_email(subject, sender, recipients, cc_recipients, bcc_recipients, data_file, language, charset, num, label_case, augment)
        elif scenario == 'secrecy':
            data_file = pd.read_csv('data/secrecy_corpus.csv')
            write_rand_email(subject, sender, recipients, cc_recipients, bcc_recipients, data_file, language, charset, num, label_case, augment)
        else:
            scenario_error()

if __name__ == '__main__':
    start = timeit.default_timer()

    logger.info('Parsing Arguments')
    parser = argparse.ArgumentParser(description='Generate Smart Test Data')
    parser.add_argument('--subject', default='Default Subject')
    parser.add_argument('--sender', default='sender@test.com')
    parser.add_argument('--recipients', nargs='+', default=['recipient@test.com'])
    parser.add_argument('--cc_recipients', nargs='+', default=[])
    parser.add_argument('--bcc_recipients', nargs='+', default=[])
    parser.add_argument('--body', default='Lorem ipsum dolor sit amet')
    parser.add_argument('--attachments', default=[])
    parser.add_argument('--lang', default='en')
    parser.add_argument('--charset', default='utf-8')

    parser.add_argument('--scenario', default='')
    parser.add_argument('--numdata', default=1, help='Defines a set number of emails to generate, or number of emails in a thread')
    parser.add_argument('--inputfile', default='', help='Input .csv/.txt file for email body')
    parser.add_argument('--labelcase', default='', help='Option to output only positive or negative text')
    parser.add_argument('-a', '--augment', default=False, action='store_true', help='Enables email body augmentation')
    parser.add_argument('-c', '--custom', default=False, action='store_true', help='Enables custom CLI-based email creation')
    parser.add_argument('-r', '--reply', default=False, action='store_true', help='Enables email reply generation')
    parser.add_argument('-t', '--thread', default=False, action='store_true', help='Enables email thread generation')

    args = parser.parse_args()
    run(args)
    logger.info('End.')

    stop = timeit.default_timer()
    print('Time: ', stop - start)