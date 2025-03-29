from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import session, TokenBlockList
from routes.auth import auth_bp  # Ensure correct import
from routes.menu import menu_bp
from routes.inventory import inventory_bp
from routes.recipes import recipes_bp
from routes.orders import orders_bp
from routes.sales import sales_bp
from routes.inventoryManagement import inventorymanagement_bp
from routes.sales_prediction import sales_prediction_bp
from routes.inventory_prediction import inventory_prediction_bp

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "edine"
jwt = JWTManager(app)
CORS(app, supports_credentials=True)

#Register the auth blueprint with "/auth" prefix
app.register_blueprint(auth_bp, url_prefix="/auth")

app.register_blueprint(menu_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(orders_bp)
app.register_blueprint(recipes_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(inventorymanagement_bp)
app.register_blueprint(sales_prediction_bp)
app.register_blueprint(inventory_prediction_bp)

#Ensure token blocklist is checked for revoked tokens
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    """Block blacklisted JWT tokens"""
    jti = jwt_payload["jti"]  # Extract token ID
    token = session.query(TokenBlockList).filter_by(jti=jti).first()
    return token is not None  # Return True if the token is blacklisted

@app.teardown_appcontext
def shutdown_session(exception=None):
    """Remove scoped session when app shuts down"""
    session.remove()

if __name__ == "__main__":
    app.run(debug=True)  #Restart the app to apply changes
