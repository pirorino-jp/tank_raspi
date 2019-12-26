import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket

class MyHandler(tornado.websocket.WebSocketHandler):
        def check_origin(self, origin):
            return True

        def open(self):
                print("connection opened")
                self.write_message("connection opened")

        def on_close(self):
                print("connection closed")

        def on_message(self,message):
                print("Message received: {}".format(message))
                self.write_message("message received")

if __name__ == "__main__":
        tornado.options.parse_command_line()
        app = tornado.web.Application(handlers=[(r"/",MyHandler)])
        server = tornado.httpserver.HTTPServer(app)
        server.listen(10000)
        tornado.ioloop.IOLoop.instance().start()
