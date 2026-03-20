# Program using dictionary comprehension

n = int(input("Enter a number: "))

square_dict = {i: i**2 for i in range(1, n + 1)}

print("Dictionary:", square_dict)
