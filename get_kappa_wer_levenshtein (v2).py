import mysql.connector
import statistics
from statsmodels.stats.inter_rater import fleiss_kappa
import textdistance
import jiwer
import os


# This script was originaly created as part of the works on the creation of the CORAA dataset, 
# created to assist the training of portuguese automatic speech recognition tools

# This is a script that calculates many different mettrics from the final export of the
# CORAA dataset. As input, the script requires only the final export csv file, and also access to the original
# project's SQL database

# Infos regarding CORAA's original database such as queries and credentials have been removed 
# for security reasons

export_file = './final_export.csv'

log_level = 0 # 0 - no logging
              # 1 - minimal info
              # 2 - full progress report





# GoldEntry
# an object that represent a gold entry in the database
class GoldEntry:

    id = -1
    file_path = ''
    text = ''
    task = -1
    invalid_user1 = 1

    def __init__(self, id, file_path, text, task, invalid_user1):
        self.id = id
        self.file_path = file_path
        self.text = text
        self.task = task
        self.invalid_user1 = invalid_user1
        

    def fix_gold_file_path(file_path):

        if('alip' in file_path):
            return file_path.replace('data/', 'wavs/ALIP/')
        elif('NURC_RE' in file_path):
            return file_path.replace('data/', 'wavs/NURC_RE/')
        elif('Ted_part' in file_path):
            return file_path.replace('data/', 'wavs/TED/')
        elif('CORAL' in file_path):
            return file_path.replace('data/', 'wavs/CORAL/')
        elif('_sp_.' in file_path):
            return file_path.replace('data/', 'wavs/SP2010/')
        else:
            raise RuntimeError('File_path \"' + file_path + '\" didn\'t match any of the expected paterns')


# get_gold_set
# Acesses the dataset and retrives infos from all the gold entries
# RETURNS: a list of 'GoldEntry' objects, each representing one gold entry. Each object has: id, file_path, 
# text, task and invalid_user1
def get_gold_set():

    if(log_level >= 1): print('Retriving gold set info from database')
    

    # execute query and receives all information about the gold set
    try:
        mydb = mysql.connector.connect(
            host="",
            user="",
            password="",
            database=""
        )

        mycursor = mydb.cursor()

    except Exception as e:
        print('\nFailed to connect')
        print(e)
        exit()


    query = f""""""

    mycursor.execute(query)
    result = mycursor.fetchall()

    if(log_level >= 2): print('Query returned')

    # uses infos returned in query to build the list of GoldEntry objects
    gold = []
    tot = len(result)
    don = 0

    for entry in result:
        gold.append(GoldEntry(entry[0], GoldEntry.fix_gold_file_path(entry[1]), entry[2], entry[3], entry[4]))

        # progress control
        don += 1
        if(don % int(tot/10) == 0):
            if(log_level >= 2): print(str(round(100*don/tot, 2)) + '% done')

    return gold



# get_gold_counterparts_in_export
# RECEIVES: the csv export file and a list of GoldEntry objects, created by the "get_gold_set" function
# Goes throught the export file looking for gold's normal counterparts. Builds a dict where the key is the
# file_path and the value is its transcription
# RETURNS: a dict, where the key is the file_path and the value is its transcription
def get_gold_counterparts_in_export(input_file, gold_set):

    if(log_level >= 1): print('Reading export lines')

    # makes a list of all the gold entries' file_paths
    gold_files = []
    for audio in gold_set:
        gold_files.append(audio.file_path)

    # dict to be returned
    export_entries = {}

    with open(input_file, 'r') as f:

        lines = f.readlines()

        tot_lines = len(lines)
        don_lines = 0

        if(log_level >= 2): print('Total of ' + str(tot_lines) + ' lines')

        # see if the current line's file_path is from a gold entry. If so, updates in the dict
        for line in lines:

            file_path = line.split(',')[0]
            text = ''.join(line.split(',')[4:])

            if(file_path in gold_files):
                export_entries[file_path] = text

            don_lines += 1

            if(don_lines % int(tot_lines/10) == 0):
                if(log_level >= 2): print(str(round(100*don_lines/tot_lines, 2)) + '% done')
    f.close()

    return export_entries





# calculate_kappa
# calculates the kappa based on the gold_set (get_gold_set function) and a dict (get_gold_counterparts_in_export function) 
# containing the gold's counterpart in the export file and their respective texts.
# One can also decide to calculate the kappa only to task=0 ("anno"), task=1 ("trans"), or both ("all"), by setting the
# "task" value
# RETURNS: the kappa value
def calculate_kappa(gold_set, export, task):

    if(log_level >= 1): print('Calculating kappa')
    kappa_matrix = []
    temp_kappa_matrix = []

    if(task == 'anno'):
        task = 0
    elif(task == 'trans'):
        task = 1
    else:
        task = -1

    # for each audio in the gold set, checks if the audio was validated in the gold set
    # and also checks if the audio is present in the export file (since the export file 
    # only contains validated audios)
    for audio in gold_set:

        validations = 0
        if(audio.task == task or task == -1):               # checks number of validations
            if(audio.file_path in export):
                validations += 1
            if(audio.invalid_user1 == 0 and audio.text != '###'):
                validations += 1

            kappa_matrix.append([validations, 2-validations])      # builds kappa input matrix

    kappa = fleiss_kappa(kappa_matrix)                          # calculates kappa

    print('Kappa is ' + str(kappa) + ' (' + str(len(kappa_matrix)) + ' samples)')

    return kappa





# calculate_mettrics_from_transcription
# calculates wer and levenshtein similarity based on the gold_set (get_gold_set function) and a 
# dict (get_gold_counterparts_in_export function), containing the gold's counterpart in the export file and their 
# respective texts.
# RECEIVES: a gold_set (get_gold_set function) and a hashmap (get_gold_counterparts_in_export)
# RETURNS: average WER and average levenshtein similarity
def calculate_mettrics_from_transcription(gold_set, export):

    if(log_level >= 1): print('Calculating wer and leveistain')
    n = 0
    avg_wer = 0
    avg_lvs = 0

    # For each audio in the gold set, if the audio has task 1 and has been validated by both gold set and
    # final export, compares the two trascriptions to calculate wer and levenshtein distance   
    for audio in gold_set:

        if(audio.task == 1):
            if(audio.file_path in export and audio.text != '###'):

                t1 = (export[audio.file_path]).replace('\n', '')
                t2 = (audio.text).replace('\n', '')

                n += 1
                tmp_wer = jiwer.wer(t1, t2)
                avg_wer += tmp_wer
                tmp_lvn = textdistance.levenshtein.normalized_similarity(t1, t2)
                avg_lvs += tmp_lvn

    avg_wer /= n
    avg_lvs /= n

    print('Average WER: ' + str(avg_wer) + ' (' + str(n) + ' samples)')
    print('Average Leveistain: ' + str(avg_lvs) + ' (' + str(n) + ' samples)')

    return avg_wer, avg_lvs






gold_set = get_gold_set()
export = get_gold_counterparts_in_export(export_file, gold_set)
calculate_kappa(gold_set, export, 'all')  # 'anno', 'trans' or 'all'
calculate_mettrics_from_transcription(gold_set, export)
