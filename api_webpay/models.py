from __init__ import db

class State(db.Document):
	name = db.StringField(max_length=50, required=True)

	def __unicode__(self):
		return self.name

class Bill(db.Document):
	orden = db.IntField(default = 10000, required = True, primary_key = True)
	client_orden = db.IntField(required = True)
	session_id = db.StringField(max_length=200, required=True)
	amount = db.IntField(required = True)
	ip = db.StringField(max_length=15, required=True)
	state = db.ReferenceField(State)
	succ_url = db.URLField(required = True)
	fail_url = db.URLField(required = True)
	auth_code = db.IntField()
	trx_id = db.IntField()
	trx_date = db.DateTimeField()
	last_digits = db.IntField()
	tipo_cuota = db.StringField(max_length=200)
	num_cuota = db.IntField()
	message = db.StringField(max_length=200)

	meta = {
        'ordering': ['orden']
    }