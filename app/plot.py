import datetime
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib
import matplotlib.pyplot as plt
import os
import subprocess
import pandas as pd
import statistics
import collections



# Create the PdfPages object to which we will save the pages:
# The with statement makes sure that the PdfPages object is closed properly at
# the end of the block, even if an Exception occurs.

file_path = 'documents/'
questions_path = 'documents/survey_questions.txt'

class PDFPlotter:
    def __init__(self, section, course_id):
        self.section = section
        self.course_id = course_id
        self.file = file_path+"course_"+str(course_id)+".pdf"

    def peek_line(self, f):
        pos = f.tell()
        line = f.readline()
        f.seek(pos)
        return line

    def createPDF(self):
        """Creates a Multipage PDF"""
        df = pd.DataFrame.from_records(self.section)
        with PdfPages(self.file) as pdf:
            fp_questions = open(questions_path, 'r')
            fr_list = [4,5,11,15,19]
            self.createCover(self.course_id, pdf) # builds cover page for pdf
            figs = plt.figure(figsize=(10,10))
            graph_vals = []
            for i in (range(0, len(df.columns))):
                if i not in fr_list:
                    graph_vals.append( df[i] )
                else:
                    if len(graph_vals) > 0:
                        self.generatePlots(pdf,fp_questions,graph_vals)
                        plt.subplots_adjust(left=.15,right=0.75,wspace=0.7, hspace=.25*len(graph_vals))
                        pdf.savefig(figs)
                        plt.close()

                        graph_vals = [] #reset histogram arguments
                        figs = plt.figure(figsize=(10,10))
                    self.generateFreeResponse(pdf,df[i],fp_questions.readline(),i)

                print("DATA "+str(i))

            fp_questions.close()
            # We can also set the file's metadata via the PdfPages object:
            d = pdf.infodict()
            d['Title'] = 'Multipage PDF Example'
            d['Author'] = 'Jouni K. Sepp\xe4nen'
            d['Subject'] = 'How to create a multipage pdf file and set its metadata'
            d['Keywords'] = 'PdfPages multipage keywords author title subject'
            d['CreationDate'] = datetime.datetime(2009, 11, 13)
            d['ModDate'] = datetime.datetime.today()

    def createCover(self, course_id, pdf):
        """Method to create the cover page of the result pdf"""
        page = plt.figure(figsize=(10,10))
        page.clf()
        txt = "Evaluation Results for course "+str(course_id)
        page.text(0.5, 0.5, txt, transform=page.transFigure, bbox=dict(facecolor='red', alpha=0.5), size=35, ha="center")
        pdf.savefig()
        plt.close()

    def generatePlots(self, pdf, questions, graph_vals):
        """Method to generate plots all on one page of PDF"""
        grid = len(graph_vals)*100+11
        for i in range(len(graph_vals)):
            question = questions.readline()
            ax = plt.subplot(grid+i)
            if "hours" in question:
                x = graph_vals[i].values
                counter = collections.Counter(x)
                label = [1.5,2.0,2.5,3.0,3.5]
                for l in label:
                    if l not in counter:
                        counter[l] = 0
                counter = sorted(counter.items(), key=lambda x:x[0])
                print(counter)
                scalars = [x[1] for x in counter]
                labels = [x[0] for x in counter]
                print(str(scalars)+" "+str(labels))
                plt.bar(x=labels, height=scalars, width=0.3, tick_label=['<2','2','2.5','3','>3'], align='center')
                plt.xlabel('Time Spent (Hours)')
            else:
                x = list(pd.to_numeric(graph_vals[i]).values)
                plt.hist(x, rwidth=0.8, range=(1,5), bins=[0.5,1.5,2.5,3.5,4.5,5.5], density=True)
                plt.xlabel('Rating')
                print(x)
                txt = "mean: "+str(round(statistics.mean(map(float, x) ), 3) ) + "\nmedian: "+str(statistics.median(x)) + "\nN: " + str(len(x))
                ax.text(6.5, 0.0, txt,
                      bbox=dict(facecolor='red', alpha=0.5),
                      horizontalalignment='center',
                      verticalalignment='center')

            plt.ylabel('Frequency')
            # ax.yaxis.set_major_formatter(PercentFormatter(xmax=1))
            plt.title("Question: "+question, size=10)

    def generateFreeResponse(self, pdf, responses, question, index):
        """Method to generate free response answers on the PDF"""
        numResponses = len(responses)
        page = plt.figure(figsize=(10,10))
        page.clf()
        page.text(0.075, 0.90, "Question: "+question, transform=page.transFigure, bbox=dict(facecolor='blue', alpha=0.3), size=8, ha="left")
        page.text(0.1, 0.875, "Student Responses:", transform=page.transFigure, bbox=dict(facecolor='blue', alpha=0.3), size=8, ha="left")
        for i in range(numResponses):
            page.text(0.15, 0.85-i*.05, str(responses[i]), transform=page.transFigure, bbox=dict(facecolor='green', alpha=0.2), size=7, ha="left")
        pdf.savefig()
        plt.close()
