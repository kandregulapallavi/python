total = 0
count = 0

with open("numbers.txt", "r") as file:
    for line in file:
        try:
            num = int(line.strip())
            print(num)
            total += num
            count += 1
        except:
            print("Invalid data skipped")

if count > 0:
    print("Total =", total)
    print("Average =", total / count)
else:
    print("No valid numbers found")
