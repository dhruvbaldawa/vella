from flask_wtf import Form
from wtforms import TextField, DecimalField, PasswordField, BooleanField
from wtforms.validators import Optional, Required


class LoginForm(Form):
    username = TextField('username', validators=[Required()])
    password = PasswordField('password', validators=[Required()])


class LogForm(Form):
    kind = TextField('kind', validators=[Required()])
    source = TextField('source', validators=[Required()])
    timestamp = DecimalField('timestamp', validators=[Optional()])
    description = TextField('description', validators=[Optional()])
    other = TextField('other', validators=[Optional()])


class EventForm(Form):
    event = TextField('event', validators=[Required()])
    timestamp = DecimalField('timestamp', validators=[Optional()])
    active = BooleanField('active', default=True,
                          false_values=('false', 'False', ''),
                          validators=[Optional()])
    other = TextField('other', validators=[Optional()])
