# coding: utf-8
"""
sql models

    use: Flask-SQLAlchemy
    -- http://flask-sqlalchemy.pocoo.org/2.1/

"""

from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin, current_user
from wtforms.validators import Email
from datetime import datetime
from markdown import markdown
from flask import url_for, current_app
from app.exceptions import ValidationError
import bleach


# permissions
class Permission:
    """
    1. COMMENT: 0x01
    2. MODERATE_COMMENTS: 0x02
    3. ADMINISTER: 0x04
    """
    COMMENT = 0x01
    MODERATE_COMMENTS = 0x02
    ADMINISTER = 0x04


# user roles
class Role(db.Model):
    """
    1. User: COMMENT
    2. Moderator: MODERATE_COMMENTS
    3. Administrator: ADMINISTER
    """
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.COMMENT, True),
            'Moderator': (Permission.COMMENT |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (
                Permission.COMMENT |
                Permission.MODERATE_COMMENTS |
                Permission.ADMINISTER,
                False
            )
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model, UserMixin):
    """user"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(164), unique=True, index=True)
    email = db.Column(db.String(164), info={'validator' : Email()})
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(164))

    @property
    def password(self):
        raise AttributeError('password is not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    def is_admin(self):
        if self.role_id == 2:
            return True
        return False

    def __repr__(self):
        return "<User %r>" % self.username


class AnonymousUser(AnonymousUserMixin):
    """ anonymous user """
    def is_admin(self):
        return False

login_manager.anonymous_user = AnonymousUser

class Base(object):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    bname = db.Column(db.Text)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    url = db.Column(db.Text)
    timestamp = db.Column(db.Text)
    author_name = db.Column(db.String(164))
    liked_count = db.Column(db.Integer, default=0)

    @staticmethod
    def on_changed_body(target, value, oldbalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))


class Movie(db.Model, Base):
    """movies"""
    __tablename__ = 'movies'
    tag = 'movie'

    def __repr__(self):
        return "<Movie %r>" % self.name


db.event.listen(Movie.body, 'set', Movie.on_changed_body)


class Anime(db.Model, Base):
    """animes"""
    __tablename__ = 'animes'
    tag = 'anime'

    def __repr__(self):
        return "<Anime %r>" % self.id


db.event.listen(Anime.body, 'set', Anime.on_changed_body)


class Article(db.Model, Base):
    """articles"""
    __tablename__ = 'articles'
    tag = 'article'

    def __repr__(self):
        return "<Article %r>" % self.id


db.event.listen(Article.body, 'set', Article.on_changed_body)


class Course(db.Model, Base):
    """courses"""
    __tablename__ = 'courses'
    tag = 'course'

    def __repr__(self):
        return "<Course %r>" % self.id


db.event.listen(Course.body, 'set', Course.on_changed_body)


class Photo(db.Model, Base):
    """photos"""
    __tablename__ = 'photos'
    tag = 'photo'

    def __repr__(self):
        return "<Photo %r>" % self.id


db.event.listen(Photo.body, 'set', Photo.on_changed_body)


class Notice(object):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(164))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return "<Notice %r>" % self.id
