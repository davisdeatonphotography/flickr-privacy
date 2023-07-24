$env:GIT_ASKPASS = "echo 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"; `
git add .; `
git commit -m "v 0.2."; `
git push origin master; `
Remove-Item Env:\GIT_ASKPASS; `
heroku git:remote -a flickr-privacy; `
git push heroku master