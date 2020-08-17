from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField, SelectField, RadioField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length, NumberRange
from wtforms.fields.html5 import IntegerRangeField
from wtforms.fields import html5 as h5fields
from wtforms.widgets import html5 as h5widgets
from app.models import User

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please select a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please select a different username.')


class CreateCharacter(FlaskForm):
    character_name = StringField('Name', validators=[DataRequired()])
    character_class = SelectField('Class', coerce=int)
    #level = IntegerField('Level', validators=[DataRequired()])
    charm = SelectField('Charm', choices = [(-1, '-1'), (0, '0'), (1, '1'), (2, '2'), (3, '3')], default=0, coerce=int)
    cool = SelectField('Cool', choices = [(-1, '-1'), (0, '0'), (1, '1'), (2, '2'), (3, '3')], default=0, coerce=int)
    sharp = SelectField('Sharp', choices = [(-1, '-1'), (0, '0'), (1, '1'), (2, '2'), (3, '3')], default=0, coerce=int)
    tough = SelectField('Tough', choices = [(-1, '-1'), (0, '0'), (1, '1'), (2, '2'), (3, '3')], default=0, coerce=int)
    weird = SelectField('Weird', choices = [(-1, '-1'), (0, '0'), (1, '1'), (2, '2'), (3, '3')], default=0, coerce=int)
    submit = SubmitField('Save')

class ViewCharacter(FlaskForm):
    harm_radio = RadioField('Harm', choices=[(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '7')], coerce=int, id='harm_radio')
    luck_radio = RadioField('Luck', choices=[(7, '7'), (6, '6'), (5, '5'), (4, '4'), (3, '3'), (2, '2'), (1, '1'), (0, '0')], coerce=int)
    #luck_int = h5fields.IntegerField('Luck', widget=h5widgets.NumberInput(min=0, max=7, step=1))
    experience = h5fields.IntegerField('Experience', widget=h5widgets.NumberInput(min=0, max=5, step=1))
    submit = SubmitField('Save Changes')

class AddItem(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    tags = StringField('Tags')
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=1, max=128)])
    submit = SubmitField('Add Item')

class AddImprovement(FlaskForm):
    improvement = SelectField('Improvement', coerce=int)
    submit = SubmitField('Add')

class AddCharacterNote(FlaskForm):
    note = TextAreaField('Character Note', validators=[Length(min=0, max=256)])
    submit = SubmitField('Submit')

class AddMove(FlaskForm):
    new_move = SelectMultipleField('Move', coerce = int)
    submit = SubmitField('Add')

class LevelUp(FlaskForm):
    improvement = SelectField('Improvement', coerce=int, validators=[NumberRange(min=1, message="You must select an improvement")])
    new_move = SelectField('Move', coerce = int)
    submit = SubmitField('Save')

    def validate(self):
        #triggers the regular validation
        if not super(LevelUp, self).validate():
            return False
        #add custom validation here
        if self.improvement.data == 1 and self.new_move.data == 0:
            self.new_move.errors.append("You must choose a move")
            return False
        #return true if default and custom validation don't trigger an error
        return True