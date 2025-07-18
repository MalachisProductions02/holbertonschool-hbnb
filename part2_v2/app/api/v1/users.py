from flask_restx import Namespace, Resource, fields
from app.services.facade import hbnb_facade
from app.models.user import User

api = Namespace('Users', description='User operations', path='/users')

# Modelo para documentación Swagger
user_model = api.model('User', {
    'id': fields.String(readonly=True, description='User ID'),
    'first_name': fields.String(required=True, description='First name', max_length=50),
    'last_name': fields.String(required=True, description='Last name', max_length=50),
    'email': fields.String(required=True, description='Email address'),
    'is_admin': fields.Boolean(default=False, description='Admin status')
})

user_update_model = api.model('UserUpdate', {
    'first_name': fields.String(description='First name', max_length=50),
    'last_name': fields.String(description='Last name', max_length=50),
    'email': fields.String(description='Email address'),
    'is_admin': fields.Boolean(description='Admin status')
})

@api.route('/')
class UserList(Resource):
    @api.marshal_list_with(user_model)
    def get(self):
        """List all users"""
        users = hbnb_facade.list_users()
        return [{
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'is_admin': user.is_admin
        } for user in users]

    @api.expect(user_model, validate=True)
    @api.marshal_with(user_model, code=201)
    @api.response(400, 'Invalid input or email exists')
    def post(self):
        """Create a new user"""
        data = api.payload
        
        # Validación de email único
        if hbnb_facade.get_user_by_email(data['email']):
            api.abort(400, 'Email already registered')
            
        try:
            user = hbnb_facade.create_user(
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                password=data.get('password', ''),
                is_admin=data.get('is_admin', False)
            )
            return user, 201
        except ValueError as e:
            api.abort(400, str(e))

@api.route('/<string:user_id>')
class UserResource(Resource):
    @api.marshal_with(user_model)
    @api.response(404, 'User not found')
    def get(self, user_id):
        """Get user by ID"""
        user = hbnb_facade.get_user(user_id)
        if not user:
            api.abort(404, 'User not found')
        return user

    @api.expect(user_update_model)
    @api.marshal_with(user_model)
    @api.response(400, 'Invalid input')
    @api.response(404, 'User not found')
    def put(self, user_id):
        """Update user information"""
        data = api.payload
        
        # Email validation if its updated
        if 'email' in data and hbnb_facade.get_user_by_email(data['email']):
            existing = hbnb_facade.get_user_by_email(data['email'])
            if existing.id != user_id:
                api.abort(400, 'Email already registered')
                
        try:
            hbnb_facade.update_user(
                user_id=user_id,
                **data
            )
            return hbnb_facade.get_user(user_id)
        except ValueError as e:
            api.abort(400, str(e))

    @api.route('/users/<user_id>')
    class AdminUserModify(Resource):
        @jwt_required()
        def put(self, user_id):
            current_user = get_jwt_identity()

            # If 'is_admin' if part of the identity payload
            if not current_user.get('is_admin'):
                return {'error': 'Admin privileges required'}, 403
            
            data = request.json
            email = data.get('email')

            if email:
                # Check if the email is already in use
                existing_user = facade.get_user_by_email(email)
                if existing_user and existing_user.id != user_id:
                    return {'error', 'Email is already in use'}, 400
                
            # Logic to update user details, including email and password
            pass


    @api.route('/users/')
    class AdminUserCreate(Resource):
        @jwt_required()
        def post(self):
            current_user = get_jwt_indentity()
            if not current_user.get('is_admin'):
                return {'error', 'Email already registered'}, 400
            
            # logic to create a new user
            pass
