# Travel Planning Platform Web Project
This is a Django project to build a travel planning platform, created by Group W10, who studied the Web Design course at FengChia University, Taiwan.

# Install and Run
## Set up Python environment
### For Windows:
```
python -m venv django_project
```
In the same directory, run the script in terminal
```
./django_project/Scripts/Activate
```
or run the following script in CMD instead
```
.\django_project\Scripts\Activate.bat
```
Make sure you have done the actions above to get into virtual environment, you will see something like `(django_project) C:\<Your Path>...` in your terminal or CMD.

Next, install the required packages.
```
cd travel_planning
pip install -r requirements.txt
```
Finally, run
```
python manage.py runserver
```
The default url will be `127.0.0.1:8000/`


### For Linux/macOS
```
python3 -m venv django_project
```
In the same directory, run the script in terminal
```
source ./django_project/bin/activate
```
Make sure you have done the actions above to get into virtual environment, you will see something like `(django_project) <Your Path>...%` in your terminal.

Next, install the required packages.
```
cd HahaLife
pip3 install -r requirements.txt
```
Finally, run
```
python3 manage.py runserver
```
The default url will be `127.0.0.1:8000/`
