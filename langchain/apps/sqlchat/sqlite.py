import sqlite3

connection = sqlite3.connect("../../_data/student.db")

cursor = connection.cursor()

def create_table():
    """
    Create a table in the SQLite database.
    """
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            class TEXT NOT NULL,
            section TEXT NOT NULL,
            marks INTEGER NOT NULL,
            grade TEXT NOT NULL
        )
    ''')
    connection.commit()
    print("Table created successfully.")


def insert_data(name, age, class_name, section, marks, grade):
    """
    Insert data into the students table.

    Args:
        name (str): Name of the student.
        age (int): Age of the student.
        class_name (str): Class of the student.
        section (str): Section of the student.
        marks (int): Marks obtained by the student.
        grade (str): Grade of the student.
    """
    cursor.execute('''
        INSERT INTO students (name, age, class, section, marks, grade)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, age, class_name, section, marks, grade))
    connection.commit()
    print("Data inserted successfully.")    

if __name__ == "__main__":
    # create_table()
    # insert_data("John Doe", 16, "10th", "A", 85, "B")
    # insert_data("Jane Smith", 15, "9th", "B", 90, "A")
    # insert_data("Alice Johnson", 17, "11th", "C", 78, "C")
    # insert_data("Bob Brown", 16, "10th", "A", 88, "B")
    # insert_data("Charlie Davis", 15, "9th", "B", 92, "A")
    # print("Data inserted successfully.")

    print("Sample data inserted successfully.")
    data=cursor.execute('SELECT * FROM students')
    for row in data:
        print(row)
    
    # Close the connection
    connection.close()  


