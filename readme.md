# Chess Club Management Toolkit

## Table of Contents

1. [Background](#background)

    1. [The Club](#the-club)
    2. [Game and Match Formats](#game-and-match-formats)
    3. [My Role in Recruitment](#my-role-in-recruitment)
2. [Problems](#problems)

    1. [Timeout and Inactivity](#timeout-and-inactivity)
    2. [Player of the Week (POTW)](#player-of-the-week-potw)
    3. [Looting](#looting)

3. [The API](#the-api)

    1. [Player](#player)
        1. [Player - Clubs](#player---clubs)
        2. [Player - Stats](#player---stats)
        3. [Player - Games - Ongoing](#player---games---ongoing)
        4. [Player - Games - Monthly Archives](#player---games---monthly-archives)
    2. [Club](#club)
        1. [Club - Members](#club---members)
        2. [Club - Club Matches](#club---club-matches)
    3. [Club Match](#club-match)

4. [The Programs](#the-programs)

    1. [Update Membership](#update-membership)
    2. [Invite](#invite)
    3. [Loot](#loot)

## Background

### The Club

We are a chess club on chess.com that actively participate in daily chess club matches and currently sits 10th on the
daily club match worldwide leaderboard.

### Game and Match Formats

In a daily chess game, a player must make a move in a given number of days (usually 3, but can also be 1, 2, 5, 7, 10,
14), whereas failure to do so will result in a loss by timeout.

In a club match between two clubs:

* Before a match starts, each club field a list of players sorted by ratings from high to low.
* When a match starts, the two lists of players are zipped up, with each pair of players (known as a board) playing two
  games with each other (one as white and the other as black). The number of boards will be the length of the shorter
  list of players.
* When a game finishes, if the result is decisive (i.e. if a player beat the other), `1` point is awarded to the
  winner's club, else `1/2` points is awarded to both clubs.
* If a player is banned by chess.com for cheating, all club matches of the player will be counted as losses, even if
  they are finished; but in case that a club match opponent of the player is also banned for cheating, the games will
  count as draws.
* When all games in a match finish, the match finishes. `5 * (number of boards)` leaderboard points is awarded to the
  club with more points; in case that the clubs tie in points, `2 * (number of boards)` leadership points is awarded to
  both.

### My Role in Recruitment

As an admin of my club, my main responsibility is to recruit new players by inviting players in other clubs' member
lists to join my club. ("Looting" or "raiding", as we call it - but as a player can belong to a virtually unlimited
number of clubs, it is not really a steal.)

To invite a player, an admin must send the player an invitation through an official invitation portal, else risk getting
banned by chess.com for spamming. Up to 30 invitations are available at any given time on the portal, and once an
invitation is used, it will be replenished after exactly 24 hours.

An invited player can decide to join the club or not. When a player opts to join the club, an admin has to approve the
player's join request for the player to become a member.

I aim to **avoid** inviting players who:

| filter                                                  | reason                                                                                                                                            |
|---------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| are not online recently                                 | they are obviously not active                                                                                                                     |
| are in too many clubs                                   | they tend not to do much for any of them                                                                                                          |
| do not play club matches                                | if they don't play for their clubs, they won't do for us                                                                                          |
| time out club matches                                   | if they time out for other clubs, they will do for us too (note that I don't care if they time out personal games such as individual tournaments) |
| resign early in club matches                            | similar rationale as above                                                                                                                        |
| move too slow                                           | it's annoying                                                                                                                                     |
| do not have too many daily games ongoing                | it incurs a huge risk of a mass timeout                                                                                                           |
| do not have suspiciously high score rate* or elo rating | they are likely to be banned for cheating                                                                                                         |
| do not have really low score rate or elo rating         | they are not of much use for the club                                                                                                             |

where score rate is calculated as such:

```
score_rate = (wins + draws * 0.5) / games_played
```

Before this project, I manually assessed players one by one according to these criteria.

I also try to avoid even assessing players who:

* have already been invited
* are current members of my club
* are former members of my club who are no longer members for whatever reasons
* are admins of the clubs that I loot

I also occasionally assist other admins with their tasks, such as identifying members who time out their games or resign
early and those who contribute a lot of points to the club.

## Problems

### Timeout and Inactivity

Players who time out their games make the club lose points in matches unnecessarily.

Prior to important club matches that require a large number of players to join, the admins may resort to manually
messaging individual members in order to field enough players. Therefore, players who seldom join club matches are
costly as they waste the admins' effort.

The admins seek to warn and may eventually remove such players. Given the large number of club matches in which the club
participate and the large membership for manual management, it is not always possible.

### Player of the Week (POTW)

The club give an award to the player who scores the most points in a 7-day interval (usually from one Thursday 10:00 to
the next), known as "player of the week (POTW)".

An admin has made a program for POTW calculation using PHP. It relies on the "daily match top players" section in the
club's profile, which is a list of club members with their club match record (wins/losses/draws) for the club. There are
50 players on each page of the section, therefore for a club like ours with over 400 members, there are 9 pages. The
admin manually copies the contents of pages one by one into his program. The program then compares the list to the last
entry to calculate changes in the members' records, thus finding out the POTW.

Given the part-manual nature of this operation, it is prone to unfairness if it cannot be executed precisely at the same
time each week, and to errors if something somehow goes wrong with the copying-pasting (for example if the content of a
page is copied when the curser is hovering within a certain area, the data will show the win/lose/draw percentages of
members instead of the absolute numbers, which will cause the program to malfunction).

### Looting

I used to find players to invite manually by going through memberships of other clubs and examining each member, but it
would take nearly one hour per day to send 30 invitations this way, which has been by far impossible for me to carry on
doing.

Also, the following information is no longer available on the web pages:

* a club's member list, if the club's super admins opt to hide it
* a player's average time per move in daily chess

The club's membership grew from 395 to 470 with my effort during 2020-21. Since I became much busier, it fell to 405
with members leaving, closing their accounts, or being removed by the admins. I know that with my programming knowledge
I can revive the club's membership.

## The API

To look for a way to automate the tasks so that I can still contribute to the club, I joined
the [Chess.com Developer Community](https://www.chess.com/club/chess-com-developer-community), where I
found [the site's api](https://www.chess.com/news/view/published-data-api) (only accessible after creating an account and
joining the Chess.com Developer Community).

The relevant endpoints are listed as follows, with simplifications to omit irrelevant parts:

### Player

```
{
  "username": str, // unique identifier of a player, can change once
  "player_id": int, // unique identifier of a player, cannot change 
  "last_online": int // timestamp of the most recent login
}
```

#### Player - Clubs

```
{
  "clubs": [
    str // API endpoint URL of club
  ]
}
```

#### Player - Stats

```
{
  "chess_daily": { // only present if the player has played daily chess 
    "last": {
      "rating": int // current rating of the player
    }, 
    "record": {
      "win": int, // number of daily chess wins overall
      "loss": int, // number of daily chess losses overall
      "draw": int, // number of daily chess draws overall
      "time_per_move": int, // number of seconds per move
      "timeout_percent": float // timeout % last 90 days
    }
  }
}
```

#### Player - Games - Ongoing

```
{
  "games": [
    {
      "match": str // API endpoint URL of the daily club match, only present if the game is a daily club match game
    }
  ]
}
```

#### Player - Games - Monthly Archives

```
{
  "games": [ // list of a player's finished daily games in a calendar month, sorted chronologically
    {
      "end_time": int, // timestamp of end time of a game 
      "white": {
        "result": str, // outcome of the game for white (specified if lost or drawn) 
        "username": str // username of white
      }, 
      "black": {
        "result": str, // outcome of the game for black (specified if lost or drawn) 
        "username": str // username of black
      },
      "match": str // API endpoint URL of the daily club match, only present if the game is a daily club match game
    }
  ]
}
```

### Club

```
{
  "code": 0, // only present if the club does not exist
  "admin": [str] // list of player API endpoint URLs of admins of the club
}
```

#### Club - Members

```
{
  "weekly": [ 
    {
      "username": str, // username of a member
      "joined": int // timestamp at which the member joined
    }
  ],
  "monthly": [
    {
      "username": str, // username of a member
      "joined": int // timestamp at which the member joined
    }
  ],
  "all_time": [
    {
      "username": str, // username of a member
      "joined": int // timestamp at which the member joined
    }
  ]
}
```

"Weekly", "monthly", and "all-time" are active levels of a club's members that are not actually helpful for my purpose.

#### Club - Club Matches

```
{
  "finished": [ // club matches that are finished
    {
      "@id": str, // API endpoint URL of club match
      "start_time": int, // timestamp at which the match started
      "time_class": str // "daily" 
    }
  ],
  "in_progress": [ // club matches in progress
    {
      "@id": str, // API endpoint URL of club match
      "start_time": int, // timestamp at which the match started
      "time_class": str // "daily" 
    }
  ]
}
```

### Club Match

```
{
  "status": str, // "finished" or "in_progress",
  "teams": { // clubs participating 
    "team1": { // the first club 
      "@id": str, // API endpoint URL of club 
      "score": int, // club score as it stands
      "players": [ // club's list of players competing in the match
        {
          "username": str, // player's username
          "played_as_white": str, // game outcome as white, only present if game as white has finished 
          "played_as_black": str // game outcome as white, only present if game as black has finished 
        }
      ],
      "fair_play_removals": [
        str // usernames of players banned for cheating 
      ]
    },
    "team2": { // the second club
      "@id": str, // API endpoint URL of club 
      "score": int, // club score as it stands
      "players": [ // club's list of players competing in the match
        {
          "username": str, // player's username
          "played_as_white": str, // game outcome as white, only present if game as white has finished 
          "played_as_black": str // game outcome as white, only present if game as black has finished 
        }
      ],
      "fair_play_removals": [
        str // usernames of players banned for cheating 
      ]
    }
  }   
}
```

## The Programs

I decided that the following use cases are to be fulfilled:

* update membership
* loot (go through members of a club to find players to invite)
* find timeouts
* find inactivity
* find early resignations
* find POTW
* automate everything (except "loot")

### Update Membership

#### Resources

Module(s) involved:

* `membership.py`

File(s) involved:

* `members.json`
* `lost_members.json`

API endpoint(s) involved:

* 3.i. [Player](#player)
* 3.ii.a. [Club - Members](#club---members)

#### Function 

This program takes no user input, updates `members.json` and `lost_members.json`, and prints usernames of new members, lost members, and username changes.

#### Mechanism, Problems, Compromises, Solutions

The 3.ii.a. [Club - Members](#club---members) endpoint provides a JSON file which consists of a list of members of a club, and with each member, the timestamps at which the member joined. It can be stored locally into `members.json`. On the next execution of the program, the new JSON and the old can be compared, exposing any differences, i.e. new and lost members. Lost member data are stored in `lost_members.json`.

A problem with this is that a player is allowed to change username once and only once. This is rare but still happens from time to time. For the sake of other use cases, it should not be seen as an old member leaving and a new one
joining.

A somewhat practical solution to this problem is to compare the timestamps of new and lost usernames. To some extent, it can be considered an identifier of a player because it is unlikely that a player leaves and another joins in the same second. Now if a member opts to change username, it can be detected as a username change, as a lost username and a new username share the same timestamp.

There are two problems with the solution: 
* As mentioned, is that the unlikely event may still happen. 
* In the also very rare event that between two execution of the program, a member leaves, rejoins, and changes username at any point during this period, the program will consider the old and the new usernames two different players, for the usernames and timestamps are both different.

A more sensible solution is to retrieve from the 3.i. [Player](#player) endpoint every player's player ID, which is an actually unique identifier of a player.

A problem with this solution is that instead of `1` HTTP request, the program now has to make `1 + (number of members)` HTTP requests, which drastically increases the runtime of this program. For a club like mine with 400-600 members, it typically takes a couple of minutes. Should the program be used on clubs with 20,000+ members, however, this process can take hours.

It can be argued that this problem is trivial. The first execution of the program indeed takes `O(n)` runtime, where n stands for the club's membership. But after that, given the generally low ratio of membership changes with regard to the entire membership and the fact that comparisons only need to be performed on the differences, not too many requests have to be made after initialising the membership data. In other words, when comparing the new JSON to the old, the username check can be used on the entire lists, and then the player_id check can be applied on the differences.

My code in production is currently using the username-timestamp check. It will be updated to use the username-player_id check instead to address the very rare corner cases.

### Invite

#### Resources

Module(s) involved:

* `invite.py` (main program)

File(s) involved:

* `invited.txt`

API endpoint(s) involved:

* (none)

#### Function

This is a script that I wrote last year when I just started to learn Python, predating this project. It maintains a duplicate-free list of invited players in `invited.txt`, and supports these operations:

* check - checks a list of usernames to find out which have been invited and which have not
* input - checks a list of usernames to find out which have been invited and which have not, and writes the usernames that have not been invited into `invited.txt`
* output - prints `invited.txt` along with the number of usernames it contains

### Loot

#### Resources

Module(s) involved:

* `loot.py` (main program)
* `membership.py`

File(s) involved:

* `members.json` (list of members of the club)
* `lost_members.json` (list of former members of the club since I began to keep this record, along with their )
* `invited.txt` (list of players invited by me)
* `scanned.json` (list )

API endpoint(s) involved:

* 3.ii. [Club](#club)
* 3.ii.a. [Club - Members](#club---members)
* 3.i. [Player](#player)
* 3.i.a. [Player - Clubs](#player---clubs)
* 3.i.b. [Player - Stats](#player---stats)
* 3.i.c. [Player - Games - Ongoing](#player---games---ongoing)
* 3.i.d. [Player - Games - Monthly Archives](#player---games---monthly-archives)

#### Function

<!-- This program has been incredibly valuable for me personally, not just because my main role in the club's admin team is to recruit new player, but also because the design, implementation, and outcome of this program have been absolutely instrumental in landing me a visa-sponsoring job in the UK.-->

This program takes user inputs of an integer `target` and a string `club_name`, prints usernames of up to `target` invitable (based on a set of hard-coded filters) players from the club with API endpoint URL `f"https://api.chess.com/pub/club/{club_name}"`, prompts the user to add these players to `invited.txt`, and updates `scanned.json` which contains expirable records of players deemed uninvitable.

#### Parameters

At the beginning of the program, user inputs are taken for the number of invitable players to find and the name of the club to find them from.

Then parameters for the filters mentioned earlier in 1.iii. [My Role in Recruitment](#my-role-in-recruitment) are set. These are hard-coded into the program, for there is usually no need to change these parameters. Should some parameters be required to change frequently, though, it would of course be possible to take user inputs for them, but the caching mechanism would have to be overhauled (explained later).

At the moment the parameters are set as following:

| name                | meaning                                           | value |
|---------------------|---------------------------------------------------|------:|
| `min_cm_played`     | minimum number of club match games played/ongoing |    12 |
| `min_cm_ongoing`    | minimum number of club match games ongoing        |     2 |
| `max_ongoing`       | maximum number of daily games ongoing             |   100 |
| `max_clubs`         | maximum number of clubs                           |    32 |
| `min_rating`        | minimum Elo rating                                |  1000 |
| `max_rating`        | maximum Elo rating                                |  2300 |
| `min_score_rate`    | minimum score rate %                              |    45 |
| `max_score_rate`    | maximum score rate %                              |    85 |
| `max_time_per_move` | maximum hours per move in daily chess             |    18 |
| `max_offline`       | maximum hours since last login                    |    48 |

The program then gets the current time. This will be used for multiple purposes:

* to delete expired cache (explained later)
* to get the player games monthly archives that may require inspection, as the program takes into account of players'
  games in the last arbitrary number of days (90 is the number that I chose)
* to write cache (explained later)

#### Caching

Usernames of players deemed invitable by the program will be added into a list. Upon the end of the scanning process (whether due to enough invitable players having been found, due to the target club's member list having been exhausted,
or due to keyboard interruption), the program will print this list and prompt the user to add these usernames into `invited.txt`. If the user opts not to do so, nothing else will happen, and the user can always manually add them using `invite.py`.

Usernames of players deemed uninvitable by the program will be added into a dictionary, along with a timestamp which is the expiry time of their record. A player's record will expire 30 days after the current time, except for players who are filtered out due to a timeout in a club match game, in which case the expiry time will be 90 days after the player's most recent club match timeout. Those numbers are arbitrary and can be changed too. Upon the end of the scanning process, usernames in the dictionary will be added to `scanned.json`. 

A problem with this caching method, as mentioned earlier, is that records must be interpreted in the context of the filters applied. For example, if a filter is set so that a player must have played or been playing 20 club match games in the last 90 days, and if the parameter is lowered to 12 at some point, then some players previously filtered out by this filter may become invitable under the new rule. It should be technically possible to store along with the cache records the set of rules used to filter players out, but it is not done for two reasons:
* It makes caching unnecessarily complicated, whereas it may be more sensible to simply avoid adjusting filters too often.
* If a filter becomes stricter, players in the cache record should fail the new filter too at the time when the record was written; and if a filter becomes looser, it will at most ignore some players who have become invitable, and those players can be assessed again once their records expire.

#### Scanning

The part is organised around the API endpoints accessed and the checks performed based on the information in the endpoints.

[Club](#club)

* Check if the club exists.
* Get a list of the club's admins.

[Club - Members](#club---members)

* Get a list of members of the club.
* Exclude the following players to make a final list of candidates to scan:
  * usernames in `members.json`
  * usernames in `lost_members.json`
  * usernames in `invited.txt`
  * usernames in `scanned.json`
  * usernames in the club's list of admins

If either of the two API endpoints cannot be accessed for any reason in the above processes, the program finishes. 

Now scanning of players begins, and from here if any API endpoint is unreachable, the program simply skips the player in question and moves onto the next one. If at any point the length of the list of invitable players found exceeds `target`, scanning finishes.

[Player](#player)

* Get the player's last login time. 
  * Reject the player if the current time minus the last login time is greater than `max_offline`. 

[Player - Clubs](#player---clubs)

* Get the player's list of clubs. Reject the player if the length of the list is greater than `max_clubs`.

[Player - Stats](#player---stats)

* Reject the player if the player has no daily chess record.
* Get the player's daily chess time per move. Reject the player if this is greater than `max_time_per_move`.
* Get the player's daily chess rating. Reject the player if this is not between `min_rating` and `max_rating`.
* Get the player's daily chess and daily chess960 (a variant of chess that my club also play sometimes) win/loss/draw stats and calculate the player's score rate. Reject the player if the score rate is not between `min_score_rate` and `max_score_rate`.
* Get the player's daily chess timeout percentage. This will not be used to reject a player, but a 0% timeout percentage will significantly simplify timeout checks later on.

[Player - Games - Ongoing](#player---games---ongoing)

* Get the player's list of ongoing games. Reject the player if the length of the list is greater than `max_ongoing`.
* Set `cm_played` to 0 to denote the number of daily club match games that the player has played or been playing. 
* Iterate though the list of ongoing games and increment `cm_played` if a game is a club match game. 
* Reject the player if `cm_played` is smaller than `min_cm_ongoing`.
* Deem the player invitable if the player has 0% timeout percentage and the player's `cm_played` is at least `min_cm_played`.

[Player - Games - Monthly Archives](#player---games---monthly-archives)

* Get the player's lists of finished games in the last 90 days.
* Iterate through the lists in descending chronological order, increment `cm_played` if a game is a club match game.
  * During the iteration, deem a player invitable if the player has 0% timeout percentage and `cm_played` is at least `min_cm_played`.
  * During the iteration, reject a player if the player has lost a game by timeout.
* Reject a player if `cm_played` is smaller than `min_cm_played`.

Deem the player invitable if the player has not been rejected for any reason after all the checks above.



