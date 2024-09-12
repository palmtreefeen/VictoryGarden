# ... (previous imports and code remain the same)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_organic = db.Column(db.Boolean, default=False)
    tags = db.Column(db.String(200))

    seller = db.relationship('User', backref=db.backref('products', lazy=True))

    def calculate_total_price(self, buyer):
        if buyer.subscription_tier == 'free':
            fee_percentage = 0.04
        elif buyer.subscription_tier == 'pro':
            fee_percentage = 0.02
        else:  # premium tier
            fee_percentage = 0.01

        transaction_fee = self.price * fee_percentage
        return self.price + transaction_fee

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    fee = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    product = db.relationship('Product', backref=db.backref('transactions', lazy=True))
    buyer = db.relationship('User', foreign_keys=[buyer_id], backref=db.backref('purchases', lazy=True))
    seller = db.relationship('User', foreign_keys=[seller_id], backref=db.backref('sales', lazy=True))

# ... (rest of the file remains the same)
