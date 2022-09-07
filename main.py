from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy import desc
from wtforms import StringField, SubmitField, validators, FloatField
from wtforms.validators import DataRequired
import requests
from markupsafe import escape
import requests

API_KEY = 'YOUR_KEY'

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

##CREATE DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movie-collection.db"
# Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CREATE TABLE
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(255), nullable=True)
    img_url = db.Column(db.String(255), nullable=False)

    # Optional: this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return f'<Book {self.title}>'


class RateMovieForm(FlaskForm):
    rating = FloatField('rating', [validators.data_required()])
    review = StringField('Review', [validators.Length(min=6, max=20), validators.data_required()])

    submit = SubmitField('submit')


class AddMovieForm(FlaskForm):
    title = StringField('Title', [validators.data_required()])

    submit = SubmitField('submit')


# db.create_all()
# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
# db.session.add(new_movie)
# db.session.commit()

@app.route("/")
def home():
    all_movies = db.session.query(Movie).order_by(desc("rating"))
    return render_template("index.html", all_movies=all_movies)


@app.route("/add", methods=["GET", "POST"])
def add():
    add_movie_form = AddMovieForm()

    if add_movie_form.validate_on_submit() and request.method == 'POST':
        API_LINK = f'https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={add_movie_form.title.data}'
        api_data_recieved = requests.get(API_LINK).json()
        # print(api_data_recieved)
        return render_template("select.html", all_movies_from_api=api_data_recieved)

    else:
        return render_template("add.html", add_movie_form=add_movie_form)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    movie_name = request.args.get('movie_name')
    form = RateMovieForm()
    if form.validate_on_submit() and request.method == 'POST':
        movie = Movie.query.filter_by(title=movie_name).first()
        movie.rating = form.rating.data
        movie.review = form.review.data
        db.session.commit()
        print(form.rating.data)
        return redirect(url_for("home"))
    return render_template("edit.html", form=form, movie_name=movie_name)


@app.route("/select", methods=["GET", "POST"])
def select():
    # new_movie = Movie(
    #     title=movie_details['original_title'],
    #     year=movie_details['release_date'].split('-')[0],
    #     description=movie_details['original_title'],
    #     rating=7.3,
    #     ranking=10,
    #     review="My favourite character was the caller.",
    #     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
    # )
    # print(movie_details)
    movie_id = request.args.get('movie_id')
    if movie_id:
        form = RateMovieForm()
        API_LINK = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}'
        movie_details = requests.get(API_LINK).json()
        print(movie_details)
        new_movie = Movie(
            title=movie_details['original_title'],
            year=movie_details['release_date'].split('-')[0],
            description=movie_details['overview'],
            rating="{:.1f}".format(float(movie_details['vote_average'])),
            img_url=f"http://image.tmdb.org/t/p/w500{movie_details['poster_path']}"
        )
        db.session.add(new_movie)
        db.session.commit()
    # return render_template("edit.html", form=form, movie_name=movie_details['original_title'])
    return redirect(url_for("edit", movie_name=movie_details['original_title']))


@app.route("/delete")
def delete():
    movie_name = request.args.get('movie_name')
    movie_to_delete = Movie.query.filter_by(title=movie_name).first()
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(debug=True)
