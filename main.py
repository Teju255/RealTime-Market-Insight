# import pandas as pd

# # Replace 'your_file.csv' with the path to your CSV file
# df = pd.read_csv('data.csv')

# # Display the first few rows
# print(df)
import csv
choice= int(input("Enter Bank Name:\n\t 1 for HDFC\n\t 2 for ICICI\n\t 3 for KOTAK\n\t 4 for IDBI\n\t 5 for SBI\n\t"))
if choice==1:
    file=open('HDFCBANK-EQ.csv')
elif choice==2:
    file=open('ICICIBANK-EQ.csv')
elif choice==3:
    file=open('KOTAKBANK-EQ.csv')
elif choice==4:
    file=open('IDBI.csv')
elif choice==5:
    file=open('SBIN-EQ.csv')
else:
    print("Invalid choice")
    exit()
# file1=open('HDFCBANK.csv')
csvreader=csv.reader(file)
for row in csvreader:
    print(row)

print(file.name)

import matplotlib.pyplot as plt
import pandas as pd

# Load the data
data = pd.read_csv(file.name, parse_dates=['date'])

# Plot the close prices over time
plt.figure(figsize=(12, 6))
ax = plt.gca()
ax.set_facecolor('black')
plt.plot(data['date'], data['close'], label='Close Price', color='cyan')
plt.title('Close Price Over Time')
plt.xlabel('Date and Time')
plt.ylabel('Price')
plt.grid(True)
plt.legend()
# plt.xticks(rotation=45)

plt.tight_layout()
plt.show()


file.close()