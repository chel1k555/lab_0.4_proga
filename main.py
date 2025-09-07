from flask import Flask, request, jsonify
from models import data_base, country, tank, tank_ammo, ammo_type

def create():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lab_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    data_base.init_app(app)

    with app.app_contect():
        data_base.create_all()

        if not ammo_type.query.first():
            default_ammo = [
                ammo_type(name="фугасный"),
                ammo_type(name="кумулятивный"),
                ammo_type(name="подкалиберный"),
                ammo_type(name="осколочно-фугасный")
            ]
            data_base.session.add_all(default_ammo)
            data_base.commit()


 #GET


    @app.route('/api/countries', methods=['GET'])
    def get_count():
        try:
            countries = country.query.all()
            return jsonify([count.to_dict for count in countries]), 200
        except Exception as exp:
            if countries is None:
                return jsonify({"error": "countries not found"}), 404
            else:
                return jsonify({"status": 500, "reason": str(exp)}), 500
    
    @app.route('/api/countries/')