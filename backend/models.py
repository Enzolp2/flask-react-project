from exts import db

"""
-------- User model

class User:
    id: int primary key
    username: str
    password: str
"""

class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(25), nullable=False, unique=True)
    password = db.Column(db.String(25), nullable=False)

    def __repr__(self) -> str:
        return f"\nUsername: {self.username})\n"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self, username, password):
        self.username = username
        self.password = password
        self.save()

"""
-------- Ticket model

class Ticket:
    id: integer
    title: string
    content: string
"""

class Ticket(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text(), nullable=False)

    def __repr__(self) -> str:
        return f"\nTicket: {self.id} - {self.title}\n"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self, title, content):
        self.title = title
        self.content = content
        self.save()