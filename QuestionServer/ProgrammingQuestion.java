/*
CITS3002 Final Project - Java Question Server
Jesse Wyatt (20756971)
Joshua Ng (20163079)
Hoang Tuan Anh (21749914)
 */
import java.lang.Runtime;
import java.lang.Process;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Scanner;
import java.util.concurrent.TimeUnit;

public class ProgrammingQuestion implements Question {
	public static final String ENV = "python";
	public static final String S_CODE = "SUBCODE.PY";
	public static final String E_CODE = "EXPCODE.PY";
	public static final String S_SOLN = "SUBSOLN";
	public static final String E_SOLN = "EXPSOLN";
    public int ID;
    public static final int questionType = 1;
    public String questionBody, referenceSolution;

    public ProgrammingQuestion(int ID, String questionBody, String referenceSolution) {
        this.ID = ID;
        this.questionBody = questionBody;
        this.referenceSolution = referenceSolution;
    }

    public int getID() {
        return ID;
    }

    public int checkCorrect(String submittedCode) {
    		try {
    			//write submission to disk
    			FileWriter out = new FileWriter(E_CODE);
    			out.write(referenceSolution);
    			out.close();
    			//write reference to disk
    			out = new FileWriter(S_CODE);
    			out.write(submittedCode);
    			out.close();
    			//run subprocesses
    			ProcessBuilder expBuild = new ProcessBuilder(ENV, E_CODE);
    			expBuild.redirectOutput(new File(E_SOLN));
    			Process expRun = expBuild.start();
    			
    			ProcessBuilder subBuild = new ProcessBuilder(ENV, S_CODE);
    			subBuild.redirectOutput(new File(S_SOLN));
    			Process subRun = subBuild.start();
    			
    			if (!subRun.waitFor(2, TimeUnit.SECONDS)) { //if runs too long then failure
    				expRun.destroy();
    				subRun.destroy();
    				return 0;
    			}
    			
    			//check outputs
    			Scanner expSc = new Scanner(new File(E_SOLN));
    			Scanner subSc = new Scanner(new File(S_SOLN));
    			while (expSc.hasNextLine()) {
    				if (!expSc.nextLine().equals(subSc.nextLine())) {
    					return 0; //if not matching fail
    				}
    			}

    			if (subSc.hasNextLine()) {
    				if (subSc.hasNextLine()) { 
    					return 0; //if submission not finished fail
    				}
    			}
    			
    			//close solution files
    			expSc.close();
    			subSc.close();
    		} catch (Exception e) {
    			e.printStackTrace(); //if exception then code fails
    			return 0;
    		}

        return 1; //submission success
    }

    public String toString() {
        return "ID\n" + ID + "\nTYPE\n" + questionType + "\nBODY\n" + questionBody;
    }
}
   