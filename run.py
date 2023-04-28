from app import app
import views
from app import db,db_name
from os import path
from app import login_manager

from main_api import UserApi,PostApi






app.app_context().push()

if __name__ == "__main__":
    #if db not present
    if not path.exists('/'+db_name):
        db.create_all()


    app.run(debug=False,port=8000)




    
    


