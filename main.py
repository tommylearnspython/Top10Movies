import sqlalchemy
from sqlalchemy import desc
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

API_KEY = "189e0884fa31fa4d9a6941322a37f3d5"
TMDB_URL ="https://api.themoviedb.org/3/search/movie"
SEARCH_API_URL = "https://api.themoviedb.org/3/movie"


app = Flask(__name__)
app.app_context().push()
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///top-10-movies.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



class edit_rating_Form(FlaskForm):
    new_rating = StringField(label="Your Rating out of 10 (ex: 7.5)", validators=[DataRequired()])
    new_review = StringField(label="Your Review", validators=[DataRequired()])
    submit = SubmitField('Done')

class Add_Form(FlaskForm):
    title = StringField('Movie title', validators=[DataRequired()])
    submit = SubmitField('Add Movie')

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, unique=False, nullable=False)
    description = db.Column(db.String(250), unique=False, nullable=False)
    rating = db.Column(db.Integer, unique=False, nullable=True)
    ranking = db.Column(db.Integer, unique=True, nullable=True)
    review = db.Column(db.String(250), unique=False, nullable=False)
    img_url = db.Column(db.String(250), unique=False, nullable=False)

    def __repr__(self):
        return f'<Books {self.title}>'


db.create_all()

new_movie = Movie(
    title="Phone Booth",
    year=2002,
    description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
    rating=7.3,
    ranking=10,
    review="My favourite character was the caller.",
    img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
)

#db.session.add(new_movie)
db.session.commit()

@app.route("/", methods=['GET', 'POST'])
def home():
    all_movies = db.session.query(Movie).order_by("rating").all()
    for index, movie in enumerate(all_movies):
        movie.ranking = len(all_movies)-index
    return render_template("index.html", all_movies=all_movies)

@app.route('/edit', methods=['GET','POST'])
def edit():
    movie_id = request.args.get('id')
    movie=Movie.query.get(movie_id)
    edit_form = edit_rating_Form()
    if edit_form.validate_on_submit():
        movie.rating=edit_form.data['new_rating']
        movie.review=edit_form.data['new_review']
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie, form=edit_form)

@app.route("/delete", methods=['GET','POST'])
def delete():
    movie_id = request.args.get('id')
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/add', methods=['GET','POST'])
def add():
    add_form = Add_Form()
    if add_form.validate_on_submit():
        parameters = {
            "api_key": API_KEY,
            "query": add_form.data.get('title')
        }
        response = requests.get(url=TMDB_URL, params=parameters)
        response.raise_for_status()
        movie_data = response.json()
        movie_list = movie_data['results']
        return render_template('select.html', movies=movie_list)
    return render_template('add.html', form=add_form)

@app.route('/new_movie', methods=['GET', 'POST'])
def new_movie():
    api_movie_id = request.args.get('movie_id')
    parameters = {
        "api_key": API_KEY,
    }
    response = requests.get(url=f"{SEARCH_API_URL}/{api_movie_id}", params=parameters)
    response.raise_for_status()
    movie_data = response.json()
    new_movie = Movie(
        title=movie_data['title'],
        year=movie_data['release_date'][:4],
        description=movie_data['overview'],
        review="My favourite character was the caller.",
        img_url=f"https://image.tmdb.org/t/p/w500{movie_data['backdrop_path']}"
    )
    db.session.add(new_movie)
    db.session.commit()
    movie_title = new_movie.title
    print(movie_title)
    movie_db = Movie.query.filter_by(title=movie_title).first()
    movie_id = movie_db.id
    return redirect(url_for('edit', id=movie_id))

if __name__ == '__main__':
    app.run(debug=True)
