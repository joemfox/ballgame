## ballgame

This is a Docker project. To get started, run `docker compose up --d` from the project root.

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