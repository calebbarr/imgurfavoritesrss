# imgurfavoritesrss

Creates an RSS feed out of any Imgur user's favorites.  Intended for use with Slack.

## usage

In Slack channel:

`/feed add https://imgurfavorites.herokuapp.com/SnugglyWalrus`

### result

![random_channel](http://i.imgur.com/vgtYTtn.png)

## deploy your own

Make sure you `heroku config:set` both `IMGUR_CLIENT_ID` and `IMGUR_CLIENT_SECRET`.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

