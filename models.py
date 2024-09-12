# ... (previous imports and code remain the same)

class GardenTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task = db.Column(db.String(200), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref=db.backref('garden_tasks', lazy=True))

# ... (rest of the file remains the same)
