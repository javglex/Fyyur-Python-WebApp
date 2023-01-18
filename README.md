Fyyur
-----

## Introduction

Fyyur is a musical venue and artist booking site that facilitates the discovery and bookings of shows between local performing artists and venues. This site lets you list new artists and venues, discover them, and list shows with artists as a venue owner.

## Overview

This app is an exercise from Udacity's Full Stack Web Course. The UI was already prepared, and mock data was used to populate views. My task was to implement controller logic in the app.py file, as well as to define SQLAlchemy models in models.py. I also migrated the previous SQLAlchemy models into their completed versions. 

In a nutshell, I implemented the following functionality: 
* creating new venues, artists, and creating new shows.
* searching for venues and artists.
* seeing details views for a specific artist or venue.

## Tech Stack (Dependencies)

### 1. Backend Dependencies
 * **virtualenv** as a tool to create isolated Python environments
 * **SQLAlchemy ORM** to be our ORM library of choice
 * **PostgreSQL** as our database of choice
 * **Python3** and **Flask** as our server language and server framework
 * **Flask-Migrate** for creating and running schema migrations

### 2. Frontend Dependencies
**HTML**, **CSS**, and **Javascript** and **Bootstrap 3** for our visual components

Highlight folders:
* `templates/pages` -- Defines the pages that are rendered to the site. These templates render views based on data passed into the template’s view, in the controllers defined in `app.py`. These pages successfully represent the data to the user, and are already defined for you.
* `templates/layouts` -- Defines the layout that a page can be contained in to define footer and header code for a given page.
* `templates/forms` -- Defines the forms used to create new artists, shows, and venues.
* `app.py` -- Defines routes that match the user’s URL, and controllers which handle data and renders views to the user. This is the main file you will be working on to connect to and manipulate the database and render views with data to the user, based on the URL.
* Models in `app.py` -- Defines the data models that set up the database tables.
* `config.py` -- Stores configuration variables and instructions, separate from the main application code. This is where you will need to connect to the database.

### Install the dependencies:

pip install -r requirements.txt

### Run the development server:

export FLASK_APP=myapp

export FLASK_ENV=development # enables debug mode

python3 app.py