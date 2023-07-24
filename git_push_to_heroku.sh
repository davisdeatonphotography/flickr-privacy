#!/bin/bash

# Add all changed files to git
git add .

# Commit the changes with a message
git commit -m "v 0.1."

# Set up Git credentials for GitHub using your personal access token
git config credential.helper 'store --file ~/.git-credentials'
echo "https://github.com:davisdeatonphotography:${PERSONAL_ACCESS_TOKEN}" >> ~/.git-credentials

# Push the changes to your GitHub repository
git push origin master

# Set up remote for Heroku (only needs to be done once)
alias heroku=/usr/local/bin/heroku
heroku git:remote -a flickr-privacy

# Push the changes to Heroku
heroku git push heroku master
