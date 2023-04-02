import configparser
import os
from config.logging import logger
from data.sqlite_tools import AppData, Tickets, DbTableBase, Roles, Users, TicketTypes, TicketStatus, EquipmentStatus, DueDateReason
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for

# Load configuration from file
config_path = os.path.join('config', 'app.conf')
config = configparser.ConfigParser()
config.read(config_path)

# Create Flask app
app = Flask(__name__)
# initialize data
database_name = config.get('Database', 'name')
app_data_path = os.path.join('data', database_name)
app_data = AppData(app_data_path)
all_tables = app_data.get_tables()
all_views = app_data.get_views()

# get the configuration values from the config file
host_addr = config.get('Server', 'host')
host_port = config.get('Server', 'port')
            
# Example usage
@app.route('/')
def serve_main():
    # log the ip address of the request
    logger.info(f'serving / request from {request.remote_addr}')
    return render_template('index.html')

@app.route('/get_tickets', methods=['GET'])
def fetch_ticket_data():
    """Return the requests table data as JSON"""
    # log the ip address of the request
    logger.info(f'serving /table_data request from {request.remote_addr}')
    # use the table name to get the data from the database
    df = Tickets(app_data_path).fetch_100()
    # convert the DataFrame to JSON
    return jsonify(df.to_dict(orient='records'))
    
@app.route('/dev_page', methods=['GET'])
def serve_dev_page():
    return render_template('dev_page.html')

@app.route('/get_table', methods=['GET'])
def get_table():
    """Return the requests table data as JSON"""
    # first make sure the query is a valid table or view
    query = request.args.get('query')
    if query not in all_tables['name'].values and query not in all_views['name'].values:
        return jsonify({'error': 'invalid query'})
    # log the ip address of the request
    logger.info(f'serving /table_data request from {request.remote_addr}')
    # get and return the data
    if query == 'all_tables':
        df = all_tables
    elif query == 'all_views':
        df = all_views
    elif query not in all_tables['name'].values and query not in all_views['name'].values:
        return jsonify({'error': 'invalid query'})
    else:
        df = DbTableBase(app_data_path, query).fetch_100()
    return jsonify(df.to_dict(orient='records'))

@app.route('/admin_tools_popup', methods=['GET'])
def admin_tools_popup():
    """Return the admin tools popup html"""
    # log the ip address of the request
    logger.info(f'serving /admin_tools_popup request from {request.remote_addr}')
    return render_template('admin_tools_popup.html')

@app.route('/new_role_popup', methods=['GET'])
def new_role_popup():
    """Return the new role popup html"""
    # log the ip address of the request
    logger.info(f'serving /new_role_popup request from {request.remote_addr}')
    return render_template('create_role_popup.html')

@app.route('/create_role', methods=['POST'])
def create_role():
    """Create a new role in the database"""
    # log the ip address of the request
    logger.info(f'serving /create_role request from {request.remote_addr}')
    # parse request data
    new_role = request.form['role-name']
    new_description = request.form['role-description']
    # initialize the Roles object
    roles = Roles(app_data_path)
    # insert data to db
    roles.insert(new_role, new_description)
    # redirect back to the main screen
    return redirect(url_for('serve_main'))
    
@app.route('/get_roles', methods=['GET'])
def get_roles():
    """Return the roles table data as JSON"""
    # log the ip address of the request
    logger.info(f'serving /get_roles request from {request.remote_addr}')
    # get and return the data
    roles_df = Roles(app_data_path).dropdown()
    return jsonify(roles_df.to_dict(orient='records'))

@app.route('/new_user_popup', methods=['GET'])
def new_user_popup():
    """Return the new user popup html"""
    # log the ip address of the request
    logger.info(f'serving /new_user_popup request from {request.remote_addr}')
    return render_template('create_user_popup.html')

@app.route('/create_user', methods=['POST'])
def create_user():
    """Create a new user in the database"""
    # log the ip address of the request
    logger.info(f'serving /create_user request from {request.remote_addr}')
    # parse request data
    new_user = request.form['username']
    new_password = request.form['password']
    new_role = request.form['role']
    # initialize the Roles object
    users = Users(app_data_path)
    users.insert(new_user, new_password, new_role)
    return redirect(url_for('serve_main'))

@app.route('/new_ticket_type_popup', methods=['GET'])
def new_ticket_type_popup():
    """Return the new ticket type popup html"""
    # log the ip address of the request
    logger.info(f'serving /new_ticket_type_popup request from {request.remote_addr}')
    return render_template('create_ticket_type_popup.html')

@app.route('/create_ticket_type', methods=['POST'])
def create_ticket_type():
    """Create a new ticket type in the database"""
    # log the ip address of the request
    logger.info(f'serving /create_ticket_type request from {request.remote_addr}')
    # parse request data
    new_ticket_type = request.form['ticket-type']
    new_description = request.form['type-description']
    # initialize the Roles object
    ticket_types = TicketTypes(app_data_path)
    ticket_types.insert(new_ticket_type, new_description)
    return redirect(url_for('serve_main'))

@app.route('/new_ticket_status_popup', methods=['GET'])
def new_ticket_status_popup():
    """Return the new ticket status popup html"""
    # log the ip address of the request
    logger.info(f'serving /new_ticket_status_popup request from {request.remote_addr}')
    return render_template('insert_to_lookup_table_popup.html', name='Ticket Status', table_name='ticket_status')

@app.route('/create_ticket_status', methods=['POST'])
def create_ticket_status():
    """Create a new ticket status in the database"""
    # log the ip address of the request
    logger.info(f'serving /create_ticket_status request from {request.remote_addr}')
    # parse request data
    new_ticket_status = request.form['ticket_status_name']
    new_description = request.form['ticket_status_description']
    # initialize the Roles object
    ticket_status = TicketStatus(app_data_path)
    ticket_status.insert(new_ticket_status, new_description)
    return redirect(url_for('serve_main'))

@app.route('/new_equipment_status_popup', methods=['GET'])
def new_equipment_status_popup():
    """Return the new equipment status popup html"""
    # log the ip address of the request
    logger.info(f'serving /new_equipment_status_popup request from {request.remote_addr}')
    return render_template('insert_to_lookup_table_popup.html', name='Equipment Status', table_name='equipment_status')

@app.route('/create_equipment_status', methods=['POST'])
def create_equipment_status():
    """Create a new equipment status in the database"""
    # log the ip address of the request
    logger.info(f'serving /create_equipment_status request from {request.remote_addr}')
    # parse request data
    new_equipment_status = request.form['equipment_status_name']
    new_description = request.form['equipment_status_description']
    # initialize the Roles object
    equipment_status = EquipmentStatus(app_data_path)
    equipment_status.insert(new_equipment_status, new_description)
    return redirect(url_for('serve_main'))

@app.route('/new_due_date_reason_popup', methods=['GET'])
def new_due_date_reason_popup():
    """Return the new due date reason popup html"""
    # log the ip address of the request
    logger.info(f'serving /new_due_date_reason_popup request from {request.remote_addr}')
    return render_template('insert_to_lookup_table_popup.html', name='Due Date Reason', table_name='due_date_reasons')

@app.route('/create_due_date_reasons', methods=['POST'])
def create_due_date_reason():
    """Create a new due date reason in the database"""
    # log the ip address of the request
    logger.info(f'serving /create_due_date_reason request from {request.remote_addr}')
    # parse request data
    new_due_date_reason = request.form['due_date_reasons_name']
    new_description = request.form['due_date_reasons_description']
    # initialize the Roles object
    due_date_reason = DueDateReason(app_data_path)
    due_date_reason.insert(new_due_date_reason, new_description)
    return redirect(url_for('serve_main'))

# test endpoint for sending misc html
@app.route('/test', methods=['GET'])
def serve_test():
    return send_from_directory('static', 'sample_popup.html')

if __name__ == '__main__':
    app.run(host=host_addr, port=host_port, debug=True)

