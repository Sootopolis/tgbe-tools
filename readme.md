# Chess Club Management Toolkit

## I. Background

### 1. The Club

We are a chess club on chess.com that actively participate in daily chess club matches and currently sits 10th on the daily club match worldwide leaderboard.

### 2. Game and Match Formats

In a daily chess game, a player must make a move in a given number of days (usually 3, but can also be 1, 2, 5, 7, 10, 14), whereas failure to do so will result in a loss by timeout. 

In a club match between two clubs:

* Before a match starts, each club field a list of players sorted by ratings from high to low.
* When a match starts, the two lists of players are zipped up, with each pair of players (known as a board) playing two games with each other (one as white and the other as black). The number of boards will be the length of the shorter list of players.
* When a game finishes, if the result is decisive (i.e. if a player beat the other), 1 point is awarded to the winner's club, else 1/2 points is awarded to both clubs.
* If a player is banned by chess.com for cheating, all club matches of the player will be counted as losses, even if they are finished; but in case that a club match opponent of the player is also banned for cheating, the games will count as draws.
* When all games in a match finish, the match finishes. `5 * (number of boards)` leaderboard points is awarded to the club with more points; in case that the clubs tie in points, `2 * (number of boards)` leadership points is awarded to both.

### 3. My Role as Club Admin

As an admin of my club, my main responsibility is to recruit new players by inviting players in other clubs' member lists to join my club. ("Looting" or "raiding", as we call it - but as a player can belong to a virtually unlimited number of clubs, it is not really a steal.)

To invite a player, an admin must send the player an invitation through an official invitation portal, else risk getting banned by chess.com for spamming. 

Up to 30 invitations are available at any given time on the portal, and once an invitation is used, it will be replenished after exactly 24 hours. 

An invited player can decide to join the club or not.

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

I also occasionally assist other admins with their tasks, such as identifying members who time out their games or resign early and those who contribute a lot of points to the club. 

## Problems

###
