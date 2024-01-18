from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Book(db.Model, SerializerMixin):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False, unique=True)
    page_count = db.Column(db.Integer, nullable=False)
    publisher_id = db.Column(db.Integer, db.ForeignKey("publishers.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"))

    publisher = db.relationship("Publisher", back_populates="books")
    author = db.relationship("Author", back_populates="books")

    def author_name(self):
        return self.author.name

    def publisher_name(self):
        return self.publisher.name

    serialize_rules = (
        "-publisher",
        "-author",
        "-publisher_id",
        "-author_id",
        "author_name",
        "publisher_name",
    )

    @validates("title")
    def validate_title(self, _, title):
        if not title:
            raise ValueError("must have a title.")
        book = Book.query.filter_by(title=title).first()
        if book and book != self:
            raise ValueError("must have a unique title.")
        return title

    @validates("page_count")
    def validate_title_page_count(self, _, page_count):
        if not isinstance(page_count, int) or page_count < 1:
            raise ValueError("must have a positive page count.")
        return page_count

    @validates("author_id")
    def validate_author_id(self, _, author_id):
        author = Author.query.get(author_id)
        if not author:
            raise ValueError("must belong to an existing author.")
        return author_id

    @validates("publisher_id")
    def validate_publisher_id(self, _, publisher_id):
        publisher = Publisher.query.get(publisher_id)
        if not publisher:
            raise ValueError("must belong to an existing publisher.")
        return publisher_id


class Publisher(db.Model, SerializerMixin):
    __tablename__ = "publishers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    founding_year = db.Column(db.Integer, nullable=False)

    books = db.relationship(
        "Book", cascade="all, delete-orphan", back_populates="publisher"
    )

    authors = association_proxy("books", "author")

    serialize_rules = ("-books",)

    @validates("name")
    def validate_name(self, _, name):
        if not name:
            raise ValueError("must have a name.")
        return name

    @validates("founding_year")
    def validate_founding_year(self, _, founding_year):
        if founding_year not in range(1600, datetime.now().year + 1):
            raise ValueError("must have a founding year between 1600 and now.")
        return founding_year


class Author(db.Model, SerializerMixin):
    __tablename__ = "authors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    pen_name = db.Column(db.String)

    books = db.relationship(
        "Book", cascade="all, delete-orphan", back_populates="author"
    )

    publishers = association_proxy("books", "publisher")

    serialize_rules = ("-books",)

    @validates("name")
    def validate_name(self, _, name):
        if not name:
            raise ValueError("must have a name.")
        return name
