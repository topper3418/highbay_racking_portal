import random
from datetime import datetime, timedelta
from data.sqlite_tools import AppData, Tickets
from main import app_data_path

# Generate some sample data
types = ['Bug', 'Feature Request', 'Other']
submitters = ['Alice', 'Bob', 'Charlie', 'Dave', 'Eve']
now = datetime.now()
due_dates = [(now + timedelta(days=random.randint(1, 30))).timestamp() for _ in range(10)]
submitted = [(now - timedelta(days=random.randint(1, 30))).timestamp() for _ in range(10)]
due_date_reasons = ['Low priority', 'Needs review', 'Waiting for input']

# Insert the sample data into the database
for i in range(10):
    ticket_data = {
        'type': random.choice(types),
        'submitter': random.choice(submitters),
        'submitted': submitted[i],
        'due_date': due_dates[i],
        'due_date_reason': random.choice(due_date_reasons)
    }
    Tickets(app_data_path).run_cmd_params("""
        INSERT INTO tickets (type, submitter, submitted, due_date, due_date_reason)
        VALUES (:type, :submitter, :submitted, :due_date, :due_date_reason)
    """, ticket_data)
