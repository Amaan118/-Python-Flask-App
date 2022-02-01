from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import json
from datetime import datetime


app = Flask(__name__)

with open('config.json') as f:
    data = json.loads(f.read())

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = data['user_mail']
app.config['MAIL_PASSWORD'] = data['user_password']
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)
app.secret_key = data['secret_key']
app.config['SESSION_TYPE'] = 'filesystem'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class DataAdd(db.Model):
    srno = db.Column(db.Integer, primary_key=True)
    reg_no = db.Column(db.String(10), nullable=False)
    sgpa = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self) -> str:
        return f"{self.srno}. {self.reg_no}"


@app.route('/', methods=['GET', 'POST'])
def home_page():
    if request.method == 'POST':
        r = request.form['registeration']
        c = request.form['sgpa']
        s = request.form['sem']

        if r.strip() == '' or c.strip() == '' or int(s) > 8:
            return redirect('/add')

        data = DataAdd(reg_no=r, sgpa=c, semester=s)
        db.session.add(data)
        db.session.commit()

    post = DataAdd.query.all()
    return render_template('index.html', posts=post)


@app.route('/home')
def home_end():
    return render_template('home.html')


@app.route('/add')
def add():
    return render_template('add.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['contact']
        descript = request.form['desc']

        try:
            mail.send_message('SGPA App Feedback from ' + name,
                              sender=email, recipients=[
                                  data['user_recipient']],
                              body='Description : ' + descript + '\nContact Details : ' + phone + '\nSender Email : ' + email)

            flash(
                'Thank You for the Feedback. We will reach out to you soon !', 'success')

        except:
            flash(
                'Sorry there is a problem at the moment. Please try after sometime.', 'danger')

    return render_template('contact.html')


@app.route('/reset/<int:num>')
def reset(num):
    query = DataAdd.query.filter_by(srno=num).first()
    query.sgpa = 0
    db.session.commit()

    return redirect('/')


@app.route('/update/<int:num>', methods=['GET', 'POST'])
def update(num):
    if request.method == 'POST':
        r = request.form['update_reg']
        c = request.form['update_sgpa']
        s = request.form['update_sem']

        query = DataAdd.query.filter_by(srno=num).first()
        query.reg_no = r
        query.sgpa = c
        query.semester = s

        db.session.add(query)
        db.session.commit()
        return redirect('/')

    query = DataAdd.query.filter_by(srno=num).first()
    return render_template('update.html', update_data=query)


@app.route('/delete/<int:num>')
def delete(num):
    query = DataAdd.query.filter_by(srno=num).first()
    db.session.delete(query)
    db.session.commit()

    return redirect('/')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        tbs = request.form['search_data']

        queries = DataAdd.query.all()
        return render_template('search.html', search_data=queries, to_be_search=tbs)


if __name__ == "__main__":
    app.run(debug=False)
