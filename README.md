PROJECT TITLE:
Sales Management System with Future Sales Prediction and Waste Management Features using Machine Learning for the EDEN DINE Restaurant

DESCRIPTION:
This web-based system was developed as a final-year undergraduate research project to enhance restaurant operations at EDEN DINE Restaurant. The system enables efficient sales management, real-time inventory tracking, predictive analytics using machine learning, and waste management functionalities. Its goal is to help restaurant staff optimize stock usage, reduce food waste, and improve decision-making through data-driven insights.

Unlike traditional restaurant management software, this system integrates sales and inventory forecasting models to proactively suggest stock replenishments and predict demand patterns. It supports role-based access and provides dashboards for various staff members, including administrators, managers, cashiers, waiters, and chefs.

TECHNOLOGIES USED:
- **Frontend**: React.js
- **Backend**: Python (Flask)
- **Database**: PostgreSQL
- **Authentication**: JSON Web Tokens (JWT)
- **Machine Learning Libraries**: Scikit-learn, LightGBM, TensorFlow
- **Deployment**: Localhost (development), compatible with cloud deployment

CORE FEATURES:
- Role-based authentication and access control
- Sales and order management module
- Inventory tracking and restocking alerts
- Sales prediction using historical transaction data
- Inventory forecasting to minimize waste
- Inventory and sales reports with date-range filters
- Admin dashboard for registering new users and managing roles
- User profile management and password update

SYSTEM REQUIREMENTS:
- Python 3.8 or above
- Node.js 16.x or above
- PostgreSQL 12 or above
- pip (Python package installer)
- npm (Node package manager)

SETUP INSTRUCTIONS:

1.  Repository: (https://github.com/HasinduN/FYP/)

2. **Backend Setup (Flask API):**
- Create and activate a virtual environment:
  ```
  python -m venv venv
  source venv/bin/activate    # Linux/macOS
  venv\Scripts\activate       # Windows
  ```
- Install backend dependencies:
  ```
  pip install -r requirements.txt
  ```
- Set up PostgreSQL:
  - Create a database
  - Update connection settings in the backend configuration file
- Run the backend server:
  ```
  python app.py
  ```

3. **Frontend Setup (React.js):**
- Navigate to the frontend folder:
  ```
  cd frontend
  ```
- Install frontend dependencies:
  ```
  npm install
  ```
- Start the frontend development server:
  ```
  npm start
  ```
- Access the application at: `http://localhost:3000`

4. **Database Configuration:**
- Ensure PostgreSQL is installed and running.
- Update your `.env` or config files with the correct DB URI:
  ```
  postgresql://postgres:hasindu123@localhost/pos_system
  ```

5. **Machine Learning Model Training:**
- Training scripts are located in the `/ml_models` directory.
- Scripts include training for:
  - Sales Prediction (`train_sales_model.py`)
  - Monthly Inventory Prediction (`train_monthly_inventory_model.py`)
  - Weekly Inventory Prediction (`train_weekly_inventory_model.py`)
  - Frequent Restock Prediction (`train_roti_inventory_model.py`)
- Models are saved as `.pkl` files and loaded dynamically during prediction.

NOTES:
- Make sure to update JWT secret keys and production settings before deployment.
- All models are trained using historical sales and inventory data from EDEN DINE Restaurant.

AUTHOR:
- Hasindu Nanayakkara
- Final Year Research Project, University of Bedfordshire
- Supervisor: Ms. Nideshika Ellepola
