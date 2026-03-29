# Program to read names and store in a text file

# Open file in write mode
file = open("names.txt", "w")

# Input number of names
n = int(input("Enter number of names: "))

# Loop to take names
for i in range(n):
    name = input("Enter name: ")
    file.write(name + "\n")   # Write each name in new line

# Close the file
file.close()

print("Names successfully saved to file.")
