## ballgame

This is a Docker project. To get started, run `docker compose up --d` from the project root.

*jan. 5*
- created lineup card on frontend with drag and drop from player list
- created Lineup model instead of many-to-many team relationship
- added API endpoint for get/post lineups
- next: hook up frontend lineup card to API endpoint so we can use it
- after: user auth

*jan. 3*
- created Membership intermediate class for adding player to team
- added many-to-many relationship to Team for use as a lineup
- added position multiselect filtering API
- added frontend for position multiselect
- next: validate lineups/create position slots somehow

*jan. 2*
- correctly set up tailwind + shadcn/ui
- implemented player list data table
- implemented add to team API endpoint
- implemented player list sorting
- implemented player list searching
- enabled server side pagination on player list
- set up client side data updating when adding to team
- next: fix pagination on client side (table always wants to go backward for some reason)
- after: create the dashboard
- also: work on user authentication

*jan. 1*
- created vite app for frontend
- ballgame container is now the frontend react/vite app instead of a django app
- set up docker on windows, went smoothly
- chadwick register is a little tricky, we don't want it to function as a git repo inside of our git repo
- set up API to return all players
- tried to set up shadcn ui and tailwind but it doesn't seem to be working. Think i included the css wrong somehow
- next: create the player list table
- after: create the dashboard 