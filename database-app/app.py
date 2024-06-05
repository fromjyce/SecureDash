from flask import Flask, render_template, request
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Jayas1709#'
app.config['MYSQL_DB'] = 'securedash'

mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start_timestamp = request.form.get('start_timestamp')
        end_timestamp = request.form.get('end_timestamp')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM packet_data WHERE timestamp BETWEEN %s AND %s ORDER BY timestamp DESC", (start_timestamp, end_timestamp))
        data = cur.fetchall()
        cur.close()
        return render_template('index.html', data=data)
    else:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM packet_data ORDER BY timestamp DESC")
        data = cur.fetchall()
        cur.close()
        return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
