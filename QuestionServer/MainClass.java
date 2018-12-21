/*
CITS3002 Final Project - Java Question Server Main
Jesse Wyatt (20756971)
Joshua Ng (20163079)
Hoang Tuan Anh (21749914)
 */
import java.net.Socket;
import java.security.KeyStore;
import java.util.Scanner;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.ServerSocket;
import java.net.InetAddress;
import javax.net.ServerSocketFactory;
import javax.net.ssl.KeyManagerFactory;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLServerSocketFactory;
import java.util.Arrays;
import java.io.DataOutputStream;
import java.util.ArrayList;
import java.util.Random;


public class MainClass {

	//file constants
	private static final String Q_FILE = "questions.txt";
	private static final String KEY_FILE = "keystore.p12";
	//keystore pass
	private static final char[] keyPass = "BigRedDogBoy".toCharArray();
	//absolute paths
	private static String startupPath = new File("").getAbsolutePath() + "/";
	private static String qFilePath = startupPath + Q_FILE;
	private static String keyFilePath = startupPath + KEY_FILE;
	//port constant
	private static final int PORT = 3030;
	//header constants
	private static final byte[] REQUEST_VERIF = "REQUEST-VERIF".getBytes();
	private static final byte[] REQUEST_QUEST = "REQUEST-QUEST".getBytes();

	private static ArrayList<Question> questionList;
	private static int numQuestions;
	private static String ipString;


	public static void main(String[] args) throws IOException {
		System.out.println(startupPath);
		System.out.println("Starting QuestionServer...");
		
		System.out.println("Loading questions from: " + Q_FILE);
		numQuestions = loadQuestions(qFilePath);
		System.out.println("" + numQuestions + " questions loaded");

		System.out.println("Setting up socket factory...");
		ServerSocketFactory ssf = getServerSocketFactory();
		
		System.out.println("Setting up listener...");
		ServerSocket listenerSocket = ssf.createServerSocket(PORT);
		ipString = InetAddress.getLocalHost().toString();
		System.out.println("Set-up complete! Now listening at: " + ipString + ":" + PORT);

		try {
			while (true) {
				Socket connectionSocket = listenerSocket.accept();
				System.out.println("INCOMING: " + connectionSocket.getInetAddress().toString());
				try {
					InputStream sockInRaw = connectionSocket.getInputStream();
					Scanner sockIn = new Scanner(sockInRaw);
					DataOutputStream sockOut = new DataOutputStream(connectionSocket.getOutputStream());
					byte[] headerType = new byte[13];
					int payloadLen;
					//read first 13 bytes and check if recognised header
					if (sockInRaw.read(headerType) > 0) {
						System.out.println(sockIn.nextLine());
						if (Arrays.equals(headerType, REQUEST_VERIF)) {
							System.out.println("Verification Request Acknowledged");
							payloadLen = Integer.parseInt(sockIn.nextLine());
							sockOut.writeUTF(respondVerify(sockIn, payloadLen));
						} else if (Arrays.equals(headerType, REQUEST_QUEST)) {
							System.out.println("Question Request Acknowledged");
							payloadLen = Integer.parseInt(sockIn.nextLine());
							sockOut.writeUTF(respondQuestions(sockIn, payloadLen));
						} else {
							System.out.println("Unknown Request");
						}
					}
					sockOut.close();
					sockIn.close();
					sockInRaw.close();
					connectionSocket.close();
				} finally {
					System.out.println("CLOSING");
					connectionSocket.close();
				}
			}
		} finally {
			listenerSocket.close();
		}
	}
	
	private static ServerSocketFactory getServerSocketFactory() {
		try {
			SSLContext context = SSLContext.getInstance("TLS");
			KeyManagerFactory managerFactory = KeyManagerFactory.getInstance("SunX509");
			KeyStore store = KeyStore.getInstance("PKCS12");
			
			store.load(new FileInputStream(keyFilePath), keyPass);
			managerFactory.init(store, keyPass);
			context.init(managerFactory.getKeyManagers(), null, null);
			
			SSLServerSocketFactory sockFactory = context.getServerSocketFactory();
			return sockFactory;
		} catch (Exception e) {
			e.printStackTrace();
		}
		return null;
	}

	private static int loadQuestions(String filepath) throws IOException {
		Scanner sc = new Scanner(new FileInputStream(filepath));
		questionList = new ArrayList<Question>();
		int id, type;
		String body;
		Question question;
		
		while (sc.hasNextLine()) {
			sc.nextLine(); //ID
			id = Integer.parseInt(sc.nextLine());
			sc.nextLine(); //TYPE
			type = Integer.parseInt(sc.nextLine());
			sc.nextLine(); //BODY
			body = sc.nextLine();
			
			if (type == 0) { //multiple choice
				System.out.println("ID: " + id + " TYPE: 0 Multiple Choice");
				sc.nextLine(); //NUM
				int numAnswers = Integer.parseInt(sc.nextLine());
				String[] answers = new String[numAnswers];
				sc.nextLine(); //ANS
				for (int i = 0; i < numAnswers; ++i) {
					answers[i] = sc.nextLine();
				}
				sc.nextLine(); //EXPECTED
				int correctAnswer = Integer.parseInt(sc.nextLine());
				sc.nextLine(); //SPACER
				question = new MultiChoiceQuestion(id, body, numAnswers, answers, correctAnswer);
			} else { //programming
				System.out.println("ID: " + id + " TYPE 1 Programming Question");
				sc.nextLine(); //EXPECTED
				String line = sc.nextLine();
				String expected = "";
				while (!line.equals("---")) {
					expected = expected + "\n" +  line;
					line = sc.nextLine();
				}
				question = new ProgrammingQuestion(id, body, expected);
			}

			questionList.add(question);
		}
		sc.close();
		return questionList.size();
	}

	private static String respondVerify(Scanner sockIn, int len) throws IOException {
		System.out.println("questionID:");
		int questionID = Integer.parseInt(sockIn.nextLine());
		System.out.println(questionID);
		
		String answer = "";
		for (int i = 0; i < len - 1; ++i) {
			answer = answer + sockIn.nextLine() + "\n";
		}


		if (questionID >= questionList.size()) {
			System.out.println("Invalid question ID rejected");
			return "ERROR-INVALID-ID\n";
		}
		
		int result = questionList.get(questionID).checkCorrect(answer);
		System.out.println("RESULT:");
		System.out.println(result);
		
		return "RESPONSE-VERIF\n" + "\nRESULT\n" + result + "\n";
	}

	private static String respondQuestions(Scanner sockIn, int numRequested) {

		String response = "";
		Random qSelect = new Random(System.currentTimeMillis());
		for (int i = 0; i < numRequested; ++i) {
			response = response + questionList.get(qSelect.nextInt(numQuestions)).toString() + "---";
		}
		int length = response.length();
		String lengthString = String.format("%05d", length);
		return "RESPONSE-QUEST\n" + lengthString + response;
	}
}
