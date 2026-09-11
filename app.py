from flask import Flask, render_template, session, redirect, url_for, flash
from config import Config
from models.models import db
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.suppliers import suppliers_bp
from routes.supplies import supplies_bp
from routes.inventory import inventory_bp
from routes.purchases import purchases_bp
from routes.requests import requests_bp
from routes.departments import departments_bp
from routes.analytics import analytics_bp
from routes.reports import reports_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(supplies_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(purchases_bp)
    app.register_blueprint(requests_bp)
    app.register_blueprint(departments_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(reports_bp)

    @app.context_processor
    def inject_user():
        return {'current_user': session.get('user')}

    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html', code=404, message='Page not found.'), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template('error.html', code=500, message='Something went wrong.'), 500

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
