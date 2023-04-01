# highbay_racking_portal
A portal for users to submit highbay racking requests and for maintenance to get all the information they need

Workflows to support:
- operations submits and tracks tickets against their own equipment 
- maintenance views and actions tickets, submit purchase requests
- admin views and actions tickets, submits, actions and follows up on purchase requests
- all can view and action tickets
- all can view highbay racking pages (buttons on page depending on user)

Architecture
- data stored in a sqlite database
- client side will be a webapp
- all webapps served, requests handled, and database changes made by a flask app
- all changes to database will be on changelog on DB, will have a username (sometimes system) attached to it
- each type of change will have its own function and will be in the database
- there will be an app log that logs all requests in a logfile, which rolls every day

Plan for sprint:
- DONT FORGET TO COMMIT FREQUENTLY
- race to minimum viable working product
  - build flask framework, maybe start with my pico hub dev server?
  - build sqlite database from notes. see if there's a good IDE
    - build a filesystem to link to
  - build a few html templates. don't bother making them do anything useful, just make them have placeholders and make them navigatable
    - fake main landing page
    - requests page
    - rack page
    - vendor page
- buildout:
  - add sqlite integration with built in fetch requests on the js
  - add ability to make changes to DB from menu, thats how we will be adding entries going forward
