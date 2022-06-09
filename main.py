from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired
import requests

# To search movie database using their API (themoviedb.org)
API_KEY = '908c6c635fa52e2f60bf8bf4375f40a5'

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

Bootstrap(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# creating sql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'
db = SQLAlchemy(app)


# creating database structure

# bug alert getting the id to automatically add and increase
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)


db.create_all()
new_entry = Movie(

    title="Phone Booth",
    year=2002,
    description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
    rating=7.3,
    ranking=10,
    review="My favourite character was the caller.",
    img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
)
# db.session.add(new_entry)

# when you commit the first time a second time will raise integrity error
# db.session.commit()
movies = Movie.query.all()

@app.route("/")
def home():
    movies_1 = Movie.query.all()
    return render_template("index.html", movies=movies_1)

# major bug alert the automatic increment of ID in sql.

# forms
class Rating_form(FlaskForm):
    rating = IntegerField(label='What is your rating over 10')
    review = StringField(label="what is your review")
    done = SubmitField(label='Done')


@app.route("/edit/int:<clicked>", methods=['GET', 'POST'])
def edit(clicked):
    form = Rating_form()
    form.validate_on_submit()
    if request.method == 'GET':
        return render_template('edit.html', form=form)
    else:
        for movie in movies:
            if int(movie.id) == int(clicked):
                movie.rating = form.rating.data
                movie.review = form.review.data
                db.session.commit()
        return redirect(url_for('home'))


#     redirect(url_for()) undo the previous url path and transfers you to another unrelated html
# duplicate sessions raise error when you add and remove same session it raises errors
# start another session and perform the opposite operation

@app.route("/delete/<clicked>", methods=['GET', 'POST'])
def delete(clicked):
    mover = Movie.query.all()
    for movie in mover:
        if int(movie.id) == int(clicked):
            db.session.delete(movie)
            db.session.commit()
    return redirect(url_for('home'))


class new_form(FlaskForm):
    name = StringField(label="name of movie", validators=[DataRequired()])
    # description = StringField(label='description')
    # ranking = IntegerField(label='ranking')
    # rating = IntegerField(label='Movie Rating over 10')
    # year = IntegerField(label='Year')
    # review = StringField(label='movie review')
    # image = None
    submit = SubmitField(label='submit')


@app.route('/add', methods=['GET', 'POST'])
def add():
    form = new_form()
    if request.method == 'GET':
        return render_template('add.html', form=form)
    else:
        searched_movie = form.name.data
        API_URL = f'https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={searched_movie}'
        data = requests.get(API_URL)
        print(data.raise_for_status())
        movie_data = data.json()
        return render_template('select.html', json_file=movie_data)
        # Alert


i = 1


@app.route('/success/<chosen>')
def success(chosen):
    final_url = f"https://api.themoviedb.org/3/movie/{chosen}?api_key={API_KEY}"
    data = requests.get(final_url)
    description = data.json()
    # adding new session to the database.
    global i
    i += 1
    try:
        new_movie = Movie(
            id=i,
            title=description['original_title'],
            year=description['release_date'],
            description=description['overview'],
            rating=description['vote_average'],
            ranking=description['vote_count'],
            review=description['tagline'],
            img_url=f'https://image.tmdb.org/t/p/w500{description["poster_path"]}'
        )
        db.session.add(new_movie)
        db.session.commit()
    except:
        print('Database error')
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
