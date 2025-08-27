from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    FloatField,
    DateField,
    SubmitField,
    SelectField,
)
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError
from models import Client


class LoginForm(FlaskForm):
    username = StringField("Usuario", validators=[DataRequired(), Length(max=80)])
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(min=4, max=80)])
    submit = SubmitField("Entrar")


class ClientForm(FlaskForm):
    name = StringField("Nombre", validators=[DataRequired(), Length(max=100)])
    document = StringField("Documento", validators=[DataRequired(), Length(max=100)])
    address = StringField("Dirección", validators=[Length(max=200)])
    phone = StringField("Teléfono", validators=[Length(max=20)])
    submit = SubmitField("Guardar")

    def validate_document(self, field):
        if Client.query.filter_by(document=field.data).first():
            raise ValidationError("Documento ya registrado")


class DebtForm(FlaskForm):
    date = DateField("Fecha", validators=[DataRequired()], format="%Y-%m-%d")
    amount = FloatField("Monto", validators=[DataRequired(), NumberRange(min=0)])
    description = StringField("Descripción", validators=[DataRequired(), Length(max=200)])
    submit = SubmitField("Agregar deuda")


class DebtClientForm(FlaskForm):
    client_id = SelectField("Cliente", coerce=int, validators=[DataRequired()])
    date = DateField("Fecha", validators=[DataRequired()], format="%Y-%m-%d")
    amount = FloatField("Monto", validators=[DataRequired(), NumberRange(min=0)])
    description = StringField("Descripción", validators=[DataRequired(), Length(max=200)])
    submit = SubmitField("Agregar deuda")


class PaymentForm(FlaskForm):
    date = DateField("Fecha", validators=[DataRequired()], format="%Y-%m-%d")
    amount = FloatField("Monto", validators=[DataRequired(), NumberRange(min=0)])
    method = SelectField(
        "Método",
        choices=[
            ("cash", "Efectivo"),
            ("transfer", "Transferencia"),
            ("other", "Otros"),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField("Agregar pago")


class WithdrawalForm(FlaskForm):
    amount = FloatField("Monto", validators=[DataRequired(), NumberRange(min=0)])
    description = StringField("Descripción", validators=[Length(max=200)])
    submit = SubmitField("Retirar")


class IncomeForm(FlaskForm):
    amount = FloatField("Monto", validators=[DataRequired(), NumberRange(min=0)])
    description = StringField("Descripción", validators=[Length(max=200)])
    submit = SubmitField("Ingresar")
