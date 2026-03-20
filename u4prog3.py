numbers = input("Enter numbers separated by commas: ")

num_list = [int(i) for i in numbers.split(",")]
num_tuple = tuple(num_list)

print("List:", num_list)
print("Tuple:", num_tuple)
