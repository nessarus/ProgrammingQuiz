/*
CITS3002 Final Project - Java Question Server
Jesse Wyatt (20756971)
Joshua Ng (20163079)
Hoang Tuan Anh (21749914)
 */
public interface Question {
    public int getID();

    public int checkCorrect(String submission);

    public String toString();
}