from flask import Flask
from flask_cors import CORS
from routes.menu import menu_bp
from routes.inventory import inventory_bp
from routes.sales import sales_bp
from routes.recipes import recipes_bp
from routes.orders import orders_bp
from routes.inventoryManagement import inventorymanagement_bp

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = "ed"

app.register_blueprint(menu_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(recipes_bp)
app.register_blueprint(orders_bp)
app.register_blueprint(inventorymanagement_bp)

if __name__ == '__main__':
    app.run(debug=True)