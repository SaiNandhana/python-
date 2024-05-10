#modules used

import mysql.connector        #connecting sql database to python 
import csv                    #csv module for storing user data
from datetime import datetime #provides classes for working with dates and times


#opening csv file and defining header

csv_file=open("stock_info.csv","w")
writer=csv.writer(csv_file)
l=["Name","Qty","Date","Type"]
writer.writerow(l)
csv_file.flush()


#This function creates two tables (stock_master, stock_trans)
#in the MySQL database if they don't already exist.

def create_stock_table():
    mycursor.execute("create table if not exists stock_master(symbol char(4) primary key, name varchar(30), price float)")
    mycursor.execute("create table if not exists stock_trans(symbol char(4), quantity int, dot date, ttype char(1), foreign key (symbol) references stock_master(symbol))")
    mydb.commit()


#Function prompts the user to input information about a new stock
#It checks if a stock with the given symbol already exists
#If not, it inserts the new stock into the stock_master table
#and appends information to the CSV file.

def add_stock():
    symbol = input("Enter stock symbol (e.g., AAPL): ")
    name = input("Enter stock name: ")
    price = float(input("Enter stock price: "))
    
    # Check if the symbol already exists
    mycursor.execute(f"select * from stock_master where symbol='{symbol}'")
    existing_stock = mycursor.fetchone()

    if existing_stock:
        print(f"Stock with symbol '{symbol}' already exists. Use 'Buy Stock' to update.")
    else:
        mycursor.execute(f"insert into stock_master values('{symbol}', '{name}', {price})")
        mydb.commit()
        
        with open("stock_info.csv", mode='a', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([symbol, name, price, 0])

        print("Stock added successfully!")
        

#This function handles the buying or selling of stocks
#checking if transaction type is valid(Buy or Sell)
#inserts records in the 'stock_trans' table, updating stock price
#in the 'stock_master' table and appends info into the csv file

def buy_sell_stock(ttype=None):
    
    if ttype not in ('B', 'S'):
        print("Error: Invalid transaction type. Please enter 'B' for Buy or 'S' for Sell.")
        return
    
    symbol = input("Enter stock symbol: ")
    quantity = int(input("Enter quantity to {}: ".format(ttype.lower())))
    dot = datetime.now().strftime("%Y-%m-%d")

    # Insert transaction record
    mycursor.execute("insert into stock_trans values('{}', {}, '{}', '{}')".format(symbol, quantity, dot, ttype))

    mydb.commit()

    # Update stock price using a subquery in SET
    update_query = "update stock_master set price = (select price from (select price from stock_master where symbol='{}') as subquery) {} {}".format(symbol, '+' if ttype == 'Buy' else '-', quantity)
    mycursor.execute(update_query)
    mydb.commit()

    with open("stock_info.csv", mode='a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([symbol, quantity, dot, ttype[0]])

    print("Stock {} successfully!".format(ttype.lower()))


#Prompts user to input stock symbol, retrieves info about the stock
#from the 'stock_master' table in the database and displays info
#It finally calls the 'analyze_stock function' for stock analysis
    
def display_stock_info():
    symbol = input("Enter stock symbol: ")
    mycursor.execute(f"select * from stock_master where symbol='{symbol}'")
    stock_info = mycursor.fetchone()

    if stock_info:
        print("Stock Information:")
        print("Symbol:", stock_info[0])
        print("Name:", stock_info[1])
        print("Price:", stock_info[2])
        analyze_stock(symbol)
    else:
        print("Stock not found.")

        
#This function analyzes the stock transactions for a given stock symbol
#It retrieves transaction information from the stock_trans table in the database
#Then calculating the total quantity of stocks bought or sold, displaying an
#investment decision based on the total quantity.
        
def analyze_stock(symbol):
    mycursor.execute(f"select quantity, ttype from stock_trans where symbol='{symbol}'")
    transactions = mycursor.fetchall()

    if transactions:
        total_quantity = 0
        for quantity, ttype in transactions:
            if ttype == 'B':
                total_quantity += quantity
            elif ttype == 'S':
                total_quantity -= quantity

        print("Stock Analysis:")
        print("Total Quantity:", total_quantity)
        print("Investment Decision: Buy" if total_quantity < 0 else "Investment Decision: Sell")
    else:
        print("No transaction history for this stock.")


def main():
    create_stock_table() #called to ensure that the necessary tables are created
                         #creates two tables: stock_master and stock_trans
    
    #Menu-driven program for user service
    
    while True:
        print("1=Add Stock")
        print("2=Buy/Sell Stock")
        print("3=Display Stock Information")
        print("4=Exit")

        try:
            choice = int(input("Enter your choice: "))

            if choice == 1:
                add_stock()
            elif choice == 2:
                ttype = input("Enter transaction type (B for Buy, S for Sell): ").upper()[0]
                buy_sell_stock(ttype)
            elif choice == 3:
                display_stock_info()
            elif choice == 4:
                break
            else:
                print("Invalid choice. Please enter a valid option.")
        except ValueError: # Catches an exception if the user doesn't enter a valid integer.
            print("Invalid input. Please enter a number.")
        except mysql.connector.Error as err: #Catches a MySQL database-related exception.
            print(f"MySQL Error: {err}")
        except Exception as e: #Catches any other unexpected exceptions.
            print(f"An unexpected error occurred: {e}")


#Establishes a connection to a MySQL database

#Ensures that this block of code is executed only if the script is run directly
#and not imported as a module into another script
            
if __name__ == "__main__":
    mydb = mysql.connector.connect(host="localhost", user="root", passwd="nandhana", database="STOCKANALYSIS")
    mycursor = mydb.cursor() #The cursor is used to execute SQL queries and fetch results.
    main()
