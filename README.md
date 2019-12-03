# SETpp
COEN174 SET++

Currently the Santa Clara University School of Engineering does not have a good way of administering student evaluations of teaching (SET) for lab sections because the questions are irrelevant to labs, which are often taught by one professor with multiple Teaching Assistants (TAs).
In this design report we present SET++, a web platform for the School of Engineering professors to get a better idea of how engineering lab teaching assistants are performing and helping students.
Our system allows an administrator to navigate to our website in a browser, login, and upload a student roster and create a survey session that will send out emails to all lab students with survey links for each individual students a set of questions to be sent to all engineering students that took a lab and have that data sent anonymously to a professor overseeing that lab section.
We designed and built this system over the quarter and have all of the functionality and error handling that is appropriate for this project.
The end result is a working web system that emails students their surveys and provides professors with organized detailed reports of their TAs' teaching performances.

INSTRUCTIONS
These instructions assume a Linux terminal (MacOSX, Ubuntu, etc.).1.

1.  Clone git repository onto your machine•git clone (https://github.com/ryanku98/SETpp.git)
2.  Install Python3/Ensure Python3 is installed (installation for Python3 varies by system)
3.  Create and source a virtual environment (optional)
        python3 -m venv venv
        source venv/bin/activate
4.  Install the necessary requirements
        pip3 install -r requirements.txt
5.  Run the application
        flask run
6.  Access the webpage through your browser•localhost:5000
