from flask import Flask, render_template, request, redirect, url_for, flash ,get_flashed_messages
from static import food_list
import json
import os
from flask import Flask, jsonify
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static')

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

items = food_list

data = supabase.table("user_profiles").select("*").execute()
data = data.data

user_name = None
@app.route('/')
def index():
    return render_template('navbar.html', user_name=user_name)

@app.route('/products')
def products():
    category = request.form.get('category')
    print(category)
    products_list = list(enumerate(items))
    return render_template('products.html', item=products_list, user_name=user_name)

@app.route('/add_cart/<int:item_index>')
def add_cart(item_index):
    global user_name
    prodcut = list(enumerate(items))

    try:
        if user_name == None:
            flash("First you need to login first:")
            return redirect(url_for("login"))
        else:
            flash("sucessful")
    except Exception as e:
        flash("Error: " + str(e))
    return render_template('products.html', item=prodcut, user_name=user_name)

@app.route('/logout')
def logout():
    global user_name
    user_name = None
    return render_template('login.html', user_name=user_name)


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login_verify', methods=['POST'])
def login_verify():
    global user_name
    if request.method == 'POST':
        user_email = request.form.get('email')
        user_password = request.form.get('password')

        try:
            result = supabase.table("user_profiles").select("email_id, password, name").eq("email_id", user_email).execute()
            result = result.data

            if result:
                row = result[0]
                if user_email == row["email_id"] and user_password == row["password"]:
                    flash("Login Successful")
                    user_name = row["name"]
                    return redirect(url_for('index'))
                elif user_email == row["email_id"] and user_password != row["password"]:
                    flash("Password wrong")
                    return redirect(url_for('login'))
            else:
                flash("user not found: if you have not account please create account first:")
                return redirect(url_for("signup"))
        except Exception as e:
            flash("error: " + str(e))
            return redirect(url_for("login"))
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/insert_user', methods=['POST'])
def insert_user():
    if request.method == 'POST':
        user_email = request.form.get('email')
        user_password = request.form.get('password')
        user_name = request.form.get('name')
        user_last = request.form.get('last')
        user_number = request.form.get('number')

        try:
            supabase.table("user_profiles").insert({
                "email_id": user_email,
                "password": user_password,
                "name": user_name,
                "last": user_last,
                "number": user_number
            }).execute()

            flash("Insert successful")
            return redirect(url_for("login"))
        except Exception as e:
            print(e)
            return redirect(url_for("signup"))


@app.route("/admin")
def admin():
    item = len(items)
    return render_template("admin.html", products_list = item)


@app.route("/add")
def add():
    item = len(items)+1
    return render_template("add.html", products_list = item)

@app.route("/add_products", methods=['POST'])
def add_products():
    if request.method == 'POST':
        new_id = len(items) + 1
        new_category = request.form.get('category')
        new_name = request.form.get('name')
        new_price = request.form.get('price')
        new_rating = request.form.get('rating')
        new_description = request.form.get('description')

        new_product = {
            "id": new_id,
            "name": new_name,
            "price": new_price,
            "rating": new_rating,
            "description": new_description,
            "category": new_category
        }
        food_list.append(new_product)

        with open('static.py', 'w') as file:
            file.write(f'food_list = {food_list}')

        return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(debug=True, port=1100)
