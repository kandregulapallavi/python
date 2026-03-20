# Function to perform arithmetic operation

def calculate(num1, num2, operator):
    if operator == '+':
        return num1 + num2
    elif operator == '-':
        return num1 - num2
    elif operator == '*':
        return num1 * num2
    elif operator == '/':
        if num2 != 0:
            return num1 / num2
        else:
            return "Division by zero not allowed"
    else:
        return "Invalid operator"

# Taking input
a = float(input("Enter first number: "))
b = float(input("Enter second number: "))
op = input("Enter operator (+, -, *, /): ")

# Calling function
result = calculate(a, b, op)

print("Result:", result)
