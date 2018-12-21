# Programming Quiz Servers

## Setup:
- Compile all java classes in /QuestionServer using "javac *.java"
- Start up the Question Server with "java MainClass"
- Observe the listening port of the Question Server
- Start up the Testing Server with python3 TestingServer.py
- Enter the IPv4 address and port number used by Question Server
- Observe the listening port of the Testing Server
- Direct your browser to the listed ip and port using HTTPS
- Follow the prompts to log in and complete a quiz

## Sample accounts:
- User:"peter", Password:"cits3002"
- User:"mary", Password:"orange" 
  
Question Server:  
![Alt Text](https://media.giphy.com/media/1foxyJTSruzVwTKcN2/giphy.gif)  
  
Testing Server:  
![Alt Text](https://media.giphy.com/media/ygwZJD0zSqJcJsDRpL/giphy.gif)  
  
Programming Quiz Website:  
![Alt Text](https://media.giphy.com/media/5QXkxncWSfkOvhwc4F/giphy.gif)  

## Aim of project
This project creates a multi-choice and programming exam website for new programming students. The students interact with the web browser to access network-based application communicated through with a Testing-Server (software). 
  
The Testing-Server authenticates the students, navigates through a sequence of multi-choice questions and programming challenges, receiving the student's attempts, and totalling marks awarded for
correct attempts.  The Testing-Server, in turn, will communicate with a Question-Server (software).  
  
Question-Server generates a sequence of multi-choice questions and
programming challenges for each student, and marks and executes students' attempts.

## Constraints
- The web-browser, Testing-Server, and Question-Server, all execute on different computers (hardware) and, thus, must communicate using network
protocols. 
- The students will be using a web-browser, thus communication between the web-browser and Testing-Server will require the HTTP(S) and HTML protocols.
- The Testing-Server should only manage the testing of students, and must have no 'understanding' of the question or how they are marked.
- The Question-Sever should only provide questions, mark questions and only communicate with Testing-Server (prevent cheating).
- the Testing-Server and Question-Server must execute on different computers (hardware), and must not assume access to any shared
(networked) files.
- the Testing-Server and Question-Server must be written in different programming languages (selected from Java, C, C++, or Python).
- the Question-Server must generate and assess questions written in Java, C, C++, or Python (only one needs to be supported).
- the software must support two or more students simultaneously attempting questions.
- all network traffic must be encrypted using SSL.

## Features
- Pre-registered students are able to login to the Testing-Server using a text-based name and password. 
- Students may then navigate, forwards and backwards, through questions which are either multi-choice questions, or ones setting a short programming challenge 
- If the student's first attempt at a question is correct, they receive 3 marks, 2 marks if their second attempt is correct, and so. 
- Once they have attempted all questions (either correctly or after 3 attempts) they may no longer submit answers. 
- At any time, a student may login, see their progress and total mark to-date, or logout.

## CITS3002 Network and Security - Final Project
Programming Quiz Servers is a student project from the University of Western Australia course CITS3002 Network and Security. 

## Our Team
Jesse Wyatt (20756971)
Joshua Ng (20163079)
Hoang Tuan Anh (21749914)
