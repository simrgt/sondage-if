from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id, login, password):
        self.id = id
        self.login = login
        self.password = password

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.login, self.password)