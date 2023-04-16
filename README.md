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
- orm built in sqlite_tools will be the interface with this data
- database is configured in db.py
- client side will be a webapp
- all webapps served, requests handled, and database changes made by a flask app


