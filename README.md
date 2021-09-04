# CORAA-scripts

These are some of the scripts I implemented when working on the creation of the CORAA dataset, 
created to assist the training of portuguese automatic speech recognition tools. In general, my job
was to pre-process audio and transcription so it could later be validated manually by hired students. I was also
charged with generating many kinds of metrics and informations about the audios and transcriptions collected.

### TREAT_ALIP_TRANSCRIPTIONS
One of the sub-dataset that compose the CORAA dataset is the ALIP dataset 
(https://revistas.gel.org.br/estudos-linguisticos/article/view/2430/1797). This dataset had 78 hours of transcripted
recordings, but the trascriptions had no synchronization maps. Therefore it was decided to use a forced alignment
software to automatically generate such maps. Such tools require as transcription input plain
text files, containing only the transcription texts, with indication of each text fragment that must be aligned.
How ever, ALIP's transcriptions could only be found in a raw pdf format, not segmented and full of extra notations
about the recordings themselves. Hence, this script had the purpose of treating these raw pdf transcriptions and generating
plain text files that could be used as input for the forced alignment tool

### GET_FLEISS_KAPPA
One way to evaluate the quality of the CORAA's dataset was to calculate the fleiss 
kappa value (https://en.wikipedia.org/wiki/Fleiss%27_kappa) among the hired students.
This is my own implementation of said algorithm. In this implementation, I try to give error messages a 
a little more intuitive compared to the available python libraries. The results, when not identical, 
differ by an order of 10^(-18)

### GET_KAPPA_WER_LEVENSHTEIN
After the final versions of the dataset started to be exported, I was task with the creation of a script
that would calculate some useful metrics, such as the general fleiss kappa value, WER (Word Error Rate) value
and levenshtein similarity value.

### GET_TIME_METTRICS_FROM_QUERY
Quite oftenly I would be asked to generate a plot showing the distribution of the durations of the audios
of the CORAA dataset, a subset of it, or one of its sub-datasets.

### GET_WORD_METTRICS_FROM_QUERY
Same as above, but regarding the number of words of the transcriptions of the CORAA dataset
