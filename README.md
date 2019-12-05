# SETpp
COEN174 SET++

Currently the Santa Clara University School of Engineering does not have an effective way of administering student evaluations of teaching (SET) for lab sections.
This is because the questions are irrelevant to labs, which are often taught by one professor with multiple Teaching Assistants (TAs).
In this design report we present SET++, a SET web platform designed specifically for the School of Engineering, suited for generating feedback for Engineering lab sections.
We designed and built this system over the quarter and have accounted for functionality and error handling requirements.
The end result is a working web system that emails students their surveys and provides professors with organized detailed reports of the effectiveness of their lab sections.
We recommend that this system be used by the School of Engineering.

INSTRUCTIONS

These instructions assume a Linux terminal (MacOSX, Ubuntu, etc.).

1. Clone git repository onto your machine
```bash
git clone (https://github.com/ryanku98/SETpp.git)
```
2. Install Python3/Ensure Python3 is installed (installation for Python3 varies by system)
3. Create and source a virtual environment (optional)
```bash
python3 -m venv venv
source venv/bin/activate
```
4. Install the necessary requirements
```bash
pip3 install -r requirements.txt
```
5. Setup database
```bash
flask db init
flask db migrate
flask db upgrade
```
6. Run the application
```bash
flask run
```
7. Access the webpage through your browser
```
localhost:5000/
```
