from flask import Flask, render_template, jsonify, make_response, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from os import environ
import requests
from forms import BookForm, MemberForm, ImportForm, IssueForm, SearchForm, ReturnForm, EditMemberForm, AddMoneyForm
from config import Config
from datetime import datetime

environ['FLASK_ENV'] = 'development'
app = Flask(__name__)
app.config.from_object(Config)
# Added Database URI without using environment variables due to local setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@flask_db:5432/postgres'

db = SQLAlchemy(app)


class Books(db.Model):
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    authors = db.Column(db.String(500), nullable=False)
    average_rating = db.Column(db.Float, nullable=False)
    isbn = db.Column(db.String(500), nullable=False)
    isbn13 = db.Column(db.String(500), nullable=False)
    language_code = db.Column(db.String(500), nullable=False)
    num_pages = db.Column(db.Integer, nullable=False)
    ratings_count = db.Column(db.Integer, nullable=False)
    text_reviews_count = db.Column(db.Integer, nullable=False)
    publication_date = db.Column(db.String(500), nullable=False)
    publisher = db.Column(db.String(500), nullable=False)
    total_count = db.Column(db.Integer, nullable=False, default=0)
    available_count = db.Column(db.Integer, nullable=False, default=0)
    rent_count = db.Column(db.Integer, nullable=False, default=0)

    def json(self):
        return {'book_id': self.book_id, 'title': self.title, 'authors': self.authors, 'average_rating': self.average_rating, 'isbn': self.isbn, 'isbn13': self.isbn13, 'language_code': self.language_code, 'num_pages': self.num_pages, 'ratings_count': self.ratings_count, 'text_reviews_count': self.text_reviews_count, 'publication_date': self.publication_date, 'publisher': self.publisher, 'total_count': self.total_count, 'available_count': self.available_count, 'rent_count': self.rent_count}


db.create_all()


class Members(db.Model):
    memberID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    email = db.Column(db.String(500), nullable=False)
    reg_date = db.Column(db.DateTime, nullable=False,
                         default=db.func.current_timestamp())
    total_books_rented = db.Column(db.Integer, nullable=False, default=0)
    debt = db.Column(db.Float, nullable=False, default=0)
    amount_paid = db.Column(db.Float, nullable=False, default=0)

    def json(self):
        return {'memberID': self.memberID, 'name': self.name, 'email': self.email, 'reg_date': self.reg_date, 'total_books_rented': self.total_books_rented, 'debt': self.debt, 'amount_paid': self.amount_paid}


db.create_all()


class Rent(db.Model):
    rentID = db.Column(db.Integer, primary_key=True)
    bookID = db.Column(db.Integer, db.ForeignKey(
        'books.book_id'), nullable=False)
    memberID = db.Column(db.Integer, db.ForeignKey(
        'members.memberID'), nullable=False)
    rent_date = db.Column(db.DateTime, nullable=False,
                          default=db.func.current_timestamp())
    return_date = db.Column(db.DateTime, nullable=True)
    amount_paid = db.Column(db.Float, nullable=False, default=0)
    total_amount = db.Column(db.Float, nullable=False, default=0)
    day_fee = db.Column(db.Float, nullable=False, default=0)

    def json(self):
        return {'rentID': self.rentID, 'bookID': self.bookID, 'memberID': self.memberID, 'rent_date': self.rent_date, 'return_date': self.return_date, 'amount_paid': self.amount_paid, 'total_amount': self.total_amount, 'day_fee': self.day_fee}


db.create_all()


@app.route('/test', methods=['GET'])
def test():
    return make_response(jsonify({'message': 'Test route works'}), 200)


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


@app.route('/search', methods=["POST"])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        search = form.search.data
        search = search.strip()
        books = Books.query.filter(Books.title.like(
            '%'+search+'%') | Books.authors.like('%'+search+'%')).all()
        if len(books) > 0:
            return render_template('books.html', books=books)
        else:
            return render_template('books.html', books=None)
    return render_template('books.html', form=form)


@app.route('/books', methods=["GET", "POST"])
def books():
    try:
        books = Books.query.order_by(Books.book_id).all()
        if len(books) > 0:
            return render_template('books.html', books=books)
        else:
            return render_template('books.html', books=None)
    except Exception as e:
        return render_template('500.html', error=str(e), code=500)


@app.route('/book/<int:id>', methods=["GET", "POST"])
def book(id):
    try:
        book = Books.query.filter_by(book_id=id).first()
        return render_template('book_detail.html', book=book)
    except Exception as e:
        return make_response(jsonify({'message': str(e)}), 500)


@app.route('/addbooks', methods=["GET", "POST"])
def addbook():
    try:
        form = BookForm()
        if form.validate_on_submit():
            new_book = Books(book_id=form.bookID.data, title=form.title.data, authors=form.authors.data, average_rating=form.average_rating.data, isbn=form.isbn.data, isbn13=form.isbn13.data, language_code=form.language_code.data, num_pages=form.num_pages.data,
                             ratings_count=form.ratings_count.data, text_reviews_count=form.text_reviews_count.data, publication_date=form.publication_date.data, publisher=form.publisher.data, total_count=form.total_count.data, available_count=form.total_count.data)
            db.session.add(new_book)
            db.session.commit()
            return redirect('/books')
        return render_template('addbook.html', form=form)
    except Exception as e:
        return render_template('500.html', error=str(e), code=500)


@app.route('/importBooks', methods=["GET", "POST"])
def importBooks():
    try:
        form = ImportForm()
        if form.validate_on_submit():
            url = 'https://frappe.io/api/method/frappe-library'
            title = form.title.data or ""
            authors = form.authors.data or ""
            isbn = form.isbn.data or ""
            publisher = form.publisher.data or ""
            no_of_books = form.number_of_books.data
            total_count = form.quantity_per_book.data
            books_imported = 0
            flag = True
            page = 1
            while (books_imported <= no_of_books):

                payload = {
                    "title": title,
                    "authors": authors,
                    "isbn": isbn,
                    "publisher": publisher,
                    "page": page
                }
                response = requests.get(url, params=payload)
                data = response.json()
                if len(data['message']) > 0:
                    for book in data['message']:
                        if books_imported >= no_of_books:
                            flag = False

                            break
                        # check if book already exists
                        book_exists = Books.query.filter_by(
                            book_id=book['bookID']).first()
                        if book_exists:
                            continue

                        new_book = Books(book_id=book['bookID'], title=book['title'], authors=book['authors'], average_rating=book['average_rating'], isbn=book['isbn'], isbn13=book['isbn13'], language_code=book['language_code'], num_pages=book['  num_pages'],
                                         ratings_count=book['ratings_count'], text_reviews_count=book['text_reviews_count'], publication_date=book['publication_date'], publisher=book['publisher'], total_count=total_count, available_count=total_count)

                        db.session.add(new_book)
                        db.session.commit()
                        books_imported += 1

                    if flag == False:
                        break
                    page += 1
                else:
                    break

            flash('New Books Added:' + str(books_imported))
            return redirect('/books')
        return render_template('importbooks.html', form=form)
    except Exception as e:
        return render_template('500.html', error=str(e), code=500)


@app.route('/editbook/<int:id>', methods=["GET", "POST"])
def editbook(id):
    try:
        book = Books.query.filter_by(book_id=id).first()
        form = BookForm()
        if form.validate_on_submit():
            book.title = form.title.data
            book.authors = form.authors.data
            book.average_rating = form.average_rating.data
            book.isbn = form.isbn.data
            book.isbn13 = form.isbn13.data
            book.language_code = form.language_code.data
            book.num_pages = form.num_pages.data
            book.ratings_count = form.ratings_count.data
            book.text_reviews_count = form.text_reviews_count.data
            book.publication_date = form.publication_date.data
            book.publisher = form.publisher.data
            book.total_count = form.total_count.data
            book.available_count = form.total_count.data
            db.session.commit()
            flash('Book Updated')
            return redirect('/books')
        return render_template('editbook.html', form=form, book=book)
    except Exception as e:
        return render_template('500.html', error=str(e), code=500)


@app.route('/deletebook/<int:id>', methods=["GET", "POST"])
def deletebook(id):
    try:
        book = Books.query.filter_by(book_id=id).first()
        db.session.delete(book)
        db.session.commit()
        flash('Book Deleted')
        return redirect('/books')
    except Exception as e:
        return render_template('500.html', error=str(e), code=500)


@app.route('/members', methods=["GET", "POST"])
def members():
    try:
        members = Members.query.order_by(Members.memberID).all()
        if len(members) > 0:
            return render_template('members.html', members=members)
        else:
            return render_template('members.html', members=None)
    except Exception as e:
        return render_template('500.html', error=str(e), code=500)


@app.route('/addmember', methods=["GET", "POST"])
def addmember():
    try:
        form = MemberForm()
        if form.validate_on_submit():
            new_member = Members(name=form.name.data, email=form.email.data)
            db.session.add(new_member)
            db.session.commit()

            flash('New Member Added')
            return redirect('/members')
        return render_template('addmembers.html', form=form)
    except Exception as e:
        return render_template('500.html', error=str(e), code=500)


@app.route('/editmember/<int:id>', methods=["GET", "POST"])
def editmember(id):
    try:
        member = Members.query.filter_by(memberID=id).first()
        form = EditMemberForm()
        if form.validate_on_submit():
            member.name = form.name.data
            member.email = form.email.data

            db.session.commit()
            flash('Member Updated')

            return redirect('/members')
        return render_template('editmember.html', form=form, member=member)
    except Exception as e:
        return render_template('500.html', error=str(e), code=500)


@app.route('/deletemember/<int:id>', methods=["GET", "POST"])
def deletemember(id):
    try:
        member = Members.query.filter_by(memberID=id).first()
        db.session.delete(member)
        db.session.commit()
        flash('Member Deleted')
        return redirect('/members')
    except Exception as e:
        return render_template('500.html', error=str(e), code=500)


@app.route('/addamount/<int:id>', methods=["GET", "POST"])
def addamount(id):
    try:
        member = Members.query.filter_by(memberID=id).first()
        form = AddMoneyForm()
        if form.validate_on_submit():
            member.amount_paid += form.amount.data
            if (member.debt - form.amount.data <= 0):
                member.debt = 0
                returning_amount = member.debt - form.amount.data
                if returning_amount < 0:
                    flash(
                        'Debt Cleared. Please return the remaining amount to the member i.e. ' + str(-returning_amount))

            else:
                member.debt = member.debt - form.amount.data
                flash('Amount Added')
            db.session.commit()
            return redirect('/members')
        return render_template('addamount.html', form=form, member=member)
    except Exception as e:
        return render_template('500.html', error=str(e), code=500)


@app.route('/transactions', methods=["GET", "POST"])
def transactions():
    try:
        transactions = Rent.query.all()
        if transactions:
            for transaction in transactions:
                transaction.rent_date = transaction.rent_date.replace(
                    tzinfo=None).date() if transaction.rent_date else None
                transaction.return_date = transaction.return_date.replace(
                    tzinfo=None).date() if transaction.return_date else None

        if len(transactions) > 0:
            return render_template('transactions.html', transactions=transactions)
        else:
            return render_template('transactions.html', transactions=None)
    except Exception as e:
        return make_response(jsonify({'message': str(e)}), 500)


@app.route('/issuebooks', methods=["GET", "POST"])
def issuebook():
    form = IssueForm()
    if form.validate_on_submit():
        book = Books.query.filter_by(book_id=form.bookID.data).first()
        if book is None:
            flash('Book not found')

            return render_template('issuebooks.html', form=form, message='Book not found')

        member = Members.query.filter_by(memberID=form.memberID.data).first()
        if member is None:
            flash('Member not found')
            return render_template('issuebooks.html', form=form, message='Member not found')
        if member.debt >= 500:
            flash(
                'Member has a debt of more than 500. Please clear the debt to rent a book.')
            return redirect('/transactions')

        elif book.available_count > 0:
            book.available_count -= 1
            book.rent_count += 1
            member.total_books_rented += 1
            rent = Rent(bookID=form.bookID.data,
                        memberID=form.memberID.data, day_fee=form.day_fee.data)
            db.session.add(rent)
            db.session.commit()
            flash('Book Issued')
            return redirect('/transactions')
        else:
            return render_template('issuebooks.html', form=form, message='Book not available')
    return render_template('issuebooks.html', form=form)


@app.route('/returnbook/<string:id>', methods=["GET", "POST"])
def returnbook(id):
    try:
        rent = Rent.query.filter_by(rentID=id).first()
        form = ReturnForm()
        per_day_fee = rent.day_fee
        borrowed_date = rent.rent_date.replace(tzinfo=None).date()
        days_borrowed = (datetime.now().date() - borrowed_date).days
        amount_due = per_day_fee * days_borrowed
        if form.validate_on_submit():
            book = Books.query.filter_by(book_id=rent.bookID).first()
            member = Members.query.filter_by(memberID=rent.memberID).first()
            book.available_count += 1
            member.total_books_rented -= 1
            member.amount_paid += form.amount_paid.data
            member.debt += amount_due - form.amount_paid.data
            rent.amount_paid = form.amount_paid.data
            rent.total_amount = amount_due
            rent.return_date = db.func.current_timestamp()
            if member.debt < 0:
                flash(
                    'Debt Cleared. Please return the remaining amount to the member i.e. ' + str(-member.debt))
                member.debt = 0
            elif member.debt == 0:
                flash('Debt Cleared')
            else:
                if member.debt >= 500:
                    flash(
                        'Member has a debt of more than 500. Please clear the debt to rent a book. Total Outstanding Debt: ' + str(member.debt))
                else:
                    flash('Amount Due: ' + str(member.debt))

            db.session.commit()
            return redirect('/transactions')
        return render_template('returnbook.html', form=form, amount_due=amount_due, days_borrowed=days_borrowed, rent=rent, per_day_fee=per_day_fee, borrowed_date=borrowed_date)
    except Exception as e:
        return render_template('500.html', error=str(e), code=500)


@app.route('/reports', methods=["GET", "POST"])
def reports():
    try:
        books = Books.query.order_by(Books.rent_count.desc()).limit(5).all()
        members = Members.query.order_by(
            Members.amount_paid.desc()).limit(5).all()
        transactions = Rent.query.order_by(
            Rent.rent_date.desc()).limit(5).all()

        return render_template('reports.html', books=books, members=members, transactions=transactions)
    except Exception as e:
        return make_response(jsonify({'message': str(e)}), 500)


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['MESSAGE_FLASHING_OPTIONS'] = {'duration': 5}
    app.run(debug=True, port=4000, host='0.0.0.0')
