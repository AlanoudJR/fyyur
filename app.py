#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
db.create_all()

# DONE: connect to a local postgresql database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://alanoudjrayes@localhost:5432/fyyur'


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

#Moved to models.py

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  # DONE: replace with real venues data.
  #num_shows should be aggregated based on number of upcoming shows per venue.
  
  data = []

  # Get areas from Venue model and select specific columns by using "with_entities"=reference to the model column attribute and group by city and state.
  areas = Venue.query.with_entities(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()

  # Iterate over each area in our areas query above
  for area in areas:
    #Create a variable to list venues
      data_venues = []

      #Query Venue by filtring by state and city and select all and save them in venues
      venues = Venue.query.filter_by(state=area.state).filter_by(city=area.city).all()

      #Iterate over each venue in venues
      for venue in venues:
          #Query upcoming shows for each venue by comparing the start_time in Shows to the date now using the venue.id 
          upcoming_shows = db.session.query(Show).filter(Show.venue_id == venue.id).filter(Show.start_time > datetime.now()).all()

          #Mapping venue (ID, name, num_upcoming_shows) and appending the values to data_venues list
          data_venues.append({
              'id': venue.id,
              'name': venue.name,
              'num_upcoming_shows': len(upcoming_shows)
          })

      # Mapping areas (city, state, venues) and appending the values to data list
      data.append({
          'city': area.city,
          'state': area.state,
          'venues': data_venues
      })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive. [DONE]
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  #Get the posted search term from the request body
  search_term = request.form.get('search_term')

  #Query using the search_term in Venue model (Case insensitive ilike)
  venues = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()

  #Create a variable to list search results data
  data = []

  #Loop thru the results in venues and append them to the data list.
  for result in venues:
    #map (id, name, num_upcoming_shows) and append the result to data list
    data.append({
      "id": result.id,
      "name": result.name,
      #Display the number of upcoming shows by querying the Show model and filtering each one by comparing the date now to the show date "Will be counted if upcoming date is > than the current date"
      "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id == result.id).filter(Show.start_time > datetime.now()).all()),
      })

  #the Response will be returned with the number of search results "venues" and the data list that will include id, name and number of upcoming shows.
  response={
    "count": len(venues),
    "data": data
    }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id
  
  #Get venue by venue_id
  venue=Venue.query.get(venue_id)
  #Join Show and Artist by filtering by venue_id to get the results for that Venue only
  shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).all()
   
  #Create data list to store all venue details.
  data=[]

  #Create upcoming_shows list to store all upcoming shows.
  upcoming_shows = []

  # Loop thru shows for a specific venue.
  for show in shows_query:
    #Check if the show start time is upcoming then store the details.
      if show.start_time > datetime.now():
        #Add show details for the upcoming show in upcoming show and map.
          upcoming_shows.append({
            #query and display the following details
              "artist_id": show.artist_id,
              "artist_name": show.Artist.name,
              "artist_image_link": show.Artist.image_link,
              "start_time": format_datetime(str(show.start_time))
          })


  #Create past_shows list to store all past shows.
  past_shows = []

  # Loop thru shows for a specific venue.
  for show in shows_query:
      #Check if the show start time is in the past then store the details.
      if show.start_time < datetime.now():
          #Add show details for the past show in past show and map.
          past_shows.append({
              #query and display the following details
              "artist_id": show.artist_id,
              "artist_name": show.Artist.name,
              "artist_image_link": show.Artist.image_link,
              "start_time": format_datetime(str(show.start_time))

          })
  #to Display all the venue data including past and upcoming show.
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
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
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion
  
  #Get form request body
  form = VenueForm(request.form)
  
  #Create a venue object that will have the following fields (because they're the fields that do exist in the new_venue html unlike the model which has additional fields like seeking value)
  venue = Venue(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      genres= form.genres.data,
      address = form.address.data,
      phone = form.phone.data,
      facebook_link = form.facebook_link.data,
  )
  #Try to add the venue object to the db and then commit the change
  try:
      db.session.add(venue)
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  
  #Except: if an error occurs rollback the change and flash an error
  except:
      db.session.rollback()
      # on unsuccessful db insert, flash an error instead
      flash('An error occurred. Venue ' + request.form['name'] +  ' could not be listed.')
  #Finally, close the session
  finally:
      db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # DONE: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  
  #Get venue by venue_id
  venue = Venue.query.get(venue_id)
  
  #Try to delete the object then commit the change/deletion
  try:
      db.session.delete(venue)
      db.session.commit()

  #If an error occurs roll back the change/deletion
  except:
      db.session.rollback()
  
  #Finally close the session
  finally:
      db.session.close()
  
  #Returned a string because returning just None gave me an error.
  return 'Deleted venue'+ venue.name +' succesfully'
 
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # DONE: replace with real data returned from querying the database

  #Query all artists
  data = db.session.query(Artist).all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  #Get the posted search term
  search_term = request.form.get('search_term')

  #Filter using the search_term in artists model (Case insensitive)
  artists = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()

  data = []
  #Loop thru the results in artists and append them to the data array.
  for result in artists:
    data.append({
    "id": result.id,
    "name": result.name,
    #Display the number of upcoming shows by querying the Show  and filtering each one by comparing the date now to the show date "Will be counted if upcoming date is > than the current date"
    "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id == result.id).filter(Show.start_time > datetime.now()).all())
    })

  #Response should return the data above (ID, name and num_upcoming_shows) as well as the number of the search results
  response={
    "count": len(artists),
    "data": data
    }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id

  #Filter by the artist_id and get the first result
  artist = Artist.query.filter_by(id=artist_id).first()

  #Join Show and Venue by filtering by artist_id to get the results for that Venue only
  shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).all()


  #Create upcoming_shows list to store all upcoming shows.
  upcoming_shows = []

  # Loop thru shows for a specific artist.
  for show in shows_query:
      #Check if the show start time is upcoming then store the details.
      if show.start_time > datetime.now():
        #Add show details (venue details) for the upcoming show in upcoming_shows and map.
          upcoming_shows.append({
              "venue_id": show.venue_id,
              "venue_name": show.Venue.name,
              "venue_image_link": show.Venue.image_link,
              "start_time": format_datetime(str(show.start_time))
          })

  #Create past_shows list to store all past shows.
  past_shows = []

  # Loop thru shows for a specific artist.
  for show in shows_query:
      #Check if the show start time is in the past then store the details.
      if show.start_time < datetime.now():
          #Add show details (venue details) for the upcoming show in upcoming_shows and map.
          past_shows.append({
              "venue_id": show.venue_id,
              "venue_name": show.Venue.name,
              "venue_image_link": show.Venue.image_link,
              "start_time": format_datetime(str(show.start_time))
          })

  #To display all the Artist data including past and upcoming show.
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
      "image_link": artist.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  #Get artist form
  form = ArtistForm()

  #get artist by Query artist ID
  artist = Artist.query.get(artist_id)
  
  #Artist fields details from artist with ID
  artist = {
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

  # DONE: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  #Get Artist form
  form = ArtistForm(request.form)
  #Get the artist by id
  artist = Artist.query.filter_by(id=artist_id).first()
 
  #Try to update 
  try:

      # Get data from the form that was inputted by the user on submit and assign it to the artist
      #Artist name = name from the edit form
      artist.name = request.form['name']
      artist.genres = request.form['genres']
      artist.city = request.form['city']
      artist.state = request.form['state']
      artist.phone = request.form['phone']
      artist.facebook_link = form.facebook_link.data
      # The fields below were not included in the form so I commented them
      '''
      #artist.image_link = request.form['image_link']
      #artist.website = request.form['website']
      #artist.seeking_venue = True if request.form['seeking_venue'] == 'Yes' else False
      #artist.seeking_description = request.form['seeking_description']
      '''
      #commit the change
      db.session.commit()
  
  #Rollback when an exception occurs
  except:
      db.session.rollback()

  #Finally close the db session
  finally:
      db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  #Get venue by venue_id
  venue = Venue.query.get(venue_id).first()

  # Populate venue values
  venue = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link
    }
  
  # DONE: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  
  form = VenueForm()
 
  #Get venue from venue_id
  venue = Venue.query.get(venue_id)

  try: 
    # Get data from the form that was inputted by the user on submit and assign it to the venue
    #Venue name = name from the edit form

    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form['facebook_link']
    '''
    venue.image_link = request.form['image_link']
    venue.website = request.form['website']
    venue.seeking_talent = True if 'seeking_talent' in request.form else False 
    venue.seeking_description = request.form['seeking_description']
    '''
    #commit the changes in the DB
    db.session.commit()

  #Handle exceptions by rolling back
  except: 
    db.session.rollback()
  #finally close the DB session
  finally: 
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # Done: insert form data as a new Venue record in the db, instead
  # Done: modify data to be the data object returned from db insertion
  
  #Get Artist request form 
  form = ArtistForm(request.form)
  
  #Create new Artist object that includes the fields that exist on new_artist.html (name, city, state, phone, generes and facebook_link)
  artist = Artist(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      genres = form.genres.data,
      facebook_link = form.facebook_link.data,
  )
  #Try to add the newly created artist instance to the db and commit changes
  try:
      db.session.add(artist)
      db.session.commit()
      # on successful db insert, flash success and display the name of the new artist
      flash('Artist ' + form.name.data + ' was successfully listed!')
  except:
        # on unsuccessful db insert, flash an error and display the name of the attempted new artist
      flash('An error occurred. Artist ' + form.name.data + 'could not be added')
  
  #finally close the session
  finally:
      db.session.close()

  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows [DONE]
  # DOne: replace with real venues data.
  #num_shows should be aggregated based on number of upcoming shows per venue.
  
  #Create a new data list
  data = []
  #Query shows and order based on start time
  shows = Show.query.order_by(Show.start_time.desc()).all()
  
  # loop the shows query to get venue and artist information of each show and add them to data list
  for show in shows:
      # Mapping the data below and and appending the values of each show to data list
      data.append({
          "venue_id": show.venue_id,
          "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
          "artist_id": show.artist_id,
          "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
          "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
          "start_time": format_datetime(str(show.start_time))
      })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # Done: insert form data as a new Show record in the db, instead
  
  #Get Show request form
  form = ShowForm(request.form)

  #Create an instance of show
  show = Show(
      venue_id = form.venue_id.data,
      artist_id = form.artist_id.data,
      start_time = form.start_time.data
  )
  #Try to add the instance "show" and commiting the change to the db session
  try:
      db.session.add(show)
      db.session.commit()
      # on successful db insert, flash success
      flash('Show was successfully listed!')
  #When an exception happens rollback the changes
  except:
      db.session.rollback()
      # on unsuccessful db insert, flash an error instead
      flash('An error occurred. Show could not be listed.')
  #Finally close the session
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
