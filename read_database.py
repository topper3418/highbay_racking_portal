from main import app_data_path
from data.sqlite_tools import Tickets

tickets = Tickets(app_data_path)

print(tickets.fetch_100())