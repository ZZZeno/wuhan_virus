from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ProvView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    added_time = db.Column(db.String(64))

    prov = db.Column(db.String(32))
    for_sure = db.Column(db.Integer)
    cured = db.Column(db.Integer)
    dead = db.Column(db.Integer)

    def __init__(self, added_time, prov, for_sure, cured, dead):
        self.added_time = added_time
        self.prov = prov
        self.for_sure = for_sure
        self.cured = cured
        self.dead = dead

class TotalView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    added_time = db.Column(db.String(64))

    sure = db.Column(db.Integer)
    suspicion = db.Column(db.Integer)
    dead = db.Column(db.Integer)
    cured = db.Column(db.Integer)

    def __init__(self, added_time, sure, suspicion, dead, cured):
        self.added_time = added_time
        self.sure = sure
        self.suspicion = suspicion
        self.dead = dead
        self.cured = cured