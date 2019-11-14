import datetime
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib
import matplotlib.pyplot as plt
import os
import subprocess
from app.survey import Section, fr_ids
import pandas as pd
import statistics
import collections



# Create the PdfPages object to which we will save the pages:
# The with statement makes sure that the PdfPages object is closed properly at
# the end of the block, even if an Exception occurs.

# class Plotter:
#     def __init__(self, section):
#         self.section = section
file_path = 'documents/'
questions_path = 'documents/survey_questions.txt'

class PDFPlotter:
    def __init__(self, section, file):
        self.section = section
        self.file = file_path+file


    def createPDF(self):
        """Creates a Multipage PDF"""
        print(self.file)
        df = pd.DataFrame.from_records(self.section.data)
        print(self.section.fr_list)
        # os.remove(self.file)
        with PdfPages(self.file) as pdf:
            fp_questions = open(questions_path, 'r')
            self.createCover(self.section.course_id, pdf) # builds cover page for pdf
            figs = plt.figure(figsize=(10,10))
            graph_vals = []
            for i in (range(2, len(self.section.data[0]))):

                if i not in fr_ids:
                    graph_vals.append( df[i] )
                    # self.generateStatistics(pdf,x)
                else:
                    if len(graph_vals) > 0:
                        self.generatePlots(pdf,fp_questions,graph_vals)
                        plt.subplots_adjust(left=.15,right=0.75,wspace=0.7, hspace=.25*len(graph_vals))
                        pdf.savefig(figs)
                        plt.close()

                        graph_vals = [] #reset histogram arguments
                        figs = plt.figure(figsize=(10,10))

                    self.generateFreeResponse(pdf,fp_questions.readline(),fr_ids.index(i))

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
        txt = "Evaluation Results for course "+course_id
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
                label = ["<2","2","2.5","3",">3"]
                for l in label:
                    if l not in counter:
                        counter[l] = 0
                scalars = list(counter.values())
                labels = list(counter.keys())
                print(str(scalars)+" "+str(labels))
                plt.bar(x=labels, height=scalars, width=0.8, tick_label=labels)
                plt.xlabel('Time Spent (Hours)')
            else:
                x = pd.to_numeric(graph_vals[i]).values
                plt.hist(x, rwidth=0.8, range=(1,5), bins=[0.5,1.5,2.5,3.5,4.5,5.5], density=True)
                plt.xlabel('Rating')
                txt = "mean: "+str(statistics.mean(map(float, x) ) ) + "\nmedian: "+str(statistics.median(x))
                ax.text(6.5, 0.0, txt,
                      bbox=dict(facecolor='red', alpha=0.5),
                      horizontalalignment='center',
                      verticalalignment='center')

            plt.ylabel('Frequency')
            # ax.yaxis.set_major_formatter(PercentFormatter(xmax=1))
            plt.title("Question: "+question, size=10)

    def generateFreeResponse(self, pdf, question, index):
        """Method to generate free response answers on the PDF"""
        responses = self.section.fr_list[index]
        numResponses = len(responses)
        page = plt.figure(figsize=(10,10))
        page.clf()
        page.text(0.075, 0.90, "Question: "+question, transform=page.transFigure, bbox=dict(facecolor='blue', alpha=0.3), size=8, ha="left")
        page.text(0.1, 0.875, "Student Responses:", transform=page.transFigure, bbox=dict(facecolor='blue', alpha=0.3), size=8, ha="left")
        for i in range(numResponses):
            page.text(0.15, 0.85-i*.05, str(responses[i]), transform=page.transFigure, bbox=dict(facecolor='green', alpha=0.2), size=7, ha="left")
        pdf.savefig()
        plt.close()
