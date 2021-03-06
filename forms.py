from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField
from wtforms.validators import DataRequired, Length, EqualTo

class BS_CreatePage(FlaskForm):
    private_subnet = StringField('Private Subnet (CIDR)', validators=[DataRequired()])
    web_subnet = StringField('Web Subnet (CIDR)', validators=[DataRequired()])
    db_subnet = StringField('DB Subnet (CIDR)', validators=[DataRequired()])
    business_subnet = StringField('Business Subnet (CIDR)', validators=[DataRequired()])

    pahostname1 = StringField('PA1 Hostname', validators=[DataRequired()])
    papublicip1 = StringField('PA1 Public Subnet (rfc 1918) IP', validators=[DataRequired()])
    papublicnexthop1 = StringField('PA1 Public Next Hop Gateway IP', validators=[DataRequired()])
    paprivateip1 = StringField('PA1 Private IP', validators=[DataRequired()])
    paprivatenexthop1 = StringField('PA1 Private Next Hop Gateway IP', validators=[DataRequired()])

    pahostname2 = StringField('PA2 Hostname', validators=[DataRequired()])
    papublicip2 = StringField('PA2 Public Subnet (rfc 1918) IP', validators=[DataRequired()])
    papublicnexthop2 = StringField('PA2 Public Next Hop Gateway IP', validators=[DataRequired()])
    paprivateip2 = StringField('PA2 Private IP', validators=[DataRequired()])
    paprivatenexthop2 = StringField('PA2 Private Next Hop Gateway IP', validators=[DataRequired()])

    storage_account_name = StringField('Azure Storage Account Name', default="cnetpalopublic", validators=[DataRequired()])
    storage_folder_name = StringField('Azure Storage Folder Name', validators=[DataRequired()])
    storage_access_key = StringField('Azure Storage Access Key', validators=[DataRequired()])
    submit = SubmitField('Build Bootstrap File')