from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
from config import DevConfig
from models import User, Ticket
from exts import db
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required

app = Flask(__name__)
app.config.from_object(DevConfig)

db.init_app(app)

migrate = Migrate(app, db)
JWTManager(app)

api = Api(app, doc='/docs')

# Model Serializer
user_model = api.model(
    "User",
    {
        "id": fields.Integer(),
        "username": fields.String(),
        "password": fields.String()
    }
)

login_model = api.model(
    "Login",
    {
        "username": fields.String(),
        "password": fields.String()
    }
)

ticket_model = api.model(
    "Ticket",
    {
        "id": fields.Integer(),
        "title": fields.String(),
        "content": fields.String()
    }
)

@api.route('/hello')
class HelloResource(Resource):
    def get(self):
        """ Hello World Test Endpoint """
        return {"message": "Hello World"}

@api.route('/signup')
class Signup(Resource):
    @api.expect(user_model)
    def post(self):
        """ SignUp a new user """
        data = request.get_json()

        username = data.get('username')
        db_user = User.query.filter_by(username=username).first()

        if db_user is not None:
            return jsonify({"message": f"Username {username} already exists"})
        new_user = User(
            username = data.get('username'),
            password = generate_password_hash(data.get('password')),
        )

        new_user.save()

        return jsonify({"message": "User has been sucessfully created!"})

@api.route('/login')
class Login(Resource):
    @api.expect(user_model)
    def post(self):
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        db_user = User.query.filter_by(username=username).first()

        if db_user and check_password_hash(db_user.password, password):
            access_token = create_access_token(identity=db_user.username)
            refresh_token = create_refresh_token(identity=db_user.username)

            return jsonify({"access_token": access_token, "refresh_token": refresh_token})

        return jsonify({
            "message": "User does not exist"
        })



@api.route('/users')
class UsersResource(Resource):
    @api.marshal_list_with(user_model)
    def get(self):
        """Get all users"""
        users = User.query.all()
        return users


@api.route('/user/<int:id>')
class UserResource(Resource):

    @api.marshal_with(user_model)
    def get(self, id):
        """Get a user by id"""
        user = User.query.get_or_404(id)
        return user

    @api.marshal_with(user_model)
    def put(self, id):
        """Update a user by id"""
        user_to_update = User.query.get_or_404(id)
        data = request.get_json()
        user_to_update.update(username=data.get('username'), password=data.get('password'))

        return user_to_update

    @api.marshal_with(user_model)
    def delete(self, id):
        """Delete a user by id"""
        user_to_delete = User.query.get_or_404(id)
        user_to_delete.delete()

        return user_to_delete

""" Tickets API Endpoints """
@api.route('/tickets')
class TicketsResource(Resource):

    @api.marshal_list_with(ticket_model)
    @jwt_required()
    def get(self):
        """Get Tickets"""
        tickets = Ticket.query.all()
        return tickets

    @api.marshal_with(ticket_model)
    @api.expect(ticket_model)
    @jwt_required()
    def post(self):
        """Create new Ticket"""
        data = request.get_json()
        new_ticket = Ticket(
            title = data.get('title'),
            content = data.get('content')
        )
        new_ticket.save()
        
        return new_ticket, 201

@api.route('/ticket/<int:id>')
class TicketResource(Resource):
    @api.marshal_with(ticket_model)
    @jwt_required()
    def get(self, id):
        """Get Ticket by id"""
        ticket = Ticket.query.get_or_404(id)
        return ticket

    @api.marshal_with(ticket_model)
    @jwt_required()
    def put(self, id):
        """Update a Ticket by id"""
        ticket_to_update = Ticket.query.get_or_404(id)
        data = request.get_json()
        ticket_to_update.update(title=data.get('title'), content=data.get('content'))

        return ticket_to_update

    @api.marshal_with(ticket_model)
    @jwt_required()
    def delete(self, id):
        """Delete a Ticket by id"""
        ticket_to_delete = Ticket.query.get_or_404(id)
        ticket_to_delete.delete()

        return ticket_to_delete

@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": User
    }

if __name__ == "__main__":
    app.run()