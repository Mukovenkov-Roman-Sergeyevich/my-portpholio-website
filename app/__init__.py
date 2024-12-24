from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mysql+mysqlconnector://romanmukovenkov:MY_PASSWORD@'
    'romanmukovenkov.mysql.pythonanywhere-services.com/'
    'romanmukovenkov$default'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Like(db.Model):
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(255), nullable=False)
    user_email = db.Column(db.String(255), nullable=False)

    __table_args__ = (db.UniqueConstraint('page', 'user_email', name='uix_page_user_email'),)

    def __repr__(self):
        return f"<Like id={self.id}, page={self.page}, user_email={self.user_email}>"

app.config['GOOGLE_CLIENT_ID'] = 'MY_GOOGLE_CLIENT_ID'
app.config['GOOGLE_CLIENT_SECRET'] = 'MY_CLIENT_GOOGLE_SECRET'
app.config['GOOGLE_REDIRECT_URI'] = 'https://romanmukovenkov.pythonanywhere.com/google/authorized'

app.config['GITHUB_CLIENT_ID'] = 'MY_GITHUB_CLIENT_ID'
app.config['GITHUB_CLIENT_SECRET'] = 'MY_CLIENT_GITHUB_SECRET'
app.config['GITHUB_REDIRECT_URI'] = 'https://romanmukovenkov.pythonanywhere.com/github/authorized'

from . import routes

application = app
