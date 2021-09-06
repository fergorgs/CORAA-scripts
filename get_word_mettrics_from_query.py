import os
import re
import statistics
import math
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import mysql.connector


# This script was originaly created as part of the works on the creation of the CORAA dataset, 
# created to assist the training of portuguese automatic speech recognition tools
 
# This script creates an array with the number of words of all the transcriptions present in a given csv file,
# sorts it, and plots a scatter plot, so you can visualize the word distribution of the transcriptions.
# In addition, it also creates an "info" file with some useful stats

# In order to use the script, you must call the "get_word_mettrics" function, providing a csv file
# containing the transcriptions to be plotted, the id of the csv's column that contains the
# file path, and an output directory where the plots can be saved as pngs. The script must also have access
# to CORAA's project original database

# Infos regarding CORAA's original database such as queries and credentials have been removed 
# for security reasons
 
 
mydb = mysql.connector.connect(
  host="",
  user="",
  password="",
  database=""
)

mycursor = mydb.cursor()


# plot
# Given a list of arrays of number of words (each array is plotted with a different color and label), 
# creates a scatter plot of said arrays and an "info" file with some useful stats
# RECEIVES: a list of arrays containing number of words, the title of the plot, the output directory 
# in which to save the plot, a list of labels for each plotted array
def plot(datasets, title='', output_dir='./', labels=None):
    
    # for each array in the list, sorts the array
    ds = []
    concat_words = []
    for words in datasets:
        words = sorted(words)
        ds.append(words)
        concat_words += words

    concat_words = sorted(concat_words)

    total = 0

    # gets the total number of words of all the arrays combined
    for words in ds:
        for word in words:
            total += word

    # writes the "infos" file, with some stats about all the arrays
    with open(output_dir + '/infos.txt', 'a') as f:
        f.write(title + '\n')
        f.write('Quartis:' + '\n')
        f.write('25%: ' + str(np.percentile(concat_words, 25)) + '\n')
        f.write('50%: ' + str(np.percentile(concat_words, 50)) + '\n')
        f.write('75%: ' + str(np.percentile(concat_words, 75)) + '\n')

        f.write('Total: ' + str(total) + ' palavras' + '\n')
        f.write('Média: ' + str(statistics.mean(concat_words)) + '\n')
        f.write('Desvio padrão: ' + str(statistics.stdev(concat_words)) + '\n')
        f.write('Nº de amostras: ' + str(len(concat_words)) + '\n')

        f.write('----------------------------------------------' + '\n')
        f.write('----------------------------------------------' + '\n')


    # Creates a scatter plot from the list of arrays. Each array will be repreented by a 
    # separate color in the final plot. The arrays will be identified by the labels informed by the user
    plots_word = []
    for words in ds:
        plot_word = []
        for index, word in enumerate(words):
            plot_word.append((index+1, word))
        plots_word.append(plot_word)


    num_of_samples = 0
    for words in ds:
        num_of_samples = max(num_of_samples, len(words))

    max_y_value = 0
    for words in ds:
        max_y_value = max(max_y_value, words[-1])


    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)


    y_tick = max(1, math.floor(max_y_value/10))
    major_y_ticks = np.arange(0, max_y_value+1, y_tick)
    minor_y_ticks = np.arange(0, max_y_value+1, y_tick/2)

    major_x_ticks = np.arange(0, num_of_samples+1, num_of_samples/5)

    ax.set_xticks(major_x_ticks)
    ax.set_yticks(major_y_ticks)
    ax.set_yticks(minor_y_ticks, minor=True)

    ax.grid(which='both')
    ax.grid(which='major', color='#3489ff')

    for index, plot_word in enumerate(plots_word):
        if(labels != None):
            plt.scatter(*zip(*plot_word), s=8, label=labels[index])
        else:
            plt.scatter(*zip(*plot_word), s=8)

    if(labels != None):
        plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1), fancybox=True, shadow=True, ncol=1)
    plt.title(title)
    plt.xlabel('Nº da amostra')
    plt.ylabel('Nº de palavras')
    plt.savefig(output_dir + '/' + title + '.png', bbox_inches='tight')



# get_word_mettrics
# plots the word mettrics of a set of transcriptions from the CORAA dataset
# RECEIVES: a csv file containing the transcriptions to be plotted, the id 
# of the column containing the transcriptions, the output directory where the plots will be saved
def get_word_mettrics(file, id_col, output_dir):

    # arrays to store the number of words of each sub-dataset transcriptions
    sp_words = []
    co_words = []
    nurc_words = []
    alip_words = []
    ted_words = []
    cnt = 0

    # opens the input file
    with open(file, 'r') as f:
        lines = f.readlines()

    # makes sure the output directory exists
    if not os.path.isdir(output_dir):   
        os.mkdir(output_dir)

    # for each line in the input file:
    # retreives the transcription from that line
    # saves the transcription in the proper sub-dataset array, according to the id present in the file path
    for line in lines:
        if(cnt % 500 == 0):
            print('Progress: ' + str(cnt) + ' of ' + str(len(lines)))
        file_path = line.split(',')[id_col]

        file_path = re.sub('wavs/[a-zA-Z0-9_]+', 'data', file_path)

        query = f""""""

        try:
            mycursor.execute(query)
            myresult = mycursor.fetchall()
        except:
            continue

        if(len(myresult) == 0):
            continue

        word_cnt = len(myresult[0][0].split(' '))

        if('_alip_.wav' in file_path):
            alip_words.append(word_cnt)
        elif('Ted_' in file_path):
            ted_words.append(word_cnt)
        elif('NURC_RE' in file_path):
            nurc_words.append(word_cnt)
        elif('_CO_' in file_path):
            co_words.append(word_cnt)
        elif('_sp_.wav' in file_path):
            sp_words.append(word_cnt)
        else:
            print('Other dataset found: ' + file_path)

        with open('./temp' + str(c) + '.csv', 'a') as g:
            g.write(str(id)+','+str(word_cnt)+'\n')

        cnt += 1

    try:
        os.system('rm ' + output_dir + '/infos.txt')
    except:
        None


    # Having now an array with the number of words of all the transcriptions separeted by sub-dataset, plots each array
    plot([alip_words], 'No palavras Alip', output_dir)
    plot([ted_words], 'No palavras TED', output_dir)
    plot([nurc_words], 'No palavras NURC-Recife', output_dir)
    plot([co_words], 'No palavras Coral Brasil', output_dir)
    plot([sp_words], 'No palavras SP-2010', output_dir)
    plot([alip_words + ted_words + nurc_words + co_words + sp_words], 'No palavras geral', output_dir)
    plot([alip_words, ted_words, nurc_words, co_words, sp_words], 'No palavras sobrepostos', output_dir, ['Alip', 'Ted', 'Nurc-Re', 'Coral', 'SP2010'])




# Main code-------------------------------------------------------
get_word_mettrics('./export.csv', 0, './graphs/words')
