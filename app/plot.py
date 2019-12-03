import datetime
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib
import matplotlib.pyplot as plt
import os
import pandas as pd
import statistics
import collections
import random

# Create the PdfPages object to which we will save the pages:
# The with statement makes sure that the PdfPages object is closed properly at
# the end of the block, even if an Exception occurs.

class PDFPlotter:
    """Class for generating plots"""
    def __init__(self, section):
        self.section = section
        # random int to avoid collisions when mutliple threads try to generate reports for the same section
        self.file = os.path.join('documents', 'course_{}_{}.pdf'.format(self.section.course_id, random.randint(1, 999999999)))
        self.createPDF()

    def peek_line(self, f):
        """Helper method to get the text of the next line without skipping it"""
        pos = f.tell()
        line = f.readline()
        f.seek(pos)
        return line

    def createPDF(self):
        """Creates a Multipage PDF"""
        data = []
        for result in self.section.results.all():
            data.append(list(result.response_data))
        df = pd.DataFrame.from_records(data)
        with PdfPages(self.file) as pdf:
            fp_questions = open(os.path.join('documents', 'survey_questions.txt'), 'r')
            fr_list = [4,5,11,15,19]
            self.createCover(pdf) # builds cover page for pdf
            figs = plt.figure(figsize=(10,10))
            graph_vals = []
            for i in (range(0, len(df.columns))):
                if i not in fr_list:
                    """Question is not a FRQ, so add it to the array of values to graph"""
                    graph_vals.append( df[i] )
                else:
                    """Hit free response, plot all subplots of non FRQ, plot free responses on the next page"""
                    if len(graph_vals) > 0:
                        self.generatePlots(pdf,fp_questions,graph_vals)
                        plt.subplots_adjust(left=.15, right=0.75, wspace=0.7, hspace=.25*len(graph_vals))
                        pdf.savefig(figs)
                        plt.close()

                        graph_vals = [] #reset histogram arguments
                        figs = plt.figure(figsize=(10,10))
                    self.generateFreeResponse(pdf, df[i], fp_questions.readline(), i)

            fp_questions.close()
            # We can also set the file's metadata via the PdfPages object:
            d = pdf.infodict()
            d['Title'] = '{}{} - {} Statistics'.format(self.section.subject, self.section.course_num, self.section.course_id)
            d['Author'] = 'SET++'
            d['Subject'] = d['Title']
            d['Keywords'] = '{}{} {}'.format(self.section.subject, self.section.course_num, self.section.course_id)
            d['CreationDate'] = datetime.datetime.today()
            d['ModDate'] = d['CreationDate']

    def createCover(self, pdf):
        """Method to create the cover page of the result pdf"""
        page = plt.figure(figsize=(10,10))
        page.clf()
        txt1 = 'SET++ Evaluation Statistics'
        txt2 = '{}{} - {}'.format(self.section.subject, self.section.course_num, self.section.course_id)
        page.text(0.5, 0.55, txt1, transform=page.transFigure, bbox=dict(facecolor='red', alpha=0.5), size=35, ha="center")
        page.text(0.5, 0.45, txt2, transform=page.transFigure, bbox=dict(facecolor='red', alpha=0.5), size=35, ha="center")
        pdf.savefig()
        plt.close()

    def generatePlots(self, pdf, questions, graph_vals):
        """Method to generate plots all on one page of PDF"""
        grid = len(graph_vals)*100+11
        for i in range(len(graph_vals)):
            question = questions.readline()
            ax = plt.subplot(grid+i)
            if "hours" in question:
                """generate barplot for questions involving time"""
                x = graph_vals[i].values
                counter = collections.Counter(x)
                label = [1.5,2.0,2.5,3.0,3.5]
                for l in label:
                    if l not in counter:
                        counter[l] = 0
                counter = sorted(counter.items(), key=lambda x:x[0])   #get frequency values of various choices

                scalars = [x[1] for x in counter]
                labels = [x[0] for x in counter]

                plt.bar(x=labels, height=scalars, width=0.3, tick_label=['<2','2','2.5','3','>3'], align='center')
                plt.xlabel('Time Spent (Hours)')

                txt = 'mean: {}\nmedian: {}\nN: {}'.format(round(statistics.mean(map(float, x)), 3), statistics.median(x), len(x))
                y_max = ax.get_ylim()[1]
                plt.text(4.25, y_max/2, txt,
                      bbox=dict(facecolor='red', alpha=0.5),
                      horizontalalignment='center',
                      verticalalignment='center')
            else:
                """Generate histogram for questions regarding rating"""
                x = list(pd.to_numeric(graph_vals[i]).values)
                plt.hist(x, rwidth=0.8, range=(1,5), bins=[0.5,1.5,2.5,3.5,4.5,5.5], density=True)
                plt.xlabel('Rating')

                # txt = "mean: "+str(round(statistics.mean(map(float, x) ), 3) ) + "\nmedian: "+str(statistics.median(x)) + "\nN: " + str(len(x))
                txt = 'mean: {}\nmedian: {}\n'.format(round(statistics.mean(map(float, x)), 3), statistics.median(x))
                if self.section.results.count() > 1:
                    txt += 'STD: {}\n'.format(round(statistics.stdev(map(float, x)), 3))
                txt += 'N: {}'.format(len(x))
                y_max = ax.get_ylim()[1]
                ax.text(6.5, y_max/2, txt,
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

    def deleteFile(self):
        """Delete the file after it has been sent to corresponding professor"""
        if os.path.exists(self.file):
            os.remove(self.file)
