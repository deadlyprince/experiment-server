"""
Used as a base class for every model to ensure ORM-style.
Add new common orm-related functions here.
"""

DBSession = None

class ORM:
    @classmethod
    def query(class_):
        return DBSession.query(class_)

    @classmethod
    def get(class_, id):
        return DBSession.query(class_).get(id)

    @classmethod
    def all(class_):
        return DBSession.query(class_).all()

    @classmethod
    def save(cls, data):
        if data.id is None:
            DBSession.add(data)
        return DBSession.commit()

    @classmethod
    def destroy(cls, data):
        DBSession.delete(data)
        return DBSession.commit()