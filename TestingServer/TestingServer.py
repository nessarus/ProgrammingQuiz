#CITS3002 Final Project - Python Testing Server
#Jesse Wyatt (20756971)
#Joshua Ng (20163079)
#Hoang Tuan Anh (21749914)

import ssl
import socket
import http.server
import http.cookies
import socketserver
import cgi
import datetime
import uuid
import binascii
import hashlib

HOSTNAME = "QuestionServer.CITS3002"
QHOST = input("Enter QuestionServer IPv4 address: ") 
QPORT = int(input("Enter QuestionServer port: "))
HTTPPORT = 8080
REQUESTSIZE = 10
HTMLHEAD = """<!DOCTYPE html>
<html>
<head>
<meta charset=\"UTF-8\">
</head>
<body>"""
HTMLFORM = """<form method=\"POST\">"""
HTMLQUEST = """<input type=\"submit\" name=\"submit\" value=\"Previous\"><br>
<input type=\"submit\" name=\"submit\" value=\"Next\"><br>"""
HTMLFOOT = """<input type=\"submit\" name=\"submit\" value=\"Log Out\"><br>
</form>
</body>
</html>"""
BADWORDS = ["import", "open(", "classmethod(", "eval(", "exec(", "globals(", "memoryview(", "__import__("]


def parseQuestions(session, quests):

    questionStrings = quests.split("---")
    sessionQuestions = []

    for qString in questionStrings[:-1]:
        qData = qString.strip().split('\n')
        ID = int(qData[1])
        TYPE = int(qData[3])

        if TYPE == 0: #multiple choice question
            sessionQuestions.append(MultiQuestion(ID, TYPE, qData))
        else: #programming question
            sessionQuestions.append(ProgQuestion(ID, TYPE, qData))

    currentSessions[session]['questions'] = sessionQuestions


class Question:
    def __init__(self, id, type):
        self.id = id
        self.type = type
        self.attempts = 3
        self.solved = False
            
class MultiQuestion(Question):
    def __init__(self, id, type, qData):
        super().__init__(id, type)
        self.qBody = qData[5]
        self.numAnswers = int(qData[7])
        self.answers = []
        for i in range(self.numAnswers):
            self.answers.append(qData[9 + i])

    def toHTML(self, just_failed=False):
        html = HTMLHEAD + HTMLFORM
        html += self.qBody + "<br>"

        for i in range(self.numAnswers):
            html += "<input type=\"radio\" name=\"mc_submission\" value=\""
            html += str(i + 1)
            html += "\"> "
            html += self.answers[i]
            html += "<br>"

        if just_failed:
            html += "<h2>Incorrect Answer!</h2>"
        if not self.solved and self.attempts > 0:
            html += "<input type=\"submit\" name=\"submit\" value=\"Submit\"><br>"
        if self.solved:
            html += "<h2>Correct Answer!</h2>"
        else:
            html += "<p>Attempts Remaining: " + str(self.attempts) + "</p>"
        html += HTMLQUEST + HTMLFOOT
        return html

class ProgQuestion(Question):
    def __init__(self, id, type, qData):
        super().__init__(id, type)
        self.qBody = qData[5]

    def toHTML(self, just_failed=False):
        html = (HTMLHEAD
               + HTMLFORM
               + self.qBody + "<br>"
               + "<textarea name=\"code_submission\" style=\"width: 500px; height: 300px;\" /></textarea><br>")
        if just_failed:
            html += "<h2>Incorrect Answer!</h2>"
        if not self.solved and self.attempts > 0:
            html += "<input type=\"submit\" name=\"submit\" value=\"Submit\"><br>"
        if self.solved:
            html += "<h2>Correct Answer!</h2>"
        else:
            html += "<p>Attempts Remaining: " + str(self.attempts) + "</p>"
        html += HTMLQUEST + HTMLFOOT
        return html

class HTTPHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path =="/favicon.ico":
            return
        else:
            cookie = http.cookies.SimpleCookie(self.headers.get('Cookie'))
            if 'session' in cookie and cookie['session'].value in currentSessions:
                self.serve_greeting(cookie)
                return

            else:
                self.serve_login()
                return

    def do_POST(self):
        cookie = http.cookies.SimpleCookie(self.headers.get('Cookie'))

        form = cgi.FieldStorage(fp=self.rfile,
                                headers=self.headers,
                                environ={'REQUEST_METHOD': 'POST',
                                         'CONTENT_TYPE': self.headers['Content-type']})
        
        if form['submit'].value == 'Log In':
            #log in process
            user = form['username'].value
            pwdhash = hashlib.pbkdf2_hmac('sha256', form['password'].value.encode(), userdata[user]['salt'].encode(), 100000) 
            if user in userdata and binascii.hexlify(pwdhash).decode() == userdata[user]['passhash']:
                #login
                expiration = datetime.datetime.now() + datetime.timedelta(seconds=3600)
                cookie = http.cookies.SimpleCookie()
                sessionID = str(uuid.uuid4())
                cookie['session'] = sessionID
                cookie['session']['expires'] = 3600
                currentSessions[sessionID] = {'user':user}
                self.serve_greeting(cookie)

            else:
                self.serve_login()

        elif not cookie['session'].value in currentSessions:
            return #kick out to login page

        else:
            sessionID = cookie['session'].value
            sess = currentSessions[sessionID]
            #start quiz
            if form['submit'].value == 'Continue Quiz':
                self._set_headers(cookie)
                self.wfile.write(sess['questions'][sess['currentQuestion']].toHTML().encode('UTF-8'))

            elif form['submit'].value == 'Start New Quiz':
                #request questions
                qSock = new_socket()
                qSock.connect((QHOST, QPORT))
                qSock.send('REQUEST-QUEST\n'.encode('UTF-8'))
                qSock.send((str(REQUESTSIZE) + '\n').encode('UTF-8'))
                #parse request

                header = qSock.recv(16)[2:].decode('UTF-8')
                length = int(qSock.recv(6).decode('UTF-8'))

                parseQuestions(cookie['session'].value, qSock.recv(length).decode('UTF-8'))
                qSock.close()
                currentSessions[sessionID]['currentQuestion'] = 0

                #send html
                self._set_headers(cookie)
                self.wfile.write(sess['questions'][sess['currentQuestion']].toHTML().encode('UTF-8'))
                return
            #next
            elif form['submit'].value == 'Next':
                self._set_headers(cookie)
                sess['currentQuestion'] += 1
                sess['currentQuestion'] %= REQUESTSIZE
                self.wfile.write(sess['questions'][sess['currentQuestion']].toHTML().encode('UTF-8'))
                return
            #previous
            elif form['submit'].value == 'Previous':
                self._set_headers(cookie)
                sess['currentQuestion'] -= 1
                sess['currentQuestion'] %= REQUESTSIZE
                self.wfile.write(sess['questions'][sess['currentQuestion']].toHTML().encode('UTF-8'))
                return
            #logout
            elif form['submit'].value == 'Log Out':
                currentSessions.pop(sessionID)
                self.serve_login()
                return
            #submit
            elif form['submit'].value == 'Submit':
                if 'mc_submission' in form:
                    #MCquestion
                    packet = ('REQUEST-VERIF\n2\n'
                              + str(sess['questions'][sess['currentQuestion']].id)
                              + '\n' + form['mc_submission'].value + '\n')

                    qSock = new_socket()
                    qSock.connect((QHOST, QPORT))
                    qSock.send(packet.encode('UTF-8'))
                    reply = qSock.recv().decode('UTF-8')
                    qSock.close()

                    if int(reply.split('\n')[3]) == 1:
                        print("Answer correct")
                        sess['questions'][sess['currentQuestion']].solved = True
                        userdata[sess['user']]['mark'] += sess['questions'][sess['currentQuestion']].attempts
                        self._set_headers(cookie)
                        self.wfile.write(sess['questions'][sess['currentQuestion']].toHTML().encode('UTF-8')) 
                        return
                    else:
                        print("Answer incorrect")
                        sess['questions'][sess['currentQuestion']].attempts -= 1
                        self._set_headers(cookie)
                        self.wfile.write(sess['questions'][sess['currentQuestion']].toHTML(just_failed=True).encode('UTF-8'))
                        return
                elif 'code_submission' in form:
                    #PGquestion
                    submission = form['code_submission'].value

                    if bad_code(submission):
                        #failure
                        print("Answer incorrect")
                        sess['questions'][sess['currentQuestion']].attempts -= 1
                        self._set_headers(cookie)
                        self.wfile.write(sess['questions'][sess['currentQuestion']].toHTML(just_failed=True).encode('UTF-8'))
                        return

                    submission = submission.split('\n')
                    packet = ('REQUEST-VERIF\n'
                            + str(len(submission) + 1) + '\n'
                            + str(sess['questions'][sess['currentQuestion']].id) + '\n')

                    for line in submission:
                        packet += line + "\n"

                    qSock = new_socket()
                    qSock.connect((QHOST, QPORT))
                    qSock.send(packet.encode('UTF-8'))
                    reply = qSock.recv().decode('UTF-8')
                    qSock.close()

                    if int(reply.split()[2]) == 1:
                        #success
                        print("Answer correct")
                        sess['questions'][sess['currentQuestion']].solved = True
                        userdata[sess['user']]['mark'] += sess['questions'][sess['currentQuestion']].attempts
                        self._set_headers(cookie)
                        self.wfile.write(sess['questions'][sess['currentQuestion']].toHTML().encode('UTF-8')) 
                        return
                    else:
                        #failure
                        print("Answer incorrect")
                        sess['questions'][sess['currentQuestion']].attempts -= 1
                        self._set_headers(cookie)
                        self.wfile.write(sess['questions'][sess['currentQuestion']].toHTML(just_failed=True).encode('UTF-8'))
                        return
            else:
                #invalid response
                return


    def _set_headers(self, cookie=None):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        if cookie:
            #re-up expiry and resend
            expiration = datetime.datetime.now() + datetime.timedelta(hours=1)
            cookie['session']['expires'] = 3600
            currentSessions[cookie['session'].value]['expiry'] = expiration
            self.send_header("Set-Cookie", cookie.output(header=''))
        self.end_headers()
        return

    def serve_login(self):
        self._set_headers()
        page = (HTMLHEAD
                + '<h1>Log in to the CITS3002 Quiz</h1>'
                + HTMLFORM
                + '<input type=\"text\" name=\"username\" required>Username<br>'
                + '<input type=\"password\" name=\"password\" required>Password<br>'
                + '<input type=\"submit\" name=\"submit\" value=\"Log In\"><br>'
                + '</form></body></html>')
        self.wfile.write(page.encode('UTF-8'))
        return

    def serve_greeting(self, cookie):
        self._set_headers(cookie=cookie)
        page = (HTMLHEAD
                + '<h1>Welcome: ' + currentSessions[cookie['session'].value]['user'] + '</h1>'
                + '<p>Current score to date: '
                + str(userdata[currentSessions[cookie['session'].value]['user']]['mark'])
                + '</p>'
                + HTMLFORM)
        if 'questions' in currentSessions[cookie['session'].value]:
            page += '<input type=\"submit\" name=\"submit\" value=\"Continue Quiz\"><br>'
        page += ('<input type=\"submit\" name=\"submit\" value=\"Start New Quiz\"><br>'
            + HTMLFOOT)
        self.wfile.write(page.encode('UTF-8'))
        return

def bad_code(submission):
    for word in BADWORDS:
        if word in submission:
            return True
    else:
        return False

                
def new_socket():
    qSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    qContext = ssl.create_default_context(cafile='certificate.pem')
    qSock = qContext.wrap_socket(qSock, server_hostname=HOSTNAME)
    return qSock

if __name__ == '__main__':
    #load user data
    userdata = dict()
    with open("user.txt", "r") as userfile:
        for line in userfile:
            (user, salt, passhash, mark) = line.split(':')
            userdata[user] = {'passhash':passhash, 'mark':int(mark), 'salt':salt}

    #store current session data
    currentSessions = dict()

    #connect to question server
    # qSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # qContext = ssl.create_default_context(cafile='certificate.pem')
    # qSock = qContext.wrap_socket(qSock, server_hostname=HOSTNAME)



    #initialise http server
    httpDaemon = socketserver.TCPServer(('', HTTPPORT), HTTPHandler)
    httpDaemon.socket = ssl.wrap_socket(httpDaemon.socket,
                                        keyfile='key.pem',
                                        certfile='certificate.pem',
                                        server_side=True)

    dummySock = socket.socket()
    dummySock.connect(("8.8.8.8", 53))
    print("Web server now listening at: " + dummySock.getsockname()[0] + ":" + str(HTTPPORT))

    httpDaemon.server_activate()
    httpDaemon.serve_forever()
