import pytest
import json
from main import app, data_base
from models import country, tank, tank_ammo, ammo_type

def stokovoe_base():
    with app.app_context():
        data_base.drop_all()
        data_base.create_all()
        base_country = country(name="Russia")
        data_base.session.add(base_country)


        base_tank = tank(tank_model="Т-90М (Прорыв)", caliber=125, crew=3, forward_speed=70, backward_speed=-4, baraban=22, country_id=1)
        data_base.session.add(base_tank)
        data_base.session.commit()

def clean():
    with app.app_context():
        data_base.drop_all()

def test_get_countries():
    stokovoe_base()

    with app.test_client() as client:
        response = client.get('/api/countries')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['name'] == "Russia"

    clean()

def test_get_country_by_id():
    stokovoe_base()
    
    with app.test_client() as client:
        response = client.get('/api/countries/1')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == "Russia"
        assert data['id'] == 1
    
    clean()

def test_create_country():
    stokovoe_base()

    with app.test_client() as client:
        
        new_country = {'name': 'USA'}
        response = client.post('/api/countries', json=new_country, content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'USA'
        
        response = client.get('/api/countries')
        data = json.loads(response.data)
        assert len(data) == 2

        new_country = {'name': 'Germany'}
        response = client.post('/api/countries', json=new_country, content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'Germany'

        response = client.get('/api/countries')
        data = json.loads(response.data)
        assert len(data) == 3
        country_names = [country['name'] for country in data]
        assert 'Russia' in country_names
        assert 'USA' in country_names
        assert 'Germany' in country_names

    clean()

def test_create_same_country():
    stokovoe_base()
    
    with app.test_client() as client:
        duplicate_country = {'name': 'Russia'}
        response = client.post('/api/countries', json=duplicate_country, content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'country with this name was added before' in data['error']
    
    clean()

def test_delete_country():
    stokovoe_base()
    
    with app.test_client() as client:
        response = client.get('/api/countries/1')
        assert response.status_code == 200
        
        response = client.delete('/api/countries/1')
        assert response.status_code == 202
        
        response = client.get('/api/countries/1')
        assert response.status_code == 404
    
    clean()

def test_delete_country_with_tanks():
    stokovoe_base()
    
    with app.test_client() as client:
        response = client.delete('/api/countries/1')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'you can\'t delete country with tanks' in data['error']
        
        response = client.get('/api/countries/1')
        assert response.status_code == 200
    
    clean()

def test_get_tanks():
    stokovoe_base()
    
    with app.test_client() as client:
        response = client.get('/api/tanks')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data['model'] == "Т-90М (Прорыв)"
        assert data['caliber'] == 125
        assert data['crew count'] == 3
        assert data['shell drum'] == 22
        assert data['speed forward'] == 70
        assert data['speed back'] == -4
    
    clean()

def test_get_tank_by_id():
    stokovoe_base()
    
    with app.test_client() as client:
        response = client.get('/api/tanks/1')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['model'] == "Т-90М (Прорыв)"
        assert data['caliber'] == 125
        assert data['crew count'] == 3
        assert data['shell drum'] == 22
        assert data['speed forward'] == 70
        assert data['speed back'] == -4
    
    clean()

def test_create_tank():
    stokovoe_base()
        
    with app.test_client() as client:

        new_country = {'name': 'USA'}
        response = client.post('/api/countries', json=new_country, content_type='application/json')

        new_tank = {
            'tank_model': 'M1A4 Abrams',
            'caliber': 120,
            'crew': 4,
            'forward_speed': 67,
            'backward_speed': -18,
            'baraban': 42,
            'country_id': 2
        }
        response = client.post('/api/tanks/', json=new_tank, content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data[0]['model'] == "M1A4 Abrams"
        assert data[0]['caliber'] == 120
        assert data[0]['crew count'] == 4
        assert data[0]['shell drum'] == 42
        assert data[0]['speed forward'] == 67
        assert data[0]['speed back'] == -18
        
        response = client.get('/api/tanks')
        data = json.loads(response.data)
        assert len(data) == 2
    
    clean()

def test_update_tank():
    stokovoe_base()
    
    with app.test_client() as client:
        update_data = {'model': "Т-80БВМ", 'forward_speed': 75, 'backward_speed': -14}
        response = client.patch('/api/tanks/1', json=update_data, content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['model'] == 'Т-80БВМ'
        assert data['speed forward'] == 75
        assert data['caliber'] == 125
        assert data['speed back'] == -14
    
    clean()

def test_delete_tank():
    stokovoe_base()
    
    with app.test_client() as client:
        response = client.get('/api/tanks/1')
        assert response.status_code == 200
        
        response = client.delete('/api/tanks/1')
        assert response.status_code == 202
        
        response = client.get('/api/tanks/1')
        assert response.status_code == 404
    
    clean()
