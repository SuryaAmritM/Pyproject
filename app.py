import random
from flask import Flask, render_template, request, redirect, url_for, session, flash
import re
import json
from flask_sqlalchemy import SQLAlchemy  # Import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'supersecretkey'
    
# Sample Veg and Non-Veg Menu Options
veg_menu = [
    "Paneer Butter Masala", "Aloo Gobi", "Vegetable Biryani", "Veg Kurma", 
    "Saag Paneer", "Dal Makhani", "Chole", "Baingan Bharta", "Malai Kofta"
]

non_veg_menu = [
    "Chicken Curry", "Mutton Biryani", "Fish Fry", "Butter Chicken", 
    "Prawn Curry", "Egg Curry", "Chicken Biryani", "Chicken Tikka", "Rogan Josh"
]

# Validate phone and pincode
def is_valid_phone(phone):
    return re.fullmatch(r'^\d{10}$', phone)

def is_valid_pincode(pincode):
    return re.fullmatch(r'^\d{6}$', pincode)

# Step 1: Collect User Details (Name, Email, Phone, Address, City, Pincode)
@app.route('/', methods=['GET', 'POST'])
def step1():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        city = request.form['city']
        pincode = request.form['pincode']

        # Validate phone number and pincode
        if not is_valid_phone(phone):
            flash("Please enter a valid 10-digit phone number.", "error")
            return render_template('step1.html')

        if not is_valid_pincode(pincode):
            flash("Please enter a valid 6-digit postal code.", "error")
            return render_template('step1.html')

        # Store data in session
        session['name'] = name
        session['email'] = email
        session['phone'] = phone
        session['address'] = address
        session['city'] = city
        session['pincode'] = pincode

        return redirect(url_for('step2'))

    return render_template('step1.html')


# Step 2: Collect Day and Time Selection
@app.route('/step2', methods=['GET', 'POST'])
def step2():
    if request.method == 'POST':
        # Get selected days and times from form
        days = request.form.getlist('day')
        times = {day: request.form[f"time_{day}"] for day in days}

        # Ensure at least one day is selected
        if not days:
            flash("Please select at least one day and its time.", "error")
            return render_template('step2.html')

        # Store days and times in session
        session['days'] = days
        session['times'] = times

        return redirect(url_for('step3'))

    return render_template('step2.html')


# Select random food from the user's chosen items for each day
def select_random_food_for_each_day(selected_items, days):
    random_food_for_days = {}
    for day in days:
        random_food_for_days[day] = random.choice(selected_items)
    return random_food_for_days


# Step 3: Menu Selection and Random Food Assignment
@app.route('/step3', methods=['GET', 'POST'])
def step3():
    if request.method == 'POST':
        menu_type = request.form.get('menu_type')
        selected_items = request.form.getlist('food_items')

        if not menu_type:
            flash("Please select a menu type.", "error")
            return render_template('step3.html')

        if not selected_items:
            flash("Please select at least one food item.", "error")
            return render_template('step3.html')

        # Generate a random food item for each day
        random_foods = {}
        for day in session['days']:
            random_food = random.choice(selected_items)
            random_foods[day] = random_food

        # Store the random food items in the session
        session['random_food_for_days'] = random_foods

        return redirect(url_for('checkout'))
    else:
        return render_template('step3.html', veg_menu=veg_menu, non_veg_menu=non_veg_menu)


# Checkout page to display the final message with the random food for each day
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        action = request.form['action']
        if action == 'menu':
            return redirect(url_for('step3'))
        elif action == 'place_order':
            # Save the order to the database or file
            # ...
            return redirect(url_for('thank_you'))
        else:
            return render_template('success.html')  # or redirect to another route
    else:
        try:
            random_foods = session['random_food_for_days']
            return render_template('checkout.html',
                                   name=session['name'],
                                   email=session['email'],
                                   phone=session['phone'],
                                   address=session['address'],
                                   city=session['city'],
                                   pincode=session['pincode'],
                                   random_foods=random_foods)
        except KeyError:
            flash("Error retrieving order details. Please try again.", "error")
            return redirect(url_for('step1'))

@app.route('/thank_you')
def thank_you():
    return render_template('success.html')    

@app.route('/save_order')
def save_order():
    try:
        random_food_for_days = session['random_food_for_days']
        order_details = {
            'name': session['name'],
            'email': session['email'],
            'phone': session['phone'],
            'address': session['address'],
            'city': session['city'],
            'pincode': session['pincode'],
            'days': session['days'],
            'random_food_for_days': random_food_for_days
        }

        # Save the order to orders.json file
        with open('orders.json', 'a') as f:
            json.dump(order_details, f)
            f.write('\n')

        print("Order saved successfully!")
        flash("Order saved successfully!", "success")
        return redirect(url_for('step1'))
    except Exception as e:
        print(f"Error saving order: {e}")
        flash("Error saving order. Please try again.", "error")
        return redirect(url_for('step1'))

if __name__ == '__main__':
    app.run(debug=True)
