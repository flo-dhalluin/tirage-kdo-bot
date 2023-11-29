from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SelectMultipleField

class PersonForm(FlaskForm):
    name = StringField()
    email = EmailField()
    avoids = SelectMultipleField(coerce=int)

