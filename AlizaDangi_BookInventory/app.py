from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import json
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres:aesthetic0@localhost:5432/book_inventory"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Author(db.Model):
    __tablename__ = 'author'
    author_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    books = db.relationship('Book', backref='author', cascade="all, delete", lazy=True)

class Book(db.Model):
    __tablename__ = 'book'
    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.author_id'), nullable=False)

#  ROUTES 

@app.route("/")
def home():
    return {"message": "Bookstore API — use /authors or /books"}, 200

# AUTHORS 

# Add new author
@app.route('/authors', methods=['POST'])
def add_author():
    data = request.json
    new_author = Author(name=data['name'], email=data['email'])
    try:
        db.session.add(new_author)
        db.session.commit()
        return jsonify({"message": "Author added successfully"}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Author email already exists"}), 400

# Get all authors
@app.route('/authors', methods=['GET'])
def get_authors():
    authors = Author.query.all()
    return jsonify([{"id": a.author_id, "name": a.name, "email": a.email} for a in authors])

# Get author by ID
@app.route('/authors/<int:id>', methods=['GET'])
def get_author(id):
    author = Author.query.get_or_404(id)
    return jsonify({"id": author.author_id, "name": author.name, "email": author.email})

# Update author email
@app.route('/authors/<int:id>', methods=['PUT'])
def update_author(id):
    data = request.json
    author = Author.query.get_or_404(id)
    if "email" in data:
        author.email = data["email"]
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({"message": "Email already exists"}), 400
    return jsonify({"message": "Author email updated successfully"})

# Delete author (cascade deletes books)
@app.route('/authors/<int:id>', methods=['DELETE'])
def delete_author(id):
    author = Author.query.get_or_404(id)
    db.session.delete(author)
    db.session.commit()
    return jsonify({"message": "Author and their books deleted successfully"})

# ---------- BOOKS ----------

# Add new book
@app.route('/books', methods=['POST'])
def add_book():
    data = request.json
    new_book = Book(
        title=data['title'],
        price=data['price'],
        author_id=data['author_id']
    )
    db.session.add(new_book)
    db.session.commit()
    return jsonify({"message": "Book added successfully"}), 201

# Get all books with author info
@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    result = []
    for b in books:
        result.append({
            "id": b.book_id,
            "title": b.title,
            "price": b.price,
            "author": {"id": b.author.author_id, "name": b.author.name, "email": b.author.email}
        })
    return jsonify(result)

# Get book by ID
@app.route('/books/<int:id>', methods=['GET'])
def get_book(id):
    book = Book.query.get_or_404(id)
    return jsonify({
        "id": book.book_id,
        "title": book.title,
        "price": book.price,
        "author_id": book.author_id
    })

# Update book
@app.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    data = request.json
    book = Book.query.get_or_404(id)
    book.title = data.get("title", book.title)
    book.price = data.get("price", book.price)
    book.author_id = data.get("author_id", book.author_id)
    db.session.commit()
    return jsonify({"message": "Book updated successfully"})

# Delete book
@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted successfully"})

# ---------- DUMP DATA TO JSON ----------

# Dump books
@app.route('/dump/books', methods=['POST'])
def dump_books():
    books = Book.query.all()
    data = [{"id": b.book_id, "title": b.title, "price": b.price, "author_id": b.author_id} for b in books]
    os.makedirs("dumps", exist_ok=True)
    with open("dumps/books.json", "w") as f:
        json.dump(data, f, indent=4)
    return jsonify({"message": "Books dumped to dumps/books.json"})

# Dump authors
@app.route('/dump/authors', methods=['POST'])
def dump_authors():
    authors = Author.query.all()
    data = [{"id": a.author_id, "name": a.name, "email": a.email} for a in authors]
    os.makedirs("dumps", exist_ok=True)
    with open("dumps/authors.json", "w") as f:
        json.dump(data, f, indent=4)
    return jsonify({"message": "Authors dumped to dumps/authors.json"})

if __name__ == "__main__":
    app.run(debug=True)
