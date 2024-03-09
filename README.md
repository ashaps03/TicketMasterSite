1) Clone github respository
2) Initialize the virtual environment for MacOS 
```
python3 -m venv .venv
```
3) Activate the venv
```
. .venv/bin/activate
```
4) Install dependencies
```
pip3 install -r requirements.txt
```
5) Create the develop database
```
python3 manage.py migrate
```
6: Run the dev server
```
python3 manage.py runserver
```
