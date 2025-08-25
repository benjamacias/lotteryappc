from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange


class LoginForm(FlaskForm):
    username = StringField("Usuario", validators=[DataRequired(), Length(max=80)])
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(min=4, max=80)])
    submit = SubmitField("Entrar")


class ClientForm(FlaskForm):
    name = StringField("Nombre", validators=[DataRequired(), Length(max=100)])
    document = StringField("Documento", validators=[DataRequired(), Length(max=100)])
    submit = SubmitField("Guardar")


class DebtForm(FlaskForm):
    date = DateField("Fecha", validators=[DataRequired()], format="%Y-%m-%d")
    amount = FloatField("Monto", validators=[DataRequired(), NumberRange(min=0)])
    description = StringField("Descripción", validators=[DataRequired(), Length(max=200)])
    submit = SubmitField("Agregar deuda")


class PaymentForm(FlaskForm):
    date = DateField("Fecha", validators=[DataRequired()], format="%Y-%m-%d")
    amount = FloatField("Monto", validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField("Agregar pago")
