from wtforms import Form, StringField, DateTimeLocalField, validators
from wtforms.fields.numeric import IntegerField
from wtforms.validators import DataRequired, NumberRange


class TaskForm(Form):
    title = StringField("title", validators=[DataRequired()])
    date = DateTimeLocalField("date", validators=[DataRequired()])
    completed = StringField("completed", validators=[DataRequired(), validators.Regexp(r'(Completed|Not Completed)')])
    drone_id = IntegerField("drone_id", validators=[DataRequired(), NumberRange(min=1)])
