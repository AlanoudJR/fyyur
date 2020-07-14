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


app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.ARRAY(db.String))
    seeking_talent=db.Column(db.Boolean(), default=False)
    seeking_description=db.Column(db.String(500),nullable=True)

    shows = db.relationship('Show', backref='Venue', lazy='dynamic')
    #Added shows field to venues using Show as the association table to have many to many relationship between Venues and Artists

    #represent Venue object when querying
    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'
    # DONE: implement any missing fields, as a database migration using Flask-Migrate [DONE ADDED MISSING FIELDS]

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500),nullable=True)
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120), nullable=True)
    seeking_venue=db.Column(db.Boolean(),default=False)
    seeking_description=db.Column(db.String(500),nullable=True)

    shows = db.relationship('Show', backref='Artist', lazy='dynamic')
    #Added shows field to Artist using Show as the association table to have many to many relationship between Venues and Artists
    
    #represent Artist object when querying
    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'

    # DONE: implement any missing fields, as a database migration using Flask-Migrate [DONE ADDED MISSING FIELDS]

# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration [DONE CREATED SHOW Model].

class Show(db.Model):
  __tablename__='show'
  #Instead of using an association table only we used a model to have extra fields/columns "Start_time" and added ID as the primary key
  id = db.Column(db.Integer,primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
  #Extra field
  start_time = db.Column(db.DateTime, nullable=False)

#represent Show object when querying
  def __repr__(self):
    return f'<Show {self.id}, Artist {self.artist_id}, Venue {self.venue_id}>'