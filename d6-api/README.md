# d6

When playing tabletop war games such as Warhammer, I found I spent most of the game referring to stats cards to figure out the rules for dice rolling.
For me, that took away a lot of the fun. Ideally, I'd like to say "I'm attacking your Psychophage with my Space Marines!" and then have the result of that battle given to me with as little thought as possible.

`d6` is a dice rolling simulator that encodes the rules of the game and the stats of your units in order to automate as much of the boring stuff as possible.

Still in the early stages of development, it is currently evolving to match the practice scenarios (and units) of the Warhammer 40k Starter Kit (10th edition). The ultimate aim, however, is to be as customizable and game-agnostic as possible.

Want to get involved? I'm looking for those with tabletop gaming expertise, regardless of technical prowess. Please get in touch!

## API

This is the current focus of development.

### Deployment

Access: <https://d6-3bxh.onrender.com>
Admin: <https://dashboard.render.com>

### Running in development

```bash
poetry run flask --app d6_api/app.py --debug run
```

### Running in production

```bash
poetry run gunicorn --chdir d6_api app:app
```

### Usage

See the `/apidocs` endpoint.
