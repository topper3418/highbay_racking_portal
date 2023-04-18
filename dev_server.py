from flask import Flask, render_template, request, redirect
import data.db

# define the app
app = Flask(__name__)
db = data.db.database('testing.db')

@app.route("/")
def index():
  html_content = render_template("index.html", color='rgb(255, 255, 255))')
  return html_content

@app.route('/<table_name>_insert', methods=['GET', 'POST'])
def insert_form(table_name):
    name_column_name = db[table_name].name_column_name

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        # Insert the data into the database
        db.default_insert(table_name, [name, description])
        # print the table to show the data was inserted
        print(db.read_table(table_name))
        # Redirect to the main page
        return redirect('Congrats you did it now go to bed and pick this up tomorrow evening')
    else:
        return render_template(f'insert_to_lookup_table_popup.html', table_name=table_name, name_column_name=name_column_name)

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5001, debug=True)