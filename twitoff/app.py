from flask import Flask, render_template, request
from .models import DB, User, Tweet
from .twitter2 import add_or_update_user
from .predict_2 import predict_user

def create_app():
    app = Flask(__name__)
   

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize SQLAlchemy with the app
    DB.init_app(app)

    @app.route('/')
    def root():
        users = User.query.all()
        return render_template('base.html', title='Home', users=users)
 

    @app.route('/update')
    def update():
        users = User.query.all()      
        for username in [user.username for user in users]:
            add_or_update_user(username)     
        return render_template('base.html', title='Users Updated')    
    
    @app.route('/reset')
    def reset():
        try:
            DB.drop_all() 
            DB.create_all()
            return render_template('base.html', title='Reset Database')
        except Exception as e:
            return f"An error occurred: {e}", 500
        return 'ok'
    
    
    @app.route('/user', methods=['POST'])
    @app.route('/user/<username>', methods=['GET'])
    def user(username=None, message= ''):

        username = username or request.values['user_name']  

        try:
            if request.method == 'POST':
                add_or_update_user(username)
                message = f'User "{username}" has been successfully added!'

            tweets = User.query.filter(User.username==username).one().tweets
        except Exception as e:
            message= f'Error adding {username}: {e}'
            tweets = []
        return render_template('user.html', title=username, tweets=tweets, message=message)

    @app.route('/compare', methods=['POST'])
    def compare():
        user0, user1 = sorted(
            [request.values['user0'], request.values["user1"]])

        if user0 == user1:
            message = "Cannot compare users to themselves!"

        else:
            # prediction returns a 0 or 1
            prediction = predict_user(
                user0, user1, request.values["tweet_text"])
            message = "'{}' is more likely to be said by {} than {}!".format(
                request.values["tweet_text"],
                user1 if prediction else user0,
                user0 if prediction else user1
            )

        return render_template('prediction.html', title="Prediction", message=message)

    return app