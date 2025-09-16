CREATE TABLE authors (
    author_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(100)
);


CREATE TABLE books (
    book_id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    genre VARCHAR(100),
    author_id INT REFERENCES authors(author_id)
);


INSERT INTO authors (name, country) VALUES ('George Orwell', 'UK');
INSERT INTO books (title, author_id, genre) VALUES ('1984', 1, 'fiction');


SELECT * FROM authors;
SELECT * FROM books;