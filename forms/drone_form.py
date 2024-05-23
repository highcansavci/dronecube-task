from wtforms import Form, StringField, FloatField, validators
from wtforms.validators import DataRequired, NumberRange


class DroneForm(Form):
    name = StringField("name", validators=[DataRequired()])
    latitude = FloatField("latitude", validators=[DataRequired(), NumberRange(min=-90, max=90)])
    longitude = FloatField("longitude", validators=[DataRequired(), NumberRange(min=-180, max=180)])
    altitude = FloatField("altitude", validators=[DataRequired()])
    home_latitude = FloatField("home_latitude", validators=[DataRequired(), NumberRange(min=-90, max=90)])
    home_longitude = FloatField("home_longitude", validators=[DataRequired(), NumberRange(min=-180, max=180)])
    home_altitude = FloatField("home_altitude", validators=[DataRequired()])
    velocity_x = FloatField("velocity_x", validators=[DataRequired()])
    velocity_y = FloatField("velocity_y", validators=[DataRequired()])
    velocity_z = FloatField("velocity_z", validators=[DataRequired()])
    connected = StringField("connected", validators=[DataRequired(), validators.Regexp(r'(Connected|Not Connected)')])
