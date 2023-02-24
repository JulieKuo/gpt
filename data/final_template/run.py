from flask_restful import Api
from app import server
from resources import *
import warnings

warnings.filterwarnings('ignore')

api = Api(server)






if __name__ == '__main__':
    server.run(host = '0.0.0.0', debug=True)