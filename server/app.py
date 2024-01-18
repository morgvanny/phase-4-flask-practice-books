#!/usr/bin/env python3


from flask import Flask, make_response, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import Author, Book, Publisher, db  # import your models here!

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.get("/")
def index():
    return "Hello world"


class AuthorById(Resource):
    def get(self, id):
        author = Author.query.get(id)
        if author:
            return make_response(author.to_dict(rules=("books",)), 200)
        else:
            return make_response({"error": "Author not found"}, 404)

    def delete(self, id):
        author = Author.query.get(id)
        if author:
            db.session.delete(author)
            db.session.commit()
            return make_response({}, 204)
        else:
            return make_response({"error": "Author not found"}, 404)


class Books(Resource):
    def get(self):
        return make_response([book.to_dict() for book in Book.query.all()], 200)

    def post(self):
        data = request.get_json()
        try:
            book = Book(
                title=data.get("title"),
                author_id=data.get("author_id"),
                publisher_id=data.get("publisher_id"),
                page_count=data.get("page_count"),
            )
            db.session.add(book)
            db.session.commit()
            return make_response(book.to_dict(), 201)
        except ValueError as e:
            return make_response({"error": e.__str__()}, 400)


class PublisherById(Resource):
    def get(self, id):
        publisher = Publisher.query.get(id)
        if publisher:
            return make_response(publisher.to_dict(rules=("authors",)), 200)
        else:
            return make_response({"error": "Publisher not found"}, 404)


api.add_resource(Books, "/books")
api.add_resource(AuthorById, "/authors/<int:id>")
api.add_resource(PublisherById, "/publishers/<int:id>")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
