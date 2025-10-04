# Smart Expense Management System

A comprehensive web-based expense tracking system built with Flask, featuring role-based access control, interactive charts, and modern UI with dark/light mode support.

## Features

### 🔐 Authentication System
- User registration and login
- Pre-configured admin account (admin/admin123)
- Role-based access control (Admin/User)

### 👤 User Dashboard
- Add, edit, and delete expenses
- Categorize expenses (Food, Transport, Entertainment, Shopping, Health, Other)
- View weekly and monthly spending totals
- Interactive charts with Chart.js
- Dark/Light mode toggle
- Responsive design

### 👑 Admin Dashboard
- View all users and their activity
- Track user spending patterns
- Compare users with interactive charts
- Filter expenses by date and category
- Export reports in CSV and PDF formats
- Comprehensive analytics

### 🎨 Modern UI/UX
- Bootstrap 5 responsive design
- Dark/Light mode with smooth transitions
- Interactive charts and visualizations
- Mobile-friendly interface
- Modern card-based layout

## Tech Stack

- **Backend**: Python Flask
- **Database**: MySQL
- **Frontend**: HTML5, CSS3, Bootstrap 5, Chart.js
- **Icons**: Font Awesome
- **Reports**: ReportLab (PDF), CSV export

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd prohack
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up MySQL database**
   - Install MySQL server
   - Create a database named `expense_management`
   - Update database credentials in `app.py` if needed:
     ```python
     DB_CONFIG = {
         'host': 'localhost',
         'user': 'root',
         'password': 'your_password',  # Update this
         'database': 'expense_management'
     }
     ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - Use admin credentials: `admin` / `admin123`
   - Or create a new user account

## Usage

### For Users
1. Register a new account or login
2. Add expenses with categories, amounts, and descriptions
3. View your spending patterns with interactive charts
4. Track weekly and monthly totals
5. Toggle between dark and light modes

### For Admins
1. Login with admin credentials
2. View all users and their spending data
3. Analyze spending patterns across users
4. Export reports in CSV or PDF format
5. Filter and compare user expenses

## Database Schema

The application automatically creates the following tables:

- **users**: User accounts with role-based access
- **expenses**: Expense records linked to users

## Features

- ✅ Single Flask application file
- ✅ MySQL database integration
- ✅ Role-based authentication
- ✅ User expense management (CRUD)
- ✅ Admin dashboard with analytics
- ✅ Interactive charts with Chart.js
- ✅ Dark/Light mode toggle
- ✅ Responsive design
- ✅ CSV/PDF export functionality
- ✅ Modern UI with Bootstrap 5

## Default Admin Account

- **Username**: admin
- **Password**: admin123

## Screenshots

The application features a modern, responsive interface with:
- Clean login/registration pages
- Interactive dashboards with charts
- Dark/light mode support
- Mobile-friendly design
- Comprehensive admin analytics

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.
