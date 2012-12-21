import constants
from rayage.database.User import User
from CASVerifiedRequestHandler import CASVerifiedRequestHandler

class PageRequestHandler(CASVerifiedRequestHandler):
    def get(self, action):
        if action == "logout":
            self.logout_user()
        else:
            username = self.get_current_user()
            
            if username is None:
                self.validate_user()
                return
                
            user = User.get_user(username)
                
            if action == "admin" and user.permission_level >= constants.PERMISSION_LEVEL_TA:
                self.render("admin.html", debug=constants.DEBUG, user=user, constants=constants)
            elif user.permission_level >= constants.PERMISSION_LEVEL_USER:
                self.render("index.html", debug=constants.DEBUG, user=user, constants=constants)
            else:
                self.render("denied.html", debug=constants.DEBUG, user=user, constants=constants)
