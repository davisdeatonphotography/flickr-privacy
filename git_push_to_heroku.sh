#!/bin/bash

# Add all changed files to git
git add .

# Commit the changes with a message
git commit -m "v 0.1."

# Set up remote for GitHub (only needs to be done once)
git remote add origin https://github.com/davisdeatonphotography/flickr-privacy.git

# Push the changes to your GitHub repository
git push origin master

# Set up remote for Heroku (only needs to be done once)
heroku git:remote -a flickr-privacy

# Push the changes to Heroku
git push heroku master
