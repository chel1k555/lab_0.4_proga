from flask import Flask, request, jsonify
from models import data_base, country, tank, tank_ammo, ammo_type

def create():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lab_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    data_base.init_app(app)

    with app.app_context():
        data_base.create_all()

        if not ammo_type.query.first():
            default_ammo = [
                ammo_type(name="фугасный"),
                ammo_type(name="кумулятивный"),
                ammo_type(name="подкалиберный"),
                ammo_type(name="осколочно-фугасный")
            ]
            data_base.session.add_all(default_ammo)
            data_base.session.commit()


 #GET


    @app.route('/api/countries', methods=['GET'])
    def get_count():
        try:
            countries = country.query.all()
            if countries is None:
                return jsonify({"warning": "countries not found or not added"}), 404
            else:
                return jsonify([count.to_dict() for count in countries]), 200
        except Exception as exp:
            return jsonify({"status": 500, "reason": str(exp)}), 500
    
    @app.route('/api/countries/<int:id>', methods=['GET'])
    def get_one_country(id):
        try:
            count = country.query.get(id)
            if count is None:
                return jsonify({"error": " country not found"}), 404
            else:
                return jsonify(count.to_dict()), 200
        except Exception as exp:
            return jsonify({"status": 500, "reason": str(exp)}), 500
        
    @app.route('/api/tanks', methods=['GET'])
    def get_all_t():
        try:
            country_id = request.args.get('country_id')
            
            if country_id:
                if not country.query.get(country_id):
                    return jsonify({"error": "country not found"}), 404
                tanks_list = tank.query.filter_by(country_id=country_id).all()
            else:
                tanks_list = tank.query.all()
                
            return jsonify([t.to_dict(on_off_ammo=False) for t in tanks_list]), 200
        except Exception as e:
            return jsonify({"status": 500, "reason": str(e)}), 500
        
    @app.route('/api/tanks/<int:tank_id>', methods=['GET'])
    def get_one_tank(tank_id):
        try:
            tankes = tank.query.get(tank_id)
            if tankes is None:
                return jsonify({"warning": "tanks not found or not added"}), 404
            else:
                return jsonify(tankes.to_dict(on_off_ammo=True)), 200
        except Exception as exp:
            return jsonify({"status": 500, "reason": str(exp)}), 500
        
    @app.route('/api/ammunition-types', methods=['GET'])
    def get_ammo_types():
        try:
            types = ammo_type.query.all()
            return jsonify([typ.to_dict() for typ in types]), 200
        except Exception as e:
            return jsonify({"status": 500, "reason": str(e)}), 500


#POST


    @app.route('/api/countries', methods=['POST'])
    def create_country():
        try:
            data = request.get_json()
            
            if not data or 'name' not in data:
                return jsonify({"error": "feild 'name' is required"}), 400
            
            exist = country.query.filter_by(name=data['name']).first()
            if exist:
                return jsonify({"error": "country with this name was added before"}), 400
        
            new_country = country(name=data['name'])
            data_base.session.add(new_country)
            data_base.session.commit()

            return jsonify(new_country.to_dict()), 200
        except Exception as e:
            data_base.session.rollback()
            return jsonify({"status": 500, "reason": str(e)}), 500
        
    @app.route('/api/tanks', methods=['POST'])
    def create_tank():
        try:
            data = request.get_json()
            
            required_fields = ['tank_model', 'caliber', 'crew', 'forward_speed', 'backward_speed', 'baraban', 'country_id']
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"field '{field}' is required"}), 400
            
            if not country.query.get(data['country_id']):
                return jsonify({"error": "country not found"}), 404
            
            existing_tank = tank.query.filter_by(
                tank_model=data['tank_model'],
                country_id=data['country_id']
            ).first()
            if existing_tank:
                return jsonify({"error": "this model of tank was already added in this country"}), 400
            
            new_tank = tank(
                tank_model=data['tank_model'],
                caliber=data['caliber'],
                crew=data['crew'],
                forward_speed=data.get('forward_speed'),
                backward_speed=data.get('backward_speed'),
                baraban=data.get('baraban'),
                country_id=data['country_id']
            )
            
            data_base.session.add(new_tank)
            data_base.session.commit()
            return jsonify([new_tank.to_dict()]), 200
        except Exception as e:
            data_base.session.rollback()
            return jsonify({"status": 500, "reason": str(e)}), 500
        
#PATCH


    @app.route('/api/countries/<int:id>', methods=['PATCH'])
    def update_country(id):
        try:
            count = country.query.get(id)
            if count is None:
                return jsonify({"error": "country not found"}), 404
            
            data = request.get_json()
            if 'name' in data:
                existing_country = country.query.filter_by(name=data['name']).first()
                if existing_country and existing_country.id != id:
                    return jsonify({"error": "country with this name already exists"}), 400
                count.name = data['name']
            
            data_base.session.commit()
            return jsonify(count.to_dict()), 200
        except Exception as e:
            data_base.session.rollback()
            return jsonify({"status": 500, "reason": str(e)}), 500

    @app.route('/api/tanks/<int:tank_id>', methods=['PATCH'])
    def update_tank(tank_id):
        try:
            tank_obj = tank.query.get(tank_id)
            if tank_obj is None:
                return jsonify({"error": "tank not found"}), 404
            
            data = request.get_json()

            if 'tank_model' in data:
                tank_obj.tank_model = data['tank_model']
            if 'caliber' in data:
                tank_obj.caliber = data['caliber']
            if 'crew' in data:
                tank_obj.crew = data['crew']
            if 'forward_speed' in data:
                tank_obj.forward_speed = data['forward_speed']
            if 'backward_speed' in data:
                tank_obj.backward_speed = data['backward_speed']
            if 'baraban' in data:
                tank_obj.baraban = data['baraban']
            if 'country_id' in data:
                tank_obj.country_id = data['country_id']
            
            data_base.session.commit()
            return jsonify(tank_obj.to_dict()), 200
        except Exception as e:
            data_base.session.rollback()
            return jsonify({"status": 500, "reason": str(e)}), 500
        

#DELETE


    @app.route('/api/countries/<int:id>', methods=['DELETE'])
    def delete_country(id):
        try:
            count = country.query.get(id)

            if count is None:
                return jsonify({"error": "country not found"}), 404
            
            if count.tanks:
                return jsonify({"error": "you can't delete country with tanks"}), 400
            else:
                data_base.session.delete(count)
                data_base.session.commit()
                return jsonify({"message": "country deleted succesful"}), 202
        except Exception as exp:
            data_base.session.rollback()
            return jsonify({"status": 500, "reason": str(exp)}), 500
        
    @app.route('/api/tanks/<int:tank_id>', methods=['DELETE'])
    def delete_tank(tank_id):
        try:
            tankes = tank.query.get(tank_id)
            
            if tankes is None:
                return jsonify({"error": "tank not found"}), 404
            else:
                data_base.session.delete(tankes)
                data_base.session.commit()
                return jsonify({"message": "tank already deleted"}), 202
        except Exception as exp:
            data_base.session.rollback()
            return jsonify({"error": 500, "reason": str(exp)}), 500
        

    @app.route('/api/ammunition-types', methods=['POST', 'PUT', 'PATCH', 'DELETE'])
    @app.route('/api/ammunition-types/<int:type_id>', methods=['POST', 'PUT', 'PATCH', 'DELETE'])
    def ammunition_types_not_allowed():
        return jsonify({"status": 500, "reason": "u can't modify ammo types"}), 500
    
    return app

app = create()

if __name__ == '__main__':
    app.run(debug=False)
