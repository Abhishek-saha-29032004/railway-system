import sqlite3 as sql
import pandas as pd
import streamlit as st

conn = sql.connect('railway_system.db')
current_page  = 'login or sign up'
c = conn.cursor()

def create_DB_if_Not_available():
    #create a table to store user info.
    c.execute('''CREATE TABLE IF NOT EXISTS users(username TEXT,password TEXT)''')
    #create a table to store employee info.
    c.execute('''CREATE TABLE IF NOT EXISTS employee(employee_id TEXT,password TEXT,designation TEXT)''')
    #create a table to store train info.
    c.execute('''CREATE TABLE IF NOT EXISTS trains(train_number TEXT,train_name TEXT,departure_date TEXT,starting_designation TEXT,ending_designation TEXT)''')
#return c
create_DB_if_Not_available()

#adding train data
def add_train(train_number,train_name,departure_date,starting_designation,ending_designation):
    c.execute("INSERT INTO trains(train_number,train_name,departure_date,starting_designation,ending_designation) VALUES(?,?,?,?,?)",(train_number,train_name,departure_date,starting_designation,ending_designation))
    conn.commit()
    create_seat_table(train_number)
    
def delete_train(train_number,departure_date):
    # c.execute(f"DROP TABLE seats_{train_number};")
    train_query = c.execute("SELECT * FROM trains WHERE train_number = ?",(train_number))
    train_data = train_query.fetchone()
    
    if train_data:
        c.execute("DELETE FROM trains WHERE train_number = ? AND departure_date = ?",(train_number,departure_date))
        conn.commit()
        st.success(f"Train with train number {train_number} has been deleted.")
    else:
        st.error(f"Train with train number {train_number} is unavailable.")
    
conn = sql.connect('railway_system.db')
c = conn.cursor()

def create_seat_table(train_number):
    #create table to store seats under a particular train number
    c.execute(f'''
              CREATE TABLE IF NOT EXISTS seats_{train_number}(
                  seat_number INTEGER PRIMARY KEY,
                  seat_type TEXT,
                  booked INTEGER,
                  passenger_name TEXT,
                  passenger_age INTEGER,
                  passenger_gender TEXT
              )
              ''')
    for i in range(1,51):
        val = catagorize_seat(i)
        c.execute(f'''
                  INSERT INTO seats_{train_number}(
                      seat_number,seat_type,booked,passenger_name,passenger_age,passenger_gender
                  ) VALUES (?,?,?,?,?,?);
                  ''',(i , val , 0 , "" , "" , ""))
        
    conn.commit()
    
def catagorize_seat(seat_number):
    if(seat_number % 10) in [0,4,5,9]:
        return "window"
    elif(seat_number % 10) in [2,3,6,7]:
        return "upper"
    else:
        return "lower"
    
