#!/bin/bash

# Set up the Git AskPass script to provide the personal access token
GIT_ASKPASS_SCRIPT="$(mktemp)"
cat << 'EOF' > "${GIT_ASKPASS_SCRIPT}"
#!/bin/bash
echo "$PERSONAL_ACCESS_TOKEN"
EOF
chmod +x "${GIT_ASKPASS_SCRIPT}"
export GIT_ASKPASS="${GIT_ASKPASS_SCRIPT}"

# Add all changed files to git
git add .

# Commit the changes with a message
git commit -m "v 0.1."

# Push the changes to your GitHub repository using the personal access token
PERSONAL_ACCESS_TOKEN="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" git push origin master

# Clean up the Git AskPass script
rm -f "${GIT_ASKPASS_SCRIPT}"

# Set up remote for Heroku (only needs to be done once)
alias heroku=/usr/local/bin/heroku
heroku git:remote -a flickr-privacy

# Push the changes to Heroku
heroku git push heroku master
