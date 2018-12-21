/*
CITS3002 Final Project - Java Question Server
Jesse Wyatt (20756971)
Joshua Ng (20163079)
Hoang Tuan Anh (21749914)
 */
import java.lang.Integer;

public class MultiChoiceQuestion implements Question {
    public int ID, numberOfAnswers, correctAnswer;
    public static final int questionType = 0;
    public String questionBody;
    public String[] answers;

    public MultiChoiceQuestion(int ID, String questionBody,
            int numberOfAnswers, String[] answers, int correctAnswer) {
        this.ID = ID;
        this.questionBody = questionBody;
        this.numberOfAnswers = numberOfAnswers;
        this.answers = answers; 
        	this.correctAnswer = correctAnswer;
    }

    public int getID() {
        return ID;
    }

    public int checkCorrect(String submission) {
        //take answer input as string to match interface
        String sub = submission.replace("\n", "").replace("\r", "");
        if (Integer.parseInt(sub) == correctAnswer) {
        		return 1;
        } else {
        		return 0;
        }
    }

    public String toString() {
        String qBuff = 
            "ID\n" + ID +
            "\nTYPE\n" + questionType +
            "\nBODY\n" + questionBody +
            "\nNUM\n" + numberOfAnswers +
            "\nANS";

        for (String ans : answers) {
            qBuff = qBuff + "\n" + ans;
        }

        return qBuff;
    }
}