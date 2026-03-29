# Program to read a text file line by line

file = open("names.txt", "r")

for line in file:
    print(line.strip())
file.close()
