# ACTIVATE VIRTUAL ENVIROMENT
source .venv/bin/activate --> mac / linux
.venv\Scripts\activate.bat --> windows

# RUN FLASK
export FLASK_APP=app.py
export FLASK_ENV=development
flask run 

flask --app app run --debug

# INSTALL PACKAGES
python -m pip install [package]
