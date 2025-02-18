from flask import Flask, request, jsonify, redirect, url_for, session, render_template_string

app = Flask(__name__)  # Correct the app initialization
app.secret_key = 'your_secret_key_here'  # This is needed to use Flask sessions

# Simulating a database with users
users = {
    'admin': {'password': 'adminpass', 'role': 'admin'},
    'user': {'password': 'userpass', 'role': 'user'}
}

# Simulated product inventory
products = {
    'cheap_item': {'name': 'Cheap Item', 'price': 10},
    'leather_jacket': {'name': 'Leather Jacket', 'price': 100}
}

# Store credit balance for users
store_credit = {
    'user': 50  # Assume the user has $50 store credit
}

# Simulating the shopping cart for each user
carts = {
    'user': {'cheap_item': 0, 'leather_jacket': 0}
}

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('account'))
    return redirect(url_for('login'))  # Redirect to login if not authenticated

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and users[username]['password'] == password:
            session['username'] = username  # Store username in session
            session['role'] = users[username]['role']  # Store role in session
            return redirect(url_for('account'))  # Redirect to account page after successful login
        return jsonify({"message": "Invalid credentials"}), 401
    
    return render_template_string('''
        <h2>Login</h2>
        <form method="post">
            Username: <input type="text" name="username" required><br><br>
            Password: <input type="password" name="password" required><br><br>
            <input type="submit" value="Login">
        </form>
    ''')

# Account page (view and manage cart)
@app.route('/account', methods=['GET'])
def account():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not authenticated
    
    username = session['username']
    return redirect(url_for('cart'))  # Redirect to cart page

# Shopping cart page
@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not authenticated
    
    username = session['username']
    
    # Process cart manipulation (add or remove items)
    if request.method == 'POST':
        product_id = request.form['product_id']
        quantity = int(request.form['quantity'])
        
        # Modify the cart
        if product_id in products:
            carts[username][product_id] += quantity
        
            # Deduct store credit if necessary
            total_price = sum(carts[username][item] * products[item]['price'] for item in carts[username])
            remaining_credit = store_credit.get(username, 0) - total_price

            # Ensure cart total doesn't exceed the available store credit
            if remaining_credit < 0:
                carts[username] = {'cheap_item': 0, 'leather_jacket': 0}  # Reset cart if credit is overdrawn
                return jsonify({"message": "Insufficient store credit, cart reset."}), 403

            store_credit[username] = remaining_credit
        
        return redirect(url_for('cart'))  # Redirect to view updated cart

    # Display the current cart status
    total_price = sum(carts[username][item] * products[item]['price'] for item in carts[username])
    return render_template_string('''
        <h2>Shopping Cart</h2>
        <ul>
            {% for product_id, quantity in carts[username].items() %}
                <li>{{ products[product_id]['name'] }}: {{ quantity }} @ ${{ products[product_id]['price'] }} each</li>
            {% endfor %}
        </ul>
        <h3>Total Price: ${{ total_price }}</h3>
        
        <form method="post">
            <label for="product_id">Product ID:</label>
            <select name="product_id">
                <option value="cheap_item">Cheap Item</option>
                <option value="leather_jacket">Leather Jacket</option>
            </select><br><br>
            <label for="quantity">Quantity:</label>
            <input type="number" name="quantity" required><br><br>
            <input type="submit" value="Update Cart">
        </form>
    ''', username=username, products=products, carts=carts, total_price=total_price)

# Admin page (restricted to users with the admin role)
@app.route('/admin', methods=['GET'])
def admin():
    if 'username' not in session or users[session['username']]['role'] != 'admin':
        return jsonify({"message": "Unauthorized access, admin role required!"}), 403  # Admin role is required
    
    return jsonify({"message": "Welcome Admin!"})

if __name__ == '__main__':  # Correct the if condition for app.run
    app.run(debug=True)
