import datetime
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import os
import subprocess
from survey import Section, fr_ids
import pandas as pd




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
        print(self.file)
        os.remove(self.file)
        with PdfPages(self.file) as pdf:
            fp_questions = open(questions_path, 'r')
            for i in range(2, len(self.section.data[0])):
                line = fp_questions.readline() # read line of questions file
                if i not in fr_ids:
                    x = pd.to_numeric(self.section.df[i])
                    self.generatePlot(pdf,line,x)
                    self.generateStatistics(pdf,x)
                else:
                    self.generateFreeResponse(pdf)
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

    def generatePlot(self, pdf, question, x):
        fig = plt.figure(figsize=(8, 6))
        plt.hist(x.values, bins=[1,2,3,4,5], density=True)
        plt.title("Question: "+question)
        pdf.savefig()  # saves the current figure into a pdf page
        plt.close()

    def generateStatistics(self, pdf, x):
        # if LaTeX is not installed or error caught, change to `usetex=False`
        firstPage = plt.figure(figsize=(8,6))
        firstPage.clf()
        txt = 'Statistics:'
        firstPage.text(0.25,0.5,txt, transform=firstPage.transFigure, size=24, ha="center")
        txt = 'Mean: '+str(x.mean())
        firstPage.text(0.25,0.4,txt, transform=firstPage.transFigure, size=16, ha="center")
        pdf.savefig()
        plt.close()

    def generateFreeResponse(self, pdf):
        numResponses = len(self.section.fr_list)
        print(numResponses)
        page = plt.figure(figsize=(8,6))
        page.clf()
        for i in range(numResponses):
            page.text(0.1,(0.5-float(i/20)), str(self.section.fr_list), transform=page.transFigure, size=10, ha="left")
        pdf.savefig()
        plt.close()




# data = [['eejohnson@scu.edu',83505,1,1,1,1,'asdf','asdf',1,1,1,1,1,'asdf',1,3,1,'asdf',2.5,2.5,2.5,'asdf'],
# ['eejohnson@scu.edu',83505,2,1,1,1,'asdf','asdf',1,1,1,5,1,'asdf',1,1,1,'asdf',2.5,2.5,2.5,'asdf'],
# ['eejohnson@scu.edu',83505,2,1,3,3,'asdf','asdf',1,1,4,1,1,'asdf',1,2,1,'asdf',2.5,2.5,2.5,'asdf'],
# ['eejohnson@scu.edu',83505,2,1,3,3,'asdf','asdf',1,1,4,1,1,'asdf',1,1,1,'asdf',2.5,3,2.5,'asdf']]
# section = Section(83505, data)
# section.get_section_stats()
