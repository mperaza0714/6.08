# 6.08 Space Team

## To-do

* Return webpage from `new_game.py`
* Generate board layout when joining

## API

* `GET /new_game.py` Start a game lobby
* `POST /new_game.py` Join an open game lobby  
 Body parameters: `username`, `game_id`

## Database (`game.db`)

### `Games`

```
CREATE TABLE Games
(game_id INTEGER PRIMARY KEY AUTOINCREMENT,
 start_time TIMESTAMP,
 lives INTEGER DEFAULT 10,
 score INTEGER,
 stage INTEGER)
```

### `Players`

```
CREATE TABLE IF NOT EXISTS Players
(player_id INTEGER PRIMARY KEY AUTOINCREMENT,
 username TEXT UNIQUE,
 active_game_id INTEGER)
```
