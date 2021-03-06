# -*- coding: utf-8 -*-
from datetime import datetime

#Utilizes the rating plugin
from plugin_rating_widget import RatingWidget
db.define_table('rate',
    Field('rating', 'integer',
          requires=IS_IN_SET(range(1,6)), # "requires" is necessary for the rating widget
))

CATEGORY = ['Long-term', 'Short-term']

#register in events table
db.define_table('register',
                Field('name'),
                Field('event_name'),
                Field('user_id', db.auth_user),
                Field('phone'),
                Field('email'),
                Field('category'),
                Field('start_time_new', 'datetime', required=True),
                Field('end_time_new','datetime', required = True),
                Field('date_posted', 'datetime'),
                Field('prof_pic', 'upload'),
                Field('description'),
                Field('attend', 'boolean', default=False, readable=False, writable=False),
                Field('rating', 'double', readable=True, writable=False),
                )

# Receives the logged in user's name
def get_first_name():
    name = 'Unidentified user'
    if auth.user:
        name = auth.user.first_name
    return name

# Receives the logged in user's email
def get_first_email():
    email = 'None'
    if auth.user:
        email = auth.user.email
    return email

#used by attending
def get_user_attending_info():
    value = 'None'
    if auth.user:
        value = auth.user.id
    return value

#used by history
def get_user_info():
    value = 'None'
    if auth.user:
        value = auth.user.id
    return value

# The attending table, which stores information about which events users are attending.
db.define_table('attending',
                Field('user_attending', db.auth_user),
                Field('event_name','reference register'), #joins register table
                Field('attended', 'boolean'),
                Field('rating', 'integer', writable=False, readable=False, requires=IS_IN_SET(range(1,6))),
                )

# The ratings table, which stores information about the ratings each event received.
db.define_table('ratings',
                Field('event_name', 'reference register'),
                Field('attended', 'reference attending', writable=False, readable=False),
                Field('rating', 'integer', requires=IS_IN_SET(range(1,6))),
                 )

# Calls the rating plugin.
db.ratings.rating.widget = RatingWidget()

# The messaging table, which is used to send messages to other users.
db.define_table('messaging',
                Field('user_sender', db.auth_user),
                Field('user_recipient', db.auth_user),
                Field('message_body','text'),
                Field('read_status','boolean',default=False),
                Field('time_of_sending','datetime',default = datetime.utcnow())
                )

# Attending table validators.
db.attending.event_name.requires = IS_EMPTY_OR(IS_IN_DB(db(db.register), 'register.id', '%(event_name)s'))
db.attending.user_attending.writable = False
db.attending.user_attending.readable = False
db.attending.user_attending.default = get_user_attending_info()
db.attending.attended.default = False

# Ratings table validators.
db.ratings.rating.writable = False
db.ratings.rating.readable = False
db.ratings.event_name.requires = IS_EMPTY_OR(IS_IN_DB(db(db.register), 'register.id', '%(event_name)s'))
if db.attending.attended == True:
    db.ratings.rating.writable = True
    db.ratings.rating.readable = True

# Messaging table validators.
db.messaging.user_recipient.requires = IS_EMPTY_OR(IS_IN_DB(db(db.auth_user), 'auth_user.id', '%(first_name)s'))
db.messaging.user_sender.writable = False
db.messaging.user_sender.default = get_user_info()

# Register table validators.
db.register.id.readable = False
db.register.date_posted.default = datetime.utcnow()
db.register.date_posted.writable = False
db.register.name.default = get_first_name()
db.register.email.default = get_first_email()
db.register.user_id.default = auth.user_id
db.register.user_id.writable = db.register.user_id.readable = False
db.register.email.requires = IS_EMAIL()
db.register.category.requires = IS_IN_SET(CATEGORY,zero=None)
db.register.category.default = 'Misc.'
db.register.category.required = True
db.register.phone.requires = IS_MATCH('^1?((-)\d{3}-?|\(\d{3}\))\d{3}-?\d{4}$',
         error_message='not a phone number')
