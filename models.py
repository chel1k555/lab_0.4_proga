from flask_sqlalchemy import SQLAlchemy

data_base = SQLAlchemy()

class country(data_base.Model):
    __tablename__ = "countries"

    id = data_base.Column(data_base.Integer, primary_key=True)
    name = data_base.Column(data_base.String(100), nullable=False)
    tanks = data_base.relationship('tank', backref='country', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }
    


class tank(data_base.Model):
    __tablename__ = "tanks"

    tank_id = data_base.Column(data_base.Integer, primary_key=True)
    caliber = data_base.Column(data_base.Integer)
    tank_model = data_base.Column(data_base.String(20), nullable=False)
    crew = data_base.Column(data_base.Integer)
    forward_speed = data_base.Column(data_base.Integer)
    backward_speed = data_base.Column(data_base.Integer)
    baraban = data_base.Column(data_base.Integer)
    country_id = data_base.Column(data_base.Integer, data_base.ForeignKey("countries.id"))
    ammo = data_base.relationship('tank_ammo', backref='tank', lazy=True)

    def to_dict(self, on_off_ammo=False):
        info = {
            "tank_id": self.tank_id,
            "caliber": self.caliber,
            "model": self.tank_model,
            "crew count": self.crew,
            "shell drum": self.baraban,
            "speed forward": self.forward_speed,
            "speed back": self.backward_speed,
            "country id": self.country_id
        }
        if on_off_ammo:
            info['ammunition'] = [ammu.to_dict for ammu in self.ammo]
        return info



class ammo_type(data_base.Model):
    __tablename__ = 'ammunition_types'
    id = data_base.Column(data_base.Integer, primary_key=True)
    name = data_base.Column(data_base.String(50), nullable=False, unique=True)

    def to_dict(self):
        return {
            'ammo_id': self.id,
            'name': self.name
        }
    
    def update(self, **kwargs):
        raise ValueError("System ammunition types cannot be modified")



class tank_ammo(data_base.Model):
    __tablename__ = 'tank_ammunition'
    id = data_base.Column(data_base.Integer, primary_key=True)
    tank_id = data_base.Column(data_base.Integer, data_base.ForeignKey('tanks.tank_id'))
    ammunition_id = data_base.Column(data_base.Integer, data_base.ForeignKey('ammunition_types.id'))
    ammunition_type = data_base.relationship('ammo_type', backref='tank_ammunition')

    def to_dict(self):
        return {
            'id': self.id,
            'tank_id': self.tank_id,
            'ammunition_id': self.ammunition_id,
            'count': self.count,
            'type_name': self.ammunition_type.name
        }