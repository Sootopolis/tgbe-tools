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
        1. [Player - Stats](#player---stats)
        2. [Player - Clubs](#player---clubs)
        3. [Player - Games - Ongoing](#player---games---ongoing)
        4. [Player - Games - Monthly Archives](#player---games---monthly-archives)
    2. [Club](#club)
        1. [Club - Members](#club---members)
        2. [Club - Club Matches](#club---club-matches)
    3. [Club Match](#club-match)
   
4. [The Programs](#the-programs)

    1. [Update Membership](#update-membership)

## Background

### The Club

We are a chess club on chess.com that actively participate in daily chess club matches and currently sits 10th on the daily club match worldwide leaderboard.

### Game and Match Formats

In a daily chess game, a player must make a move in a given number of days (usually 3, but can also be 1, 2, 5, 7, 10, 14), whereas failure to do so will result in a loss by timeout. 

In a club match between two clubs:

* Before a match starts, each club field a list of players sorted by ratings from high to low.
* When a match starts, the two lists of players are zipped up, with each pair of players (known as a board) playing two games with each other (one as white and the other as black). The number of boards will be the length of the shorter list of players.
* When a game finishes, if the result is decisive (i.e. if a player beat the other), 1 point is awarded to the winner's club, else 1/2 points is awarded to both clubs.
* If a player is banned by chess.com for cheating, all club matches of the player will be counted as losses, even if they are finished; but in case that a club match opponent of the player is also banned for cheating, the games will count as draws.
* When all games in a match finish, the match finishes. `5 * (number of boards)` leaderboard points is awarded to the club with more points; in case that the clubs tie in points, `2 * (number of boards)` leadership points is awarded to both.

### My Role in Recruitment

As an admin of my club, my main responsibility is to recruit new players by inviting players in other clubs' member lists to join my club. ("Looting" or "raiding", as we call it - but as a player can belong to a virtually unlimited number of clubs, it is not really a steal.)

To invite a player, an admin must send the player an invitation through an official invitation portal, else risk getting banned by chess.com for spamming. Up to 30 invitations are available at any given time on the portal, and once an invitation is used, it will be replenished after exactly 24 hours. 

An invited player can decide to join the club or not. When a player opts to join the club, an admin has to approve the player's join request for the player to become a member.

I aim to **avoid** inviting players who: 

| filter                                               | reason                                                                                                                                            |
|------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| are not online recently                              | they are obviously not active                                                                                                                     |
| are in too many clubs                                | they tend not to do much for any of them                                                                                                          |
| do not play club matches                             | if they don't play for their clubs, they won't do for us                                                                                          |
| time out club matches                                | if they time out for other clubs, they will do for us too (note that I don't care if they time out personal games such as individual tournaments) |
| resign early in club matches                         | similar rationale as above                                                                                                                        |
| move too slow                                        | it's annoying                                                                                                                                     |
| do not have too many daily games ongoing             | it incurs a huge risk of a mass timeout                                                                                                           |
| do not have suspiciously high win rate or elo rating | they are likely to be banned for cheating                                                                                                         |
| do not have really low win rate or elo rating        | they are not of much use for the club                                                                                                             |

Before this project, I manually assessed players one by one according to these criteria. 

I also try to avoid even assessing players who:

* have already been invited
* are current members of my club
* are former members of my club who are no longer members for whatever reasons
* are admins of the clubs that I loot

I also occasionally assist other admins with their tasks, such as identifying members who time out their games or resign early and those who contribute a lot of points to the club. 

## Problems

### Timeout and Inactivity

Players who time out their games make the club lose points in matches unnecessarily.

Prior to important club matches that require a large number of players to join, the admins may resort to manually messaging individual members in order to field enough players. Therefore, players who seldom join club matches are costly as they waste the admins' effort. 

The admins seek to warn and may eventually remove such players. Given the large number of club matches in which the club participate and the large membership for manual management, it is not always possible.

### Player of the Week (POTW)

The club give an award to the player who scores the most points in a 7-day interval (usually from one Thursday 10:00 to the next), known as "player of the week (POTW)". 

An admin has made a program for POTW calculation using PHP. It relies on the "daily match top players" section in the club's profile, which is a list of club members with their club match record (wins/losses/draws) for the club. There are 50 players on each page of the section, therefore for a club like ours with over 400 members, there are 9 pages. The admin manually copies the contents of pages one by one into his program. The program then compares the list to the last entry to calculate changes in the members' records, thus finding out the POTW.

Given the part-manual nature of this operation, it is prone to unfairness if it cannot be executed precisely at the same time each week, and to errors if something somehow goes wrong with the copying-pasting (for example if the content of a page is copied when the curser is hovering within a certain area, the data will show the win/lose/draw percentages of members instead of the absolute numbers, which will cause the program to malfunction).

### Looting

I used to find players to invite manually by going through memberships of other clubs and examining each member, but it would take nearly one hour per day to send 30 invitations this way, which has been by far impossible for me to carry on doing.

Also, the following information is no longer available on the web pages:

* a club's member list, if the club's super admins opt to hide it
* a player's average time per move in daily chess

The club's membership grew from 395 to 470 with my effort during 2020-21. Since I became much busier, it fell to 405 with members leaving, closing their accounts, or being removed by the admins. I know that with my programming knowledge I can revive the club's membership.

## The API

To look for a way to automate the tasks so that I can still contribute to the club, I joined the [Chess.com Developer Community](https://www.chess.com/club/chess-com-developer-community), where I found [the site's api](https://www.chess.com/news/view/published-data-api) (only accessible after creating a account and joining the Chess.com Developer Community).

The relevant endpoints are listed as follows, with simplifications to omit irrelevant parts: 

### Player

```
{
  "username": str, // unique identifier of a player, can change once
  "player_id": int, // unique identifier of a player, cannot change 
  "last_online": int // timestamp of the most recent login
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

#### Player - Clubs

```
{
  "clubs": [
    str // API endpoint URL of club
  ]
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
  "games": [
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

Name of the main program:
* `membership.py`

Files used for this use case:
* `members.json`
* `lost_members.json`

API endpoints used for this use case:
* 3.i. [Player](#player)
* 3.ii.a. [Club - Members](#club---members)

The *Club - Members* API endpoint (3.ii.a.) provides a JSON file which consists of a list of members of a club, and with each member, the timestamps at which the member joined. It can be stored locally into `members.json`. On the next execution of the program, the new JSON and the old can be compared, exposing any differences, i.e. new and lost members. Lost member data are stored in `lost_members.json`.

A problem with this is that a player is allowed to change username once and only once. This is rare but still happens from time to time. For the sake of other use cases, it should not be seen as an old member leaving and a new one joining. 

A somewhat practical solution to this problem is to compare the timestamps of new and lost usernames. To some extent, it can be considered an identifier of a player because it is unlikely that a player leaves and another joins in the same second.

There are two problems with the solution. The obvious one is that the aforementioned event still may happen. Another is that in the rare event that between two execution of the program, a member leaves, rejoins, and changes username at any point during this period, the program cannot detect the username change because the usernames and timestamps are both different.

a more sensible solution is obviously to use the player id in the player api endpoint (3.1.), which is a truly unique identifier of a player. 

a problem with this solution is that instead of 1 http request, the program now has to make (1 + number of members) http requests, which drastically increases the runtime. 

given the relatively low frequency of membership changes thus the need to run this program, plus the fact that comparisons only need to be made on the differences, this should not be a problem. 
