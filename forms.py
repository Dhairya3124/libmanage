from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, validators
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
class BookForm(FlaskForm):
    bookID = StringField('Book ID', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    authors = StringField('Authors', validators=[DataRequired()])
    average_rating = StringField('Average Rating', validators=[DataRequired()])
    isbn = StringField('ISBN', validators=[DataRequired()])
    isbn13 = StringField('ISBN13', validators=[DataRequired()])
    language_code = StringField('Language Code', validators=[DataRequired()])
    num_pages = StringField('Number of Pages', validators=[DataRequired()])
    ratings_count = StringField('Ratings Count', validators=[DataRequired()])
    text_reviews_count = StringField('Text Reviews Count', validators=[DataRequired()])
    publication_date = StringField('Publication Date', validators=[DataRequired()])
    publisher = StringField('Publisher', validators=[DataRequired()])
    total_count = StringField('Total Count', validators=[DataRequired()])
    submit = SubmitField('Add Book')
class MemberForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Add Member')
class EditMemberForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Edit Member')
class AddMoneyForm(FlaskForm):
    amount = IntegerField('Amount', validators=[DataRequired()])
    submit = SubmitField('Add Money')

class ImportForm(FlaskForm):
    number_of_books = IntegerField('No. of Books*', [validators.NumberRange(min=1)])
    quantity_per_book = IntegerField(
        'Quantity Per Book*', [validators.NumberRange(min=1)])
    title = StringField(
        'Title', [validators.Optional(), validators.Length(min=2, max=255)])
    authors = StringField(
        'Author(s)', [validators.Optional(), validators.Length(min=2, max=255)])
    isbn = StringField(
        'ISBN', [validators.Optional(), validators.Length(min=10, max=10)])
    publisher = StringField(
        'Publisher', [validators.Optional(), validators.Length(min=2, max=255)])
    submit = SubmitField('Import Data')
class IssueForm(FlaskForm):
    memberID = StringField('Member ID', validators=[DataRequired()])
    bookID = StringField('Book ID', validators=[DataRequired()])
    day_fee = IntegerField('Day Fee', validators=[DataRequired()])
    
    submit = SubmitField('Issue Book')
class SearchForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')

class ReturnForm(FlaskForm):
    amount_paid = IntegerField('Amount Paid', validators=[DataRequired()])