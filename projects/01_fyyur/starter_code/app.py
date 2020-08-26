#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import babel
from flask import Flask, abort, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import datetime
import pytz
import functools

print = functools.partial(print, flush=True)

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', lazy=True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist', lazy=True)

class Show(db.Model):
  __tablename__= 'shows'

  id = db.Column(db.Integer, primary_key=True)
  start_time =  db.Column(db.String(120))
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)

# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  # This is to parse string date format
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------
@app.route('/venues')
def venues():
  try:
    venues_shows = Venue.query.outerjoin(Venue.shows).all()
    cities = set()
    data = []
    for venue in venues_shows:
      # Use parser to parse iso or other time format directly , temporarily ignore timezone issue to simplify
      num_upcoming_shows = sum( dateutil.parser.parse(el.start_time, ignoretz=True) > datetime.datetime.now() for el in venue.shows)
      if venue.city not in cities:
        data.append({"city": venue.city, "state": venue.state, "venues": [{"id": venue.id, "name": venue.name, "num_upcoming_shows": num_upcoming_shows}]})
        cities.add(venue.city)
      else:
        for el in data:
          if venue.city == el["city"]:
            el["venues"].append({"id": venue.id, "name": venue.name, "num_upcoming_shows": num_upcoming_shows})
  except:
    print(sys.exc_info())
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  response={
    "count": 0,
    "data": []
  }
  try:
    search_term = request.form['search_term']
    venues_shows = Venue.query.outerjoin(Venue.shows).all()
    for venue in venues_shows: 
      if search_term.lower() in venue.name.lower():
        num_upcoming_shows = max(0, sum( dateutil.parser.parse(show.start_time, ignoretz=True) > datetime.datetime.now() for show in venue.shows))
        response["count"] += 1
        response["data"].append({
          "id": venue.id, 
          "name": venue.name,
          "num_upcoming_shows" : num_upcoming_shows # seems this is not captured by frontend
        })
  except:
    print(sys.exc_info())
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  try:
    venue_form = request.form
    genres = ",".join(venue_form.getlist('genres'))
    venue = Venue(
      name=venue_form['name'], 
      city=venue_form['city'],
      state=venue_form['state'],
      address=venue_form['address'],
      phone=venue_form['phone'], 
      genres=genres, 
      website=venue_form['website'], 
      facebook_link=venue_form['facebook_link'],
      # check if seeking tablen is checked
      seeking_talent=True if venue_form.get('seeking_talent') else False ,
      seeking_description=venue_form['seeking_description']
    )
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return redirect(url_for('venues'))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data = {}
  try: 
    v = Venue.query.get(venue_id)
    print(v)
    # use outerjoin to perform left outer join on Venue
    venue_show = Venue.query.filter_by(id=venue_id).outerjoin(Venue.shows).first()
    past_shows = []
    print(venue_show)
    upcoming_shows = []
    for show in venue_show.shows:
      artist = Artist.query.get(show.artist_id)
      print(show)
      if dateutil.parser.parse(show.start_time, ignoretz=True) < datetime.datetime.now():
        past_show = {
          "artist_id": artist.id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": show.start_time
        }
        past_shows.append(past_show)
      else:
        upcoming_show = {
          "artist_id": artist.id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": show.start_time
        }
        upcoming_shows.append(upcoming_show)
    
    data = {
      "id": venue_show.id,
      "name": venue_show.name,
      "genres": venue_show.genres.strip().split(","), 
      "address": venue_show.address,
      "city": venue_show.city,
      "state": venue_show.state,
      "phone": venue_show.phone,
      "website": venue_show.website,
      "facebook_link": venue_show.facebook_link,
      "seeking_talent": venue_show.seeking_talent,
      "seeking_description": venue_show.seeking_description,
      "image_link": venue_show.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows)
    }
  except:
    db.session.rollback()
    flash('Venue ' + str(venue_id) + ' is not in the records!')
    print(sys.exc_info())
  finally: 
    db.session.close()
  return render_template('pages/show_venue.html', venue=data)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  try: 
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error:
    return {"success": False}
  else:
    return {"success": True}

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  data = {}
  error = False
  try:
    venue = Venue.query.get(venue_id)
    data={
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres.split(","),
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "address": venue.address,
      "website": venue.website,
      "facebook_link":  venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link
    }
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + str(venue_id) + ' does not exit.')
  return render_template('forms/edit_venue.html', form=form, venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  try:
    venue_form = request.form
    genres = ",".join(venue_form.getlist('genres'))

    # update artist object and commit
    venue = Venue.query.get(venue_id)
    venue.name=venue_form['name']
    venue.city=venue_form['city']
    venue.state=venue_form['state']
    venue.phone=venue_form['phone']
    venue.address = venue_form['address']
    venue.genres=genres
    venue.website=venue_form['website']
    venue.facebook_link=venue_form['facebook_link']
    venue.seeking_talent = True if venue_form.get('seeking_talent') else False
    venue.seeking_description=venue_form["seeking_description"]
    venue.image_link=venue_form["image_link"]
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully edited!')
  return redirect(url_for('venues'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  try:
    data = Artist.query.order_by('id').all()
  except:
    print(sys.exc_info())
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  response={
    "count": 0,
    "data": []
  }
  try:
    search_term = request.form['search_term']
    artist_shows=Artist.query.outerjoin(Artist.shows).all()
    for artist in artist_shows: 
      if search_term.lower() in artist.name.lower():
        num_upcoming_shows = max(0, sum( dateutil.parser.parse(show.start_time, ignoretz=True) > datetime.datetime.now() for show in artist.shows))
        response["count"] += 1
        response["data"].append({
          "id": artist.id, 
          "name": artist.name,
          "num_upcoming_shows" : num_upcoming_shows 
        })
  except:
    print(sys.exc_info())
  finally: 
    db.session.close()
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

#  Create Artist
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  try:
    artist_form = request.form
    genres = ",".join(artist_form.getlist('genres'))
    # to loop through genres
    artist = Artist(
      name=artist_form['name'], 
      city=artist_form['city'],
      state=artist_form['state'],
      phone=artist_form['phone'], 
      genres=genres, 
      facebook_link=artist_form['facebook_link']
    )
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally: 
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  data = {}
  try: 
    artist_show = Artist.query.filter_by(id=artist_id).outerjoin(Artist.shows).first()
    past_shows = []
    upcoming_shows = []
    for show in artist_show.shows:
      venue = Venue.query.get(show.venue_id)
      show_info = {
        "venue_id": venue.id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": show.start_time
      }
      if dateutil.parser.parse(str(show.start_time), ignoretz=True) < datetime.datetime.now():
        past_shows.append(show_info)
      else:
        upcoming_shows.append(show_info)
    data = {
      "id": artist_show.id,
      "name": artist_show.name,
      "genres": artist_show.genres.strip().split(","), 
      "city": artist_show.city,
      "state": artist_show.state,
      "phone": artist_show.phone,
      "website": artist_show.website,
      "facebook_link": artist_show.facebook_link,
      "seeking_venue": artist_show.seeking_venue,
      "seeking_description": artist_show.seeking_description,
      "image_link": artist_show.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows)
    }
  except:
    flash('Artist ' + str(artist_id) + ' is not in the records!')
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  return render_template('pages/show_artist.html', artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  data = {}
  error = False
  try:
    artist = Artist.query.get(artist_id)
    data={
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres.split(","),
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link
    }
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + str(artist_id) + ' does not exit.')
  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  try:
    artist_form = request.form
    genres = ",".join(artist_form.getlist('genres'))
    print(artist_form)
    # update artist object and commit
    artist = Artist.query.get(artist_id)
    artist.name=artist_form['name']
    artist.city=artist_form['city']
    artist.state=artist_form['state']
    artist.phone=artist_form['phone'] 
    artist.genres=genres
    artist.website=artist_form['website']
    artist.facebook_link=artist_form['facebook_link']
    artist.seeking_venue=True if artist_form.get('seeking_venue') else False
    artist.seeking_description=artist_form["seeking_description"]
    artist.image_link=artist_form["image_link"]
    
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully edited!')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  error = False
  try: 
    artist = Artist.query.get(artist_id)
    db.session.delete(artist)
    db.session.commit()
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error:
    return {"success": False}
  else:
    return {"success": True}

#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
  data = []
  try:
    shows = Show.query.join(Venue).filter(Show.venue_id == Venue.id).join(Artist).filter(Show.artist_id == Artist.id).all()
    for show in shows:
      data.append({
        "id": show.id,
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time
      })
  except:
    print(sys.exc_info())
  finally: 
    db.session.close()
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  try:
    show_form = request.form
    show = Show(
      venue_id=int(show_form['venue_id']), 
      artist_id=int(show_form['artist_id']),
      start_time=show_form['start_time']
    )
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error:
    flash('An error occurred. Show could not be created.')
  else:
    flash('Show  was successfully created!')
  return render_template('pages/home.html')

@app.route('/shows/<show_id>', methods=['DELETE'])
def delete_show(show_id):
  error = False
  try: 
    show = Show.query.get(show_id)
    db.session.delete(show)
    db.session.commit()
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error:
    return {"success": False}
  else:
    return {"success": True}

# App running
# --------------------------------------------------
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
