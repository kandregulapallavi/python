import matplotlib.pyplot as plt

# Sample data
categories = ['A', 'B', 'C', 'D', 'E']
values = [10, 24, 36, 18, 30]

# Create bar plot
plt.bar(
    categories,           # x-axis labels
    values,               # heights of bars
    color='skyblue',      # bar color
    edgecolor='black',    # border color
    width=0.5,            # width of bars
    align='center',       # alignment: 'center' or 'edge'
    alpha=0.8,            # transparency (0 to 1)
    linewidth=1.5,        # border thickness
    hatch='/',            # pattern on bars
    label='Sample Data'   # legend label
)

# Titles and labels
plt.title("Bar Plot Example", fontsize=16, color='darkblue')
plt.xlabel("Categories", fontsize=12)
plt.ylabel("Values", fontsize=12)

# Additional features
plt.grid(axis='y', linestyle='--', alpha=0.7)  # grid lines
plt.legend()                                  # show legend
plt.xticks(rotation=45)                       # rotate x labels

# Show plot
plt.show()
