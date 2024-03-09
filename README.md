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
6) Create your .env file
```
TICKET_MASTER_API_KEY = 'INSERT_API_KEY'
```
8) Run the dev server
```
python3 manage.py runserver
```
