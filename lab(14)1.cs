using System;

class Employee
{
	int employeeId;
	string name;
	double salary;

	public Employee()
	{
		employeeId = 0;
		name = "Not Assigned";
		salary = 0.0;
	}

	public Employee(int id, string n, double sal)
	{
		employeeId = id;
		name = n;
		salary = sal;
	}

	public double CalculateAnnualSalary()
	{
		return salary * 12;
	}

	public void Display()
	{
		Console.WriteLine("Employee ID: " + employeeId);
		Console.WriteLine("Name: " + name);
		Console.WriteLine("Monthly Salary: " + salary);
		Console.WriteLine("Annual Salary: " + CalculateAnnualSalary());
	}
}

class Program
{
	static void Main()
	{
		Employee e1 = new Employee();
		e1.Display();

		Console.WriteLine();

		Employee e2 = new Employee(101, "Pallavi", 25000);
		e2.Display();
	}
}
