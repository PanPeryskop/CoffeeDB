import os
import requests
import json
from flask import Flask, render_template, request, redirect, url_for, session, flash
import random

app = Flask(__name__)
app.secret_key = 'change_this_key'

# Base API URL (Go server)
API_BASE = 'http://srv17.mikr.us:40331'

# Geocoding API setup (using Nominatim/OpenStreetMap)
GEOCODING_API = "https://nominatim.openstreetmap.org/search"
GEOCODING_HEADERS = {
    "User-Agent": "CoffeeBaseApp/1.0",
    "Accept": "application/json"
}

def get_auth_headers():
    token = session.get('jwt_token')
    print(token)
    if token:
        return {'Authorization': f'Bearer {token}'}
    return {}


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        data = {"username": username, "passwords": password}
        resp = requests.post(f"{API_BASE}/login", json=data)
        if resp.ok:
            token = resp.json().get('token')
            session['jwt_token'] = token
            flash("Successfully logged in")
            return redirect(url_for('index'))
        else:
            flash("Invalid login credentials")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = {
            "username": request.form.get('username'),
            "password": request.form.get('password'),
            "email": request.form.get('email')
        }
        resp = requests.post(f"{API_BASE}/register", json=data)
        if resp.ok:
            flash("Registration successful, you can now log in.")
            return redirect(url_for('login'))
        else:
            flash("Registration failed: " + resp.text)
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('jwt_token', None)
    flash("Logged out")
    return redirect(url_for('index'))

@app.route('/coffees')
def coffees():
    resp = requests.get(f"{API_BASE}/coffees")
    coffees_list = resp.json() if resp.ok else []
    return render_template('coffees.html', coffees=coffees_list)

@app.route('/coffee/<int:coffee_id>')
def get_coffee(coffee_id):
    resp = requests.get(f"{API_BASE}/coffees/{coffee_id}")
    if resp.ok:
        coffee = resp.json()
        
        if coffee.get('roasteryId'):
            roastery_resp = requests.get(f"{API_BASE}/roasteries/{coffee['roasteryId']}")
            if roastery_resp.ok:
                roastery = roastery_resp.json()
                coffee['roasteryName'] = roastery['name']
                # Możemy też dodać więcej informacji o palarni, jeśli potrzebne
                coffee['roasteryCountry'] = roastery['country']
                coffee['roasteryCity'] = roastery['city']
        
        return render_template('coffee_detail.html', coffee=coffee)
    else:
        flash("Coffee not found")
        return redirect(url_for('coffees'))

@app.route('/coffees/create', methods=['GET', 'POST'])
def create_coffee():
    if request.method == 'POST':
        coffee = {
            "name": request.form.get('name'),
            "country": request.form.get('country'),
            "process": request.form.get('process'),
            "roastProfile": request.form.get('roastProfile'),
            "flavourNotes": [note.strip() for note in request.form.get('flavourNotes', '').split(',') if note.strip()],
            "description": request.form.get('description'),
            "roasteryId": int(request.form.get('roasteryId', '0'))
        }
        headers = get_auth_headers()
        resp = requests.post(f"{API_BASE}/coffees", json=coffee, headers=headers)
        if resp.ok:
            flash("Coffee added")
            return redirect(url_for('coffees'))
        else:
            flash("Error adding coffee: " + resp.text)
    return render_template('coffee_form.html', coffee=None)

@app.route('/shop/<int:shop_id>')
def get_shop(shop_id):
    resp = requests.get(f"{API_BASE}/shops/{shop_id}")
    if resp.ok:
        shop = resp.json()
        shop["lng"] = shop.pop("lon")
        
        return render_template('shop_details.html', shop=shop)
    else:
        flash("Coffee shop not found", "error")
        return redirect(url_for('shops'))

@app.route('/roasteries')
def roasteries():
    resp = requests.get(f"{API_BASE}/roasteries")
    roasteries_list = resp.json() if resp.ok else []
    
    for roastery in roasteries_list:
        if roastery.get("lat") and roastery.get("lng"):
            continue

        lng = roastery.pop("lon")
        roastery["lng"] = lng

    return render_template('roasteries.html', roasteries=roasteries_list)

@app.route('/roastery/<int:roastery_id>')
def get_roastery(roastery_id):
    resp = requests.get(f"{API_BASE}/roasteries/{roastery_id}")
    if resp.ok:
        roastery = resp.json()
        
        coffees_resp = requests.get(f"{API_BASE}/coffees?roastery={roastery_id}")
        roastery_coffees = coffees_resp.json() if coffees_resp.ok else []

        roastery["lng"] = roastery.pop("lon")
        
        return render_template('roastery_detail.html', roastery=roastery, coffees=roastery_coffees)
    else:
        flash("Roastery not found")
        return redirect(url_for('roasteries'))

@app.route('/shops')
def shops():
    resp = requests.get(f"{API_BASE}/shops")
    shops_list = resp.json() if resp.ok else []
    
    for shop in shops_list:

        if shop.get("lat") and shop.get("lng"):
            continue

        lng = shop.pop("lon")
        shop["lng"] = lng    
        
    
    return render_template('shops.html', shops=shops_list)

@app.route('/reviews')
def reviews():
    resp = requests.get(f"{API_BASE}/reviews")
    lst = resp.json() if resp.ok else []
    return render_template('reviews.html', reviews=lst)

@app.route('/reviews/create', methods=['GET', 'POST'])
def create_review():
    if request.method == 'POST':
        selected_type = request.form.get('review-type')
        review_data = {
            "review": request.form.get('review'),
            "rating": float(request.form.get('rating') or 0)
        }
        
        if selected_type == 'coffee':
            coffee_id = request.form.get('coffeeId')
            if coffee_id:
                review_data["coffeeId"] = int(coffee_id)
        elif selected_type == 'roastery':
            roastery_id = request.form.get('roasteryId')
            if roastery_id:
                review_data["roasteryId"] = int(roastery_id)
        elif selected_type == 'shop':
            shop_id = request.form.get('coffeeShopId')
            if shop_id:
                review_data["coffeeShopId"] = int(shop_id)
        
        headers = get_auth_headers()
        
        try:
            resp = requests.post(f"{API_BASE}/reviews", json=review_data, headers=headers)
            if resp.ok:
                flash("Review added successfully", "success")
                return redirect(url_for('reviews'))
            else:
                flash(f"Error adding review: {resp.text}", "error")
                return render_template('review_form.html')
        except Exception as e:
            flash(f"Error adding review: {str(e)}", "error")
            return render_template('review_form.html')
    
    return render_template('review_form.html')

@app.route('/reviews/delete/<int:review_id>', methods=['POST'])
def delete_review(review_id):
    token = request.form.get('token') or session.get('jwt_token')
    if not token:
        flash("Authentication required", "error")
        return redirect(url_for('reviews'))
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    try:
        resp = requests.delete(f"{API_BASE}/reviews/{review_id}", headers=headers)
        if resp.ok:
            flash("Review deleted successfully", "success")
        else:
            flash(f"Error deleting review: {resp.text}", "error")
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
    
    return redirect(url_for('reviews'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 40330))
    app.run(host="0.0.0.0", port=port, debug=False)