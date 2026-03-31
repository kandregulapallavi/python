using System;

interface Exam
{
	bool Pass(int mark);
}

interface Classify
{
	string Division(int average);
}

class Result : Exam, Classify
{
	
	public bool Pass(int mark)
	{
		return mark >= 50;
	}

	
	public string Division(int average)
	{
		if (average >= 60)
			return "First";
		else if (average >= 50)
			return "Second";
		else
			return "No division";
	}
}


class Program
{
	static void Main(string[] args)
	{
		Result r = new Result();

		int mark = 55;
		int average = 58;

		Console.WriteLine("Pass Status: " + r.Pass(mark));
		Console.WriteLine("Division: " + r.Division(average));
	}
}
