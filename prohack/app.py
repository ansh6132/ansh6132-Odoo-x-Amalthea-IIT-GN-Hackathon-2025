from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# --- Database Configuration ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Add your MySQL password here if you have one
    'database': 'expense_management'
}

def get_db_connection():
    """Create and return a database connection."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# --- Routes ---

@app.route('/')
def index():
    """Redirect to login page or dashboard if already logged in."""
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('user_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        connection = get_db_connection()
        if not connection:
            flash('Database connection error', 'error')
            return render_template('login.html')
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT id, username, password_hash, role FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                
                if user['role'] == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('user_dashboard'))
            else:
                flash('Invalid username or password', 'error')
        except Error as e:
            flash(f'Login error: {e}', 'error')
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        connection = get_db_connection()
        if not connection:
            flash('Database connection error', 'error')
            return render_template('register.html')

        try:
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
            if cursor.fetchone():
                flash('Username or email already exists.', 'error')
                return render_template('register.html')

            password_hash = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, password_hash)
            )
            connection.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Error as e:
            flash(f'Registration error: {e}', 'error')
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                
    return render_template('register.html')


@app.route('/logout')
def logout():
    """Handle user logout."""
    session.clear()
    return redirect(url_for('login'))

@app.route('/user_dashboard')
def user_dashboard():
    """User dashboard with expense management."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'error')
        return redirect(url_for('login'))

    expenses_this_month = []
    weekly_total = 0.0
    monthly_total = 0.0
    category_labels = []
    category_values = []
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, category, amount, description, expense_date
            FROM expenses
            WHERE user_id = %s AND MONTH(expense_date) = MONTH(CURDATE())
            AND YEAR(expense_date) = YEAR(CURDATE())
            ORDER BY expense_date DESC
        """, (session['user_id'],))
        expenses_this_month = cursor.fetchall()
        
        category_summary = {}
        today = datetime.now().date()
        seven_days_ago = today - timedelta(days=7)

        for expense in expenses_this_month:
            amount = float(expense['amount'])
            monthly_total += amount
            if expense['expense_date'] >= seven_days_ago:
                weekly_total += amount
            category = expense['category']
            category_summary[category] = category_summary.get(category, 0) + amount

        if category_summary:
            category_labels = list(category_summary.keys())
            category_values = list(category_summary.values())

    except Error as e:
        print(f"Database error: {e}")
        flash('Error loading dashboard', 'error')
    
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            
    return render_template(
        'user_dashboard.html',
        expenses=expenses_this_month,
        weekly_total=weekly_total,
        monthly_total=monthly_total,
        category_labels=category_labels,
        category_values=category_values,
        username=session.get("username", "User")
    )


@app.route('/add_expense', methods=['POST'])
def add_expense():
    """Add new expense."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        category = request.form['category']
        amount = float(request.form['amount'])
        description = request.form.get('description', '')
        expense_date = request.form['expense_date']
    except (ValueError, KeyError):
        flash('Invalid form data submitted.', 'error')
        return redirect(url_for('user_dashboard'))

    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'error')
        return redirect(url_for('user_dashboard'))

    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO expenses (user_id, category, amount, description, expense_date) VALUES (%s, %s, %s, %s, %s)",
            (session['user_id'], category, amount, description, expense_date)
        )
        connection.commit()
        flash('Expense added successfully!', 'success')
    except Error as e:
        flash(f'Error adding expense: {e}', 'error')
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return redirect(url_for('user_dashboard'))


@app.route('/edit_expense/<int:expense_id>', methods=['POST'])
def edit_expense(expense_id):
    """Edit existing expense."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        category = request.form['category']
        amount = float(request.form['amount'])
        description = request.form.get('description', '')
        expense_date = request.form['expense_date']
    except (ValueError, KeyError):
        flash('Invalid form data submitted.', 'error')
        return redirect(url_for('user_dashboard'))
    
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'error')
        return redirect(url_for('user_dashboard'))

    try:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE expenses SET category=%s, amount=%s, description=%s, expense_date=%s WHERE id=%s AND user_id=%s",
            (category, amount, description, expense_date, expense_id, session['user_id'])
        )
        connection.commit()
        flash('Expense updated successfully!', 'success')
    except Error as e:
        flash(f'Error updating expense: {e}', 'error')
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return redirect(url_for('user_dashboard'))

@app.route('/delete_expense/<int:expense_id>')
def delete_expense(expense_id):
    """Delete an expense."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'error')
        return redirect(url_for('user_dashboard'))

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM expenses WHERE id = %s AND user_id = %s", (expense_id, session['user_id']))
        connection.commit()
        flash('Expense deleted successfully!', 'success')
    except Error as e:
        flash(f'Error deleting expense: {e}', 'error')
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return redirect(url_for('user_dashboard'))


# --- Admin Routes ---
@app.route('/admin_dashboard')
def admin_dashboard():
    """Admin dashboard with user management and analytics."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    if not connection:
        flash('Database connection error', 'error')
        return redirect(url_for('login'))

    # Initialize variables
    users_analytics = []
    all_expenses = []
    category_breakdown = []
    total_spent = 0

    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get user analytics (one efficient query)
        cursor.execute("""
            SELECT 
                u.id, u.username, u.email, u.created_at,
                COALESCE(SUM(e.amount), 0) as total_amount,
                COALESCE(SUM(CASE WHEN e.expense_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) THEN e.amount ELSE 0 END), 0) as weekly_total,
                COALESCE(SUM(CASE WHEN MONTH(e.expense_date) = MONTH(CURDATE()) AND YEAR(e.expense_date) = YEAR(CURDATE()) THEN e.amount ELSE 0 END), 0) as monthly_total
            FROM users u
            LEFT JOIN expenses e ON u.id = e.user_id
            WHERE u.role = 'user'
            GROUP BY u.id, u.username, u.email, u.created_at
            ORDER BY u.created_at DESC
        """)
        users_analytics = cursor.fetchall()
        
        # Get all expenses with user info
        cursor.execute("""
            SELECT e.id, u.username, e.category, e.amount, e.description, e.expense_date 
            FROM expenses e 
            JOIN users u ON e.user_id = u.id 
            ORDER BY e.expense_date DESC
        """)
        all_expenses = cursor.fetchall()

        # Get category breakdown for all users
        cursor.execute("""
            SELECT category, SUM(amount) as total
            FROM expenses
            GROUP BY category
            ORDER BY total DESC
        """)
        category_breakdown = cursor.fetchall()
        
        # Calculate total spent from user analytics
        total_spent = sum(user['total_amount'] for user in users_analytics)

    except Error as e:
        flash(f'Error loading admin dashboard: {e}', 'error')
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
    return render_template('admin_dashboard.html', 
                           users_analytics=users_analytics,
                           all_expenses=all_expenses,
                           category_breakdown=category_breakdown,
                           total_spent=total_spent)

# Add export routes if needed (e.g., /export_csv, /export_pdf)
# These would need their own logic similar to the admin_dashboard queries.

if __name__ == '__main__':
    app.run(debug=True)