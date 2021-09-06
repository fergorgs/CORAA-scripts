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
 
# This script creates an array with the duration of all the audios present in a given csv file,
# sorts it, and plots a scatter plot, so you can visualize the time distribution of the audios.
# In addition, it also creates an "info" file with some useful stats

# In order to use the script, you must call the "get_time_mettrics" function, providing a csv file
# containing the file paths of the audios to be plotted, the id of the csv's column that contains the
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
# Given a list of arrays of durations (each array is plotted with a different color and label), 
# creates a scatter plot of said arrays and an "info" file with some useful stats
# RECEIVES: a list of arrays containing durations, the title of the plot, the output directory 
# in which to save the plot, a list of labels for each plotted array
def plot(datasets, title='', output_dir='./', labels=None):
    
    # for each array in the list, sorts the array
    ds = []
    concat_times = []
    for times in datasets:
        times = sorted(times)
        ds.append(times)
        concat_times += times

    concat_times = sorted(concat_times)

    total = 0

    # gets the total time of all the arrays combined
    for times in ds:
        for time in times:
            total += time
    
    # writes the "infos" file, with some stats about all the arrays
    with open(output_dir + '/infos.txt', 'a') as f:
        f.write(title + '\n')
        f.write('Quartiles:' + '\n')
        f.write('25%: ' + str(np.percentile(concat_times, 25)) + '\n')
        f.write('50%: ' + str(np.percentile(concat_times, 50)) + '\n')
        f.write('75%: ' + str(np.percentile(concat_times, 75)) + '\n')

        f.write('Total: ' + str(total) + ' segundos' + '\n')
        f.write('Média: ' + str(statistics.mean(concat_times)) + '\n')
        f.write('Desvio padrão: ' + str(statistics.stdev(concat_times)) + '\n')
        f.write('Nº de amostras: ' + str(len(concat_times)) + '\n')

        f.write('----------------------------------------------' + '\n')
        f.write('----------------------------------------------' + '\n')


    # Creates a scatter plot from the list of arrays. Each array will be repreented by a 
    # separate color in the final plot. The arrays will be identified by the labels informed by the user
    plots_time = []
    for times in ds:
        plot_time = []
        for index, time in enumerate(times):
            plot_time.append((index+1, time))
        plots_time.append(plot_time)

    num_of_samples = 0
    for times in ds:
        num_of_samples = max(num_of_samples, len(times))

    max_y_value = 0
    for times in ds:
        max_y_value = max(max_y_value, times[-1])

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

    for index, plot_time in enumerate(plots_time):
        if(labels != None):
            plt.scatter(*zip(*plot_time), s=8, label=labels[index])
        else:
            plt.scatter(*zip(*plot_time), s=8)

    if(labels != None):
        plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1), fancybox=True, shadow=True, ncol=1)
    plt.title(title)
    plt.xlabel('Nº da amostra')
    plt.ylabel('Segundos')
    plt.savefig(output_dir + '/' + title + '.png', bbox_inches='tight')




# get_time_mettrics
# plots the time mettrics of a set of audios from the CORAA dataset
# RECEIVES: a csv file containing the file paths of the audios to be plotted, the id 
# of the column containing the file paths, the output directory where the plots will be saved
def get_time_mettrics(file, id_col, output_dir):

    # arrays to store the durations of each sub-dataset audios
    sp_times = []
    co_times = []
    nurc_times = []
    alip_times = []
    ted_times = []
    cnt = 0

    # opens the input file
    with open(file, 'r') as f:
        lines = f.readlines()

    # makes sure the output directory exists
    if not os.path.isdir(output_dir):   
        os.mkdir(output_dir)

    
    # for each line in the input file:
    # retreives the file path from that line
    # makes a query to the database to retreive that audio's duration
    # saves the duration in the proper sub-dataset array, according to the id present in the file path
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

        dur = myresult[0][0]
        if('_alip_.wav' in file_path):
            alip_times.append(myresult[0][0])
        elif('Ted_' in file_path):
            ted_times.append(myresult[0][0])
        elif('NURC_RE' in file_path):
            nurc_times.append(myresult[0][0])
        elif('_CO_' in file_path):
            co_times.append(myresult[0][0])
        elif('_sp_.wav' in file_path):
            sp_times.append(myresult[0][0])
        else:
            print('Other dataset found: ' + file_path)

        with open('./temp' + str(c) + '.csv', 'a') as g:
            g.write(str(id)+','+str(dur)+'\n')

        cnt += 1


    try:
        os.system('rm ' + output_dir + '/infos.txt')
    except:
        None


    # Having now an array with the duration of all the audios separeted by sub-dataset, plots each array
    plot([alip_times], 'Tempos Alip', output_dir)
    plot([ted_times], 'Tempos TED', output_dir)
    plot([nurc_times], 'Tempos NURC-Recife', output_dir)
    plot([co_times], 'Tempos Coral Brasil', output_dir)
    plot([sp_times], 'Tempos SP-2010', output_dir)
    plot([alip_times + ted_times + nurc_times + co_times + sp_times], 'Tempos geral', output_dir)
    plot([alip_times, ted_times, nurc_times, co_times, sp_times], 'Tempos sobrepostos', output_dir, ['Alip', 'Ted', 'Nurc-Re', 'Coral', 'SP2010'])







# Main code-------------------------------------------------------
get_time_mettrics('./export.csv', 0, './graphs/times')
