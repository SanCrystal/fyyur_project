#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from itertools import count
import sys,os
import json
import dateutil.parser
import babel
from flask import Flask, jsonify, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# set migration script
migrate = Migrate(app,db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY( db.Enum('Techno','Disco','Ambient','Industrial','Gospel','Trance','Dubstep','Breakbeat','Ska','Orchestra','New Wave','Grunge','Alternative', 'Blues', 'Classical', 'Country', 'Electronic', 'Folk', 'Funk', 'Hip-Hop', 'Heavy Metal', 'Instrumental', 'Jazz', 'Musical Theatre', 'Pop', 'Punk', 'R&B', 'Reggae', 'Rock n Roll', 'Soul','Swing', 'Other',name='genre')), nullable=True, default='Other')
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=True)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
        return f'<Venue id: {self.id} Venue Name: {self.name}>'
   
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.Enum('Techno','Disco','Ambient','Industrial','Gospel','Trance','Dubstep','Breakbeat','Ska','Orchestra','New Wave','Grunge','Alternative', 'Blues', 'Classical', 'Country', 'Electronic', 'Folk', 'Funk', 'Hip-Hop', 'Heavy Metal', 'Instrumental', 'Jazz', 'Musical Theatre', 'Pop', 'Punk', 'R&B', 'Reggae', 'Rock n Roll', 'Soul','Swing', 'Other',name='genre')),nullable=True, default='Other')
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(200))
    seeking_venue = db.Column(db.Boolean,default=False)
    seeking_description = db.Column(db.String(150))
    shows = db.relationship('Show', backref='artist',lazy=True)

    def __repr__(self):
        return f'<Artist id: {self.id} Artist Name: {self.name}>'
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Show id: {self.id} Artist id: {self.artist_id} Venue Id: {self.venue_id} Start time: {self.start_time}>'
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
  """
  returns Home page,Showing recently listed artists and venues
  """
  # implement artist and venue functions
  venues = Venue.query.order_by(Venue.id.desc()).limit(5).all()
  artists = Artist.query.order_by(Artist.id.desc()).limit(5).all()
  data = {
   "venues": [{"id": venues[i].id, "name": venues[i].name,"image_link":venues[i].image_link} for i in range(len(venues))],
   "artists": [{"id": artists[i].id, "name": artists[i].name,"image_link":artists[i].image_link} for i in range(len(artists))]
  }
  return render_template('pages/home.html',data= data)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  """
     returns a list of all venues
  """
  try:
    venue =  Venue.query.all()
    data = [{
      "city": venue[i].city,
      "state": venue[i].state,
      "venues": [{"id":venue[j].id,"name":venue[j].name} for j in filter(lambda x: venue[i].city == venue[x].city and venue[i].state == venue[x].state, range(len(venue)))]
      }for i in range(len(venue))
    ]
    return render_template('pages/venues.html', areas=data)
  except:
    return render_template('errors/404.html')

@app.route('/venues/search', methods=['POST'])
def search_venues():
  """
    search venues by name, characters in the name, and returns a list of matching venues
  """
  try:
    search_term = request.form.get('search_term', '')
    venue = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
    data =[{"id": venue[i].id, "name": venue[i].name} for i in range(len(venue))]
  
    response={
      "count": len(venue),
      "data":data
    }
    return render_template('pages/search_venues.html', results=response, search_term=search_term)
  except:
    return render_template('errors/404.html')

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  """
    shows the venue page with the given venue_id,returns 404 if venue is not found
  """
  print(venue_id)
  try:
    tables = db.session.query(Venue,Show).join(Show,isouter=True).filter( Show.venue_id==venue_id or Venue.id==venue_id ).all()
    
    if len(tables)>0:
      data = {
        "id":tables[0][0].id,
        "name":tables[0][0].name,
        "genres": tables[0][0].genres,
        "city":tables[0][0].city,
        "state":tables[0][0].state,
        "phone":tables[0][0].phone,
        "website":tables[0][0].website,
        "facebook_link":tables[0][0].facebook_link,
        "seeking_talent":tables[0][0].seeking_talent,
        "seeking_description":tables[0][0].seeking_description,
        "image_link":tables[0][0].image_link,
        "past_shows":[] if tables[0][1]==None else [{ "artist_id": show[1].artist.id,
              "artist_name": show[1].artist.name,
              "artist_image_link": show[1].artist.image_link,
              "start_time": show[1].start_time.strftime('%Y-%m-%d %H:%M:%S')
              } for show in filter(lambda x: x[1].start_time < datetime.now(), tables)],
        "upcoming_shows":[] if tables[0][1]==None else [{ "artist_id": show[1].artist.id,
                "artist_name": show[1].artist.name,
                "artist_image_link": show[1].artist.image_link,
                "start_time": show[1].start_time.strftime('%Y-%m-%d %H:%M:%S')
                } for show in filter(lambda x: x[1].start_time > datetime.now(), tables)],
        "past_shows_count":0 if tables[0][1]==None else len([show[1] for show in tables if show[1].start_time < datetime.now()]),
        "upcoming_shows_count":0 if tables[0][1]==None else len([show[1] for show in tables if show[1].start_time > datetime.now()])
      }
    
    
      return render_template('pages/show_venue.html', venue=data)
    raise Exception
  except:
    print(sys.exc_info())
    return render_template('errors/404.html')
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  """
    renders form to create a new venue
  """
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  """
    creates a new venue and returns a flash message(sucess or failure)
  """
  try:
    venue = Venue(name=request.form.get('name'),city=request.form.get('city'),state=request.form.get('state'),address=request.form.get('address'),phone=request.form.get('phone'),genres=request.form.getlist('genres'),image_link=request.form.get('image_link'),facebook_link=request.form.get('facebook_link'),website=request.form.get('website_link'),seeking_talent= True if request.form.get('seeking_talent','') == 'y' else False,seeking_description=request.form.get('seeking_description')) 
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    # rollback commmit
    db.session.rollback()
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    
  finally:
    # close session
    db.session.close()
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  """
    deletes a venue with the given venue_id, and redirects to the homepage(/) 
  """
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
    return None
   

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  """"
    return all list of artists
  """
  try:
    artist_list = Artist.query.all()
    data = [{"id": artist_list[i].id, "name": artist_list[i].name} for i in range(len(artist_list))]
    return render_template('pages/artists.html', artists=data)
  except:
    return render_template('errors/404.html')


@app.route('/artists/search', methods=['POST'])
def search_artists():
  """
    search artists by name, characters in the name, and returns a list of matching artists
  """
  try:
    data = Artist.query.filter(Artist.name.ilike(f'%{request.form.get("search_term")}%')).all()
    response = {
      "count": len(data),
      "data": [{"id": data[i].id, "name": data[i].name} for i in range(len(data))]
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))
  except:
    return render_template('errors/404.html')


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  """
    shows the artist page with the given artist_id,returns 404 if artist is not found
  """
  try:

    tables = db.session.query(Artist,Show).join(Show,isouter=True).filter(Show.artist_id == artist_id or Artist.id==artist_id ).all()
    
    if len(tables)>0:
      data = {
        "id":tables[0][0].id,
        "name":tables[0][0].name,
        "genres": tables[0][0].genres,
        "city":tables[0][0].city,
        "state":tables[0][0].state,
        "phone":tables[0][0].phone,
        "website":tables[0][0].website,
        "facebook_link":tables[0][0].facebook_link,
        "seeking_venue":tables[0][0].seeking_venue,
        "seeking_description":tables[0][0].seeking_description,
        "image_link":tables[0][0].image_link,
        "past_shows":[] if tables[0][1]==None else [{ "venue_id": show[1].venue.id,
              "venue_name": show[1].venue.name,
              "venue_image_link": show[1].venue.image_link,
              "start_time": show[1].start_time.strftime('%Y-%m-%d %H:%M:%S')
              } for show in filter(lambda x: x[1].start_time < datetime.now(), tables)],
        "upcoming_shows":[] if tables[0][1]==None else [{ "venue_id": show[1].venue.id,
                "venue_name": show[1].venue.name,
                "venue_image_link": show[1].venue.image_link,
                "start_time": show[1].start_time.strftime('%Y-%m-%d %H:%M:%S')
                } for show in filter(lambda x: x[1].start_time > datetime.now(), tables)],
        "past_shows_count":0 if tables[0][1]==None else len([show[1] for show in tables if show[1].start_time < datetime.now()]),
        "upcoming_shows_count":0 if tables[0][1]==None else len([show[1] for show in tables if show[1].start_time > datetime.now()])
      }
    
    
      return render_template('pages/show_artist.html', artist=data)
    raise Exception
  except:
    return render_template('errors/404.html')
 

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  """
    renders form to edit an artist with the given artist_id, and populate the fields with the current artist data
  """
  try:
    form = ArtistForm()
    artist=Artist.query.get(artist_id)
    
    data = {
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link
    }

    return render_template('forms/edit_artist.html', form=form, artist=data)
  except:
    return render_template('errors/404.html')


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  """
    handles the edit artist form submission, and updates the artist with the given artist_id  
  """
  try:
    artist = Artist.query.get(artist_id)
    data = {
            "name":request.form.get("name"),
            "genres":request.form.getlist("genres"),
            "city":request.form.get("city"),
            "state":request.form.get("state"),
            "phone":request.form.get("phone"),
            "website":request.form.get("website"),
            "facebook_link":request.form.get("facebook_link"),
            "seeking_venue":True if request.form.get("seeking_venue")=='y' else False,
            "seeking_description":request.form.get("seeking_description"),
            "image_link":request.form.get("image_link")
            }
    for i,j in data.items():
      setattr(artist, i, j)

    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
  finally:
    db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))
  

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  """
    renders form to edit a venue with the given venue_id, and populate the fields with the current venue data
  """
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  """
    handles the edit venue form submission, and updates the venue with the given venue_id
  """
  try:
    venue = Venue.query.get(venue_id)
    data = {
          "name":request.form.get("name"),
          "genres":request.form.getlist("genres"),
          "city":request.form.get("city"),
          "state":request.form.get("state"),
          "phone":request.form.get("phone"),
          "website":request.form.get("website"),
          "facebook_link":request.form.get("facebook_link"),
          "seeking_talent":True if request.form.get("seeking_talent")=='y' else False,
          "seeking_description":request.form.get("seeking_description"),
          "image_link":request.form.get("image_link")
          }
    for i,j in data.items():
      setattr(venue, i, j)
      
    db.session.commit()
    # flash success message
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
    
  except:
    db.session.rollback()
    # flash error message
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
  finally:
    db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))
    

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  """
    renders form to create a new artist
  """
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  """
    handles the create artist form submission, and creates a new artist with the given required data
  """
  try:
    form_data = request.form
    artist = Artist(name=form_data.get('name'),city=form_data.get('city'),state=form_data.get('state'),phone=form_data.get('phone'),genres=form_data.getlist('genres'),image_link=form_data.get('image_link'),facebook_link=form_data.get('facebook_link'),website=form_data.get('website_link'),seeking_venue=True if form_data.get('seeking_venue')=='y' else False,seeking_description=form_data.get('seeking_description'))
    db.session.add(artist)
    db.session.commit()
  # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  """
      renders list of shows at 
  """
  try:

    tables= db.session.query(Show,Artist,Venue).join(Artist).join(Venue).order_by(Show.start_time.desc()).all()
  
    data=[{"venue_id": i[2].id,
        "venue_name": i[2].name,
        "artist_id": i[0].artist_id,
        "artist_name": i[1].name,
        "artist_image_link": i[1].image_link,
        "start_time": i[0].start_time.strftime('%Y-%m-%d %H:%M:%S')} for i in tables]
    
    return render_template('pages/shows.html', shows=data)
  except:
    return render_template('errors/404.html')
 

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  """
    renders form to create a new show
  """
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  """
    handles the create show form submission, and creates a new show with the given required data
  """
  try:
    form_data = request.form
    show = Show(artist_id=form_data.get('artist_id'),venue_id=form_data.get('venue_id'),start_time=form_data.get('start_time'))
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    flash('An error occurred. Show could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
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

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
