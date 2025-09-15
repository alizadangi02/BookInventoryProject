from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import json
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres:aesthetic0@localhost:5432/book_inventory"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Author Model
class Author(db.Model):
    __tablename__ = 'author'
    author_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True)
    books = db.relationship('Book', backref='author', cascade="all, delete", lazy=True)

# Book Model
class Book(db.Model):
    __tablename__ = 'book'
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.author_id'))


#  API Routes 

# Add Author
@app.route('/authors', methods=['POST'])
def add_author():
    data = request.json
    new_author = Author(name=data['name'], email=data['email'])
    db.session.add(new_author)
    db.session.commit()
    return jsonify({"message": "Author added successfully"}), 201

# Get All Authors
@app.route('/authors', methods=['GET'])
def get_authors():
    authors = Author.query.all()
    return jsonify([{"id": a.author_id, "name": a.name, "email": a.email} for a in authors])

# Get Author by ID
@app.route('/authors/<int:id>', methods=['GET'])
def get_author(id):
    author = Author.query.get_or_404(id)
    return jsonify({"id": author.author_id, "name": author.name, "email": author.email})

# Add Book
@app.route('/books', methods=['POST'])
def add_book():
    data = request.json
    new_book = Book(title=data['title'], price=data['price'], author_id=data['author_id'])
    db.session.add(new_book)
    db.session.commit()
    return jsonify({"message": "Book added successfully"}), 201

# Get All Books with Author Info
@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    result = []
    for b in books:
        result.append({
            "id": b.book_id,
            "title": b.title,
            "price": b.price,
            "author": {"id": b.author.author_id, "name": b.author.name}
        })
    return jsonify(result)

# Get Book by ID
@app.route('/books/<int:id>', methods=['GET'])
def get_book(id):
    b = Book.query.get_or_404(id)
    return jsonify({"id": b.book_id, "title": b.title, "price": b.price, "author_id": b.author_id})

# Update Book
@app.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    data = request.json
    book = Book.query.get_or_404(id)
    book.price = data.get("price", book.price)
    db.session.commit()
    return jsonify({"message": "Book updated successfully"})

# Update Author Email
@app.route('/authors/<int:id>', methods=['PUT'])
def update_author(id):
    data = request.json
    author = Author.query.get_or_404(id)
    author.email = data.get("email", author.email)
    db.session.commit()
    return jsonify({"message": "Author email updated successfully"})

# Delete Book
@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted successfully"})

# Delete Author (Cascade Deletes Books)
@app.route('/authors/<int:id>', methods=['DELETE'])
def delete_author(id):
    author = Author.query.get_or_404(id)
    db.session.delete(author)
    db.session.commit()
    return jsonify({"message": "Author and their books deleted successfully"})

# Dump Books to JSON
@app.route('/dump/books', methods=['POST'])
def dump_books():
    books = Book.query.all()
    data = [{"id": b.book_id, "title": b.title, "price": b.price, "author_id": b.author_id} for b in books]
    with open("books.json", "w") as f:
        json.dump(data, f, indent=4)
    return jsonify({"message": "Books dumped to books.json"})

# Dump Authors to JSON
@app.route('/dump/authors', methods=['POST'])
def dump_authors():
    authors = Author.query.all()
    data = [{"id": a.author_id, "name": a.name, "email": a.email} for a in authors]
    with open("authors.json", "w") as f:
        json.dump(data, f, indent=4)
    return jsonify({"message": "Authors dumped to authors.json"})


if __name__ == "__main__":
    app.run(debug=True) 
