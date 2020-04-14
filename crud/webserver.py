#!/usr/bin/env python3
#

from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi

#DB Setup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

#Create Session and connect to DB
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

class WebServerHandler(BaseHTTPRequestHandler):

    my_form = \
        '''
        <form method='POST' enctype='multipart/form-data' action='/hello'>
        <h2>What would you like me to say?</h2>
        <input name="message" type="text"><input type="submit" value="Submit">
        </form>
         '''

    add_restaurant_form = \
        '''
        <form method='POST' enctype='multipart/form-data' action='/restaurants/new'>
        <h2>Add Restaurant</h2>
        <input name="new_restaurant" type="text">
        <input type="submit" value="Add">
        </form>
         '''

    def do_GET(self):
        try:

            #hello
            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body><br>"
                output += "<h1>Hello!</h1>"
                output += self.my_form
                output += "</body></html>"

                self.wfile.write(output.encode())
                print("Hello: {}\n".format(output))
                return

            #hola
            if self.path.endswith("/hola"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>&#161;Hola!"
                output += self.my_form
                output += "</body></html>"

                self.wfile.write(output.encode())
                print("Hola: {}\n".format(output))
                return

            #list Restaurants
            if self.path.endswith("/restaurants"):

                #Query restaurants
                restaurants = session.query(Restaurant).all()

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body></br>"
                output += "<h1>Restaurants</h1>"

                for restaurant in restaurants:
                    output += "{}".format(restaurant.name) + "</br>"
                    output += "</br>"
                    output += "<a href =" + "\'/restaurants/{}/edit\'".format(restaurant.id) + " >Edit </a></br> "
                    output += "<a href =" + "\'/restaurants/{}/delete\'".format(restaurant.id) + " >Delete </a></br></br> "
                    #output += '<a href="#"> Delete </a><br></br>'

                output += "</body></html>"

                self.wfile.write(output.encode())
                print("Restaurants: {}\n".format(output))
                return

            #add Restaurant
            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body></br>"
                output += self.add_restaurant_form
                output += "</body></html>"

                self.wfile.write(output.encode())
                print("Restaurant new: {}\n".format(output))
                return

            #edit Restaurant name
            if self.path.endswith("/edit"):
                restaurantIDPath = self.path.split("/")[2]
                restaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
                print("Editing RestaurantIDPath: {}".format(restaurantIDPath))
                if restaurantQuery:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body></br>"
                    output += "<h1>"
                    output += "{}".format(restaurantQuery.name)
                    output += "</h1>"
                    output += "<form method='POST' enctype='multipart/form-data'"
                    output += " action= " + "\'/restaurants/{}/edit\'".format(restaurantIDPath) + " >"
                    output += " <input name= 'edit_restaurant' type='text' placeholder="
                    output += " \'{}\'".format(restaurantQuery.name) + " >"
                    output += "<input type = 'submit' value = 'Rename'></form>"
                    output += "</body></html>"

                self.wfile.write(output.encode())
                print("Edit: {}\n".format(output))
                return

            #delete Restaurant name
            if self.path.endswith("/delete"):
                restaurantIDPath = self.path.split("/")[2]
                restaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
                print("Deleting RestaurantIDPath: {}".format(restaurantIDPath))
                if restaurantQuery:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body></br>"
                    output += "<h1> Are you sure you want to delete "
                    output += "{}".format(restaurantQuery.name)
                    output += " ?</h1>"
                    output += "<form method='POST' enctype='multipart/form-data'"
                    output += " action= " + "\'/restaurants/{}/delete\'".format(restaurantIDPath) + " >"
                    output += " <input type = 'submit' value = 'Delete'></form>"
                    output += "</body></html>"

                self.wfile.write(output.encode())
                print("Edit: {}\n".format(output))
                return

        except IOError:
            self.send_error(404, "File not Found: {}".format(self.path))

    def do_POST(self):
        try:
            #hello
            if self.path.endswith("/hello"):
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                ctype, pdict = cgi.parse_header(self.headers['content-type'])

                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")

                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messageContent = fields.get('message')
                    print("Message Content: {}\n".format(messageContent))

                output = ""
                output += "<html><body>"
                output += " <h2> Okay, how about this: </h2>"
                output += "<h1> {} </h1>".format(messageContent[0].decode())
                output += self.my_form
                output += "</body></html>"

                self.wfile.write(output.encode())
                print("Post: {}\n".format(output))

            #add Restaurant
            if self.path.endswith("/restaurants/new"):
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                ctype, pdict = cgi.parse_header(self.headers['content-type'])

                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")

                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messageContent = fields.get('new_restaurant')
                    session.add(Restaurant(name=messageContent[0].decode()))
                    session.commit()
                    print("added new restaurant!")

                self.send_header('Location', '/restaurants')
                self.end_headers()

            #edit Restaurant
            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers['content-type'])

                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")

                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messageContent = fields.get('edit_restaurant')

                    restaurantIDPath = self.path.split("/")[2]
                    restaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()

                    if restaurantQuery != []:
                        restaurantQuery.name = messageContent[0].decode()
                        session.add(restaurantQuery)
                        session.commit()
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()
                        print("restaurant edited!")

            #delete Restaurant
            if self.path.endswith("/delete"):
                ctype, pdict = cgi.parse_header(self.headers['content-type'])

                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")

                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messageContent = fields.get('edit_restaurant')

                    restaurantIDPath = self.path.split("/")[2]
                    restaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()

                    if restaurantQuery != []:
                        session.delete(restaurantQuery)
                        session.commit()
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()
                        print("restaurant deleted!")
        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('',port), WebServerHandler)
        print("Web server running on port: {}".format(port))
        server.serve_forever()

    except KeyboardInterrupt:
        print("^C entered, stopping web server...")
        server.socket.close()


if __name__ == '__main__':
    main()
