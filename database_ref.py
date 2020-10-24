class Ideas(db.Model):

    __tablename__ = 'ideas'

    id = db.Column(db.Integer, primary_key=True)
    heading = db.Column(db.Text)
    idea_text = db.Column(db.Text)

    images = db.relationship('Images', cascade="all,delete", backref='idea', lazy='dynamic')
    external_images = db.relationship('ExternalImages', cascade="all,delete", backref='idea', lazy="dynamic")
    def __init__(self, heading, idea_text):
        self.heading = heading 
        self.idea_text = idea_text
    
class Images(db.Model):

    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String)
    idea_id = db.Column(db.Integer, db.ForeignKey('ideas.id'))

    def __init__(self, image_path, idea_id):
        self.image_path = image_path
        self.idea_id = idea_id

class ExternalImages(db.Model):
    __tablename__ = 'external_images'

    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String)
    idea_id = db.Column(db.Integer, db.ForeignKey('ideas.id'))

    def __init__(self, image_path, idea_id):
        self.image_path = image_path
        self.idea_id = idea_id
