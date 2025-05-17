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
    
def allocate_next_available_seat(train_number,seat_type):
    #find the next available seat 
    #for seat_number in range(1,51):
    seat_query = c.execute(
        f"SELECT seat_number FROM seats_{train_number} WHERE booked = 0 AND seat_type = ? ORDER BY seat_number asc",(seat_type) 
    )
    result = seat_query.fetchall()
    #print(result)
    if result:
        return result[0]
    
def book_ticket(train_number,passenger_name,passenger_age,passenger_gender,seat_type):
    train_query = c.execute(
        "SELECT * FROM trains WHERE train_number = ?",(train_number)
    )    
    train_data = train_query.fetchone()
    if train_data:
        seat_number = allocate_next_available_seat(train_number,seat_type)
        #updating the seat as booked and storing passenger details
        if seat_number:
            c.execute(
                f"UPDATE seats_{train_number} SET booked = 1 , seat_type = ? , passenger_name = ? , passenger_age = ? , passenger_gender = ? WHERE seat_number = ?",(seat_type,passenger_name,passenger_age,passenger_gender,seat_number[0])
            )
            conn.commit()
            st.success(f"Successfully booked seat {seat_number[0]} ({seat_type}) for {passenger_name}.")
        else:
            st.error("No available seats for booking in this train.")
    else:
        st.error(f"No such train with number {train_number} found")
        
def cancel_tickets(train_number,seat_number):
    train_query = c.execute(
        "SELECT * FROM trains WHERE train_number = ?", (train_number)
    )       
    
    train_data = train_query.fetchone()
    
    if train_data:
        c.execute(
            f"UPDATE seats_{train_number} SET booked = 0 , passenger_name = '' , passenger_age = '' , passenger_gender = '' WHERE seat_number = ?",(seat_number))
        conn.commit()
        st.success(f"Successfully canceled seat {seat_number} from {train_number}")
    else:
        st.error(f"No such train with train number = {train_number} is available.")
        
def search_train_by_train_number(train_number):
    train_query = c.execute(
        "SELECT * FROM trains WHERE train_number = ?",(train_number)
    )
    train_data = train_query.fetchone()
    return train_data

def view_seats(train_number):
    train_query = c.execute(
        "SELECT * FROM trains WHERE train_number = ?",(train_number)
    )
    train_data = train_query.fetchone()
    if train_data:
        seat_query = c.execute(
            f"SELECT 'Number:' || seat_number, '\n Type:' || seat_type, '\n Name:' || passenger_name, '\n Age:' || passenger_age, '\n Gender:' || passenger_gender as Details , booked FROM seats_{train_number} ORDER BY seat_number ASC"
        )
        result = seat_query.fetchall()
        if result:
            st.dataframe(data = result)
        else:
            st.error(f"No such train with number {train_number} is available.")

def train_functions():
    st.title("TRAIN ADMIN")
    functions = st.sidebar.selectbox("SELECT train functions", [
        "Add Train" , "View Train" , "Search Train" , "Delete Train" , "Book Ticket" , "Cancel Ticket" , "View Seats"
    ])
    if functions == "Add Train":
        st.header("Add new train.")
        with st.form(key = 'new_train_details'):
            train_number = st.text_input("Train Number")
            train_name = st.text_input("Train Name")
            departure_date = st.text_input("Departure Date")
            starting_destination = st.text_input("Starting destination")
            ending_destination = st.text_input("Ending destination")
            submitted = st.form_submit_button("Add Train")
            
        if submitted and train_number != '' and train_name != '' and departure_date != '' and starting_destination != '' and ending_destination != '':
            add_train(train_number,train_name,departure_date,starting_destination,ending_destination)
            st.success("Train added successfully")
            
    elif functions == "View Trains":
        st.title('View all trains')
        #query all available trains from the database.
        train_query = c.execute('SELECT * FROM trains')
        trains = train_query.fetchall()
        
        if trains:
            st.header("Available trains ")
            st.dataframe(data = trains)
        else:
            st.error("No trains available now")
            
    elif functions == "Search Train":
        st.title("Train detail search")
        st.write("Search by train number")
        train_number = st.text_input("Enter a train number:")
        st.write("Search by starting and ending destination:")
        starting_destination = st.text_input("Starting Destination:")
        ending_destination = st.text_input("Ending Destination:")
        
        if st.button("Search by train number"):
            if train_number:
                train_data = search_train_by_train_number(train_number)
                if train_data:
                    st.header("Search Result:")
                    df = pd.DataFrame([train_data],columns=["Train Number","Train Name","Departure Date","Starting Destination","Ending Destination"])
                    st.table(df)
                else:
                    st.error("No trains found for the given destination.")
                    
    elif functions == "Delete Trains":
        st.title("Delete Train")
        train_number = st.text_input("Enter a train number:")
        departure_date = st.date_input("Departure Date of the train")
        
        if st.button("Delete Train"):
            if train_number:
                c.execute(f"DROP TABLE IF EXISTS seats_{train_number}")
                delete_train(train_number,departure_date)
                
    elif functions == "Book Ticket":
        st.title("Book Train Ticket")
        train_number = st.text_input("Enter train number:")
        seat_type = st.selectbox(
            'Seat Type : ',["Aisle","Window","Middle"], index = 0
        )
        
        passenger_name = st.text_input("Enter the name:")
        passenger_age = st.number_input("Enter age:",min_value=1)
        passenger_gender = st.selectbox(
            "Passenger Gender:",['Male','Female','Non-Binary'],index=0
        )
        
        if st.button("Book Ticket"):
            if train_number and passenger_name and passenger_age and passenger_gender:
                book_ticket(train_number,passenger_name,passenger_age,passenger_gender,seat_type)
    
    elif functions == "Cancel Ticket":
        st.title("Tickets Cancelled.")
        train_number = st.text_input("Enter train number:")
        seat_number = st.number_input("Enter seat number:",min_value=1)
        
        if st.button("Cancel Ticket"):
            if train_number and seat_number:
                cancel_tickets(train_number,seat_number)
                
    elif functions == "View Seats":
        st.title("View seats")
        train_number = st.text_input("Enter train number:")
        if st.button("Submit"):
            if train_number:
                view_seats(train_number)
                
train_functions()
conn.close()

conn.close()

              