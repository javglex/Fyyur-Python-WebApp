#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import collections
collections.Callable = collections.abc.Callable
from models import db, Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db) # setup so we can start using the flask db migrate commands


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  locations = Venue.query.with_entities(Venue.state, Venue.city).distinct(Venue.state, Venue.city).all()
  data = [] # will populate with our venues
  for i in range(len(locations)):
    venues = Venue.query.filter_by(state=locations[i][0], city=locations[i][1]).all()
    data.append({
      'city': locations[i].city,
      'state': locations[i].state,
      'venues':[]
    })
    for venue in venues:
      item = {
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': -1 # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
      }
      data[i]['venues'].append(item)

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  print(search_term)
  query = Venue.query.filter(Venue.name.ilike('%' + search_term + '%'))
  venues = []
  for venue in query.all():
    venues.append({
      "id":venue.id,
      "name":venue.name
    })
  response = {
    "count": query.count(),
    "data": venues
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue = Venue.query.get(venue_id)
  now = datetime.now()
  artistShowJoinQuery = Show.query.join(Artist).filter(Show.venue_id==venue_id)
  joinedShows = artistShowJoinQuery.all()
  upcomingShowData = []
  pastShowData = []
  for show in joinedShows:
    showData = {
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": str(show.start_time)
      }
    if show.start_time> now:
      upcomingShowData.append(showData)
    else: 
      pastShowData.append(showData)
      
  data={
    "id": venue_id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": pastShowData,
    "upcoming_shows": upcomingShowData,
    "past_shows_count": len(pastShowData),
    "upcoming_shows_count": len(upcomingShowData),
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  form = VenueForm(request.form, meta={'csrf': False})
  # called to create new shows in the db, upon submitting new show listing form
  try:
    name = form['name'].data # get our data using json key
    city = form['city'].data
    state = form['state'].data
    phone = form['phone'].data
    image_link = form['image_link'].data
    genres = form['genres'].data
    address = form['address'].data
    facebook_link = form['facebook_link'].data
    website_link = form['website_link'].data
    seeking_talent =  True if 'seeking_talent' in form else False
    seeking_description = form['seeking_description'].data

    if form.validate():
      newVenue = Venue(
        name=name,
        city=city,
        state=state,
        phone=phone,
        address=address,
        image_link=image_link,
        genres=genres,
        facebook_link=facebook_link,
        website_link=website_link,
        seeking_talent=seeking_talent,
        seeking_description = seeking_description
      )
      db.session.add(newVenue) # added todo as a pending change, not yet commited
      db.session.commit() # commit our record
    else: 
      error = True
      message = ''
      for field, err in form.errors.items():
        message+=field + ' ' + '|'.join(err) + '. '
      flash('Error validating form: ' + str(message))
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    flash('Error creating Venue')
    return render_template('forms/new_venue.html', form=form)
  if not error:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
  try:
      print('deleting venue with id:', venue_id)
      venue = Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.commit()
  except:
      db.session.rollback()
      print('exception while deleting todo')
  finally:
      db.session.close()
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  print(search_term)
  query = Artist.query.filter(Artist.name.ilike('%' + search_term + '%'))
  artists = []
  for artist in query.all():
    artists.append({
      "id":artist.id,
      "name":artist.name
    })
  response = {
    "count": query.count(),
    "data": artists
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  artist = Artist.query.get(artist_id)
  now = datetime.now()
  artistShowJoinQuery = Show.query.join(Artist).filter(Show.artist_id==artist_id)
  joinedShows = artistShowJoinQuery.all()
  upcomingShowData = []
  pastShowData = []
  for show in joinedShows:
    showData = {
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": str(show.start_time)
      }
    if show.start_time> now:
      upcomingShowData.append(showData)
    else: 
      pastShowData.append(showData)
      
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": pastShowData,
    "upcoming_shows": upcomingShowData,
    "past_shows_count": len(pastShowData),
    "upcoming_shows_count": len(upcomingShowData),
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  data={
    "id": artist_id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website_link": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }
  print(data)
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  if artist:
    setattr(artist, 'name', request.form['name'])
    setattr(artist, 'genres', request.form.getlist('genres'))
    setattr(artist, 'city', request.form['city'])
    setattr(artist, 'state', request.form['state'])
    setattr(artist, 'phone', request.form['phone'])
    setattr(artist, 'website_link', request.form['website_link'])
    setattr(artist, 'facebook_link', request.form['facebook_link'])
    setattr(artist, 'image_link', request.form['image_link'])
    setattr(artist, 'seeking_venue', True if 'seeking_venue' in request.form else False)
    setattr(artist, 'seeking_description', request.form['seeking_description'])

    db.session.commit()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  data={
    "id": venue_id,
    "name": venue.name,
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"], # TODO use real data
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "address": venue.address,
    "website_link": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }
  print(data)
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  if venue:
    setattr(venue, 'name', request.form['name'])
    setattr(venue, 'genres', request.form.getlist('genres'))
    setattr(venue, 'city', request.form['city'])
    setattr(venue, 'state', request.form['state'])
    setattr(venue, 'phone', request.form['phone'])
    setattr(venue, 'address', request.form['address'])
    setattr(venue, 'website_link', request.form['website_link'])
    setattr(venue, 'facebook_link', request.form['facebook_link'])
    setattr(venue, 'image_link', request.form['image_link'])
    setattr(venue, 'seeking_talent', True if 'seeking_talent' in request.form else False)
    setattr(venue, 'seeking_description', request.form['seeking_description'])

    db.session.commit()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  form = ArtistForm(request.form, meta={'csrf': False})
  try:
    name = form['name'].data
    city = form['city'].data
    state = form['state'].data
    phone = form['phone'].data
    image_link = form['image_link'].data
    genres = form['genres'].data
    facebook_link = form['facebook_link'].data
    website_link = form['website_link'].data
    seeking_venue =  True if 'seeking_venue' in request.form else False
    seeking_description = form['seeking_description'].data
    print('seeking venue:' + str(seeking_venue))

    if form.validate():
      newArtist = Artist(
        name=name,
        city=city,
        state=state,
        phone=phone,
        image_link=image_link,
        genres=genres,
        facebook_link=facebook_link,
        website_link=website_link,
        seeking_venue=seeking_venue,
        seeking_description = seeking_description
      )

      db.session.add(newArtist) # added todo as a pending change, not yet commited
      db.session.commit() # commit our record
    else: 
      error = True
      message = ''
      for field, err in form.errors.items():
        message+=field + ' ' + '|'.join(err) + '. '
      flash('Error validating form: ' + str(message))
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    flash('Error creating Artist')
    return render_template('forms/new_artist.html', form=form)
  if not error:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  shows = Show.query.all()
  data = []
  for show in shows:
    artist = Artist.query.get(show.artist_id)
    venue = Venue.query.get(show.venue_id)
    data.append({
      "venue_id": show.venue_id,
      "venue_name": venue.name,
      "artist_id": show.artist_id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": str(show.start_time)
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  # called to create new shows in the db, upon submitting new show listing form
  try:
    venue_id = request.form.get('venue_id', '') # get our data using json key
    artist_id = request.form.get('artist_id', '')
    start_time = request.form.get('start_time', '')
    newShow = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(newShow) # added todo as a pending change, not yet commited
    db.session.commit() # commit our record
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    flash('Error creating Artist')
  if not error:
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  
  return render_template('pages/home.html')

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

# equivalent to typing the following command in the terminal 
# FLASK_APP=app.py FLASK_DEBUG=true flask run
if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0")