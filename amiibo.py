import sqlite3
from sqlite3 import OperationalError
import os

db      = sqlite3.connect('amiibo.db')
cursor  = db.cursor()

def print_data(data):
    print('-'*40)
    for row in data:
        print("%s" % (row,))
    print('-'*40)

def print_list(_list):
    print()
    i = 0
    new_list = []
    print('-'*30)
    for item in _list:
        series_name = item.__getitem__(0)
        print(str(i) + ' | ' + series_name)
        new_list.append(series_name)
        i += 1
    print('-'*30)
    print()
    return new_list

def determine_function(choice):
    if choice == "0":
        first_time_setup()
    elif choice == "1":
        add_new_amiibo()
    elif choice == "2":
        view_by_series()
    elif choice == "3":
        view_needed()
    elif choice == "DT":
        drop_tables()
    elif choice == "cls":
        os.system('cls')
    elif choice == "-1":
        db.close()
        exit(0)
    else:
        print('Invalid Function Name')
    return

def print_message(msg):
    print('*'*20)
    print(msg)
    print('*'*20)

def print_menu():
    print("0) Perform first time setup")
    print("DT) Drop tables")
    print("1) Add new amiibo")
    print("2) View by Series")
    print("3) View ones needed")
    print("-1) Exit\n")

def determine_is_owned(is_owned):
    if is_owned == 'y' or is_owned == 'Y':
        owned = True
    else:
        owned = False
    return owned

def deteremine_is_jap_only(is_jap_only):
    if is_jap_only == 'y' or is_jap_only == 'Y':
        jap_only = True
    else:
        jap_only = False
    return jap_only

def first_time_setup():
    try :
        create_table = """
        CREATE TABLE series (
            name text
        );
        """
        cursor.execute(create_table)
        print_message('Created Series Table')
        create_table = """
        CREATE TABLE amiibo (
            name text,
            series_id int,
            release_date text,
            is_owned int,
            is_jap_only int,
            FOREIGN KEY(series_id) REFERENCES series(rowid)
        );
        """
        cursor.execute(create_table)
        print_message('Created Amiibo Table')
        return
    except OperationalError as e:
        print(e)
        print('Tables already exist!')
        return

def add_new_amiibo():
    print('Time to add a new amiibo')
    name            = input('\nWhat is the name of this amiibo?\n')

    select = """
    SELECT *
    FROM series
    """
    cursor.execute(select)
    series_list     = cursor.fetchall()
    
    reg_input       = False
    if series_list.__len__() > 0:
        new_list = print_list(series_list)
        a = input('Here\'s a list of series currently\navailable, is it one of these?\nPress the number to use that, otherwise -1\n')
        if a == "-1":
            reg_input   = True
        else:
            series      = new_list[int(a)]
            print('\nYou chose ' + series)
    if series_list.__len__() == 0 or reg_input:
        series          = input('What is the series?\n')
    
    release_date    = input('What is the original release date?\n')
    is_owned        = input('Do you own it? y/n\n')
    is_jap_only     = input('Is it a japanese only amiibo? y/n\n')
    
    select = """
    SELECT rowid 
    FROM Series
    WHERE name like (?)
    """  
    cursor.execute(select, (series,))
    all_entries = cursor.fetchall()
    series_id   = all_entries
    
    if series_id.__len__() == 0:
        print('Looks like it\'s a new series, lemme add that for you')
        
        insert = """
        INSERT INTO series
        VALUES (?);"""
        cursor.execute(insert, (series,))
        db.commit()

        select = """
        SELECT last_insert_rowid();
        """
        cursor.execute(select)
        series_id = cursor.fetchall()[0].__getitem__(0)
    else:
        series_id = all_entries[0].__getitem__(0)
    
    owned       = determine_is_owned(is_owned)
    jap_only    = deteremine_is_jap_only(is_jap_only)
    insert = """
    INSERT INTO amiibo
    VALUES (?,?,?,?,?);
    """
    cursor.execute(insert, (name, series_id, release_date, owned, jap_only))
    db.commit()
    print('\n' + name + ' has been added!')
    return

def view_by_series():
    select = """
    SELECT *
    FROM series
    """
    cursor.execute(select)
    series_list     = cursor.fetchall()
    new_list = print_list(series_list)
    
    series      = input('What series do you want to view by?\nType the number or \'all\' for all\n')
    
    if series == 'all':
        select = """
        SELECT *
        FROM amiibo A
        INNER JOIN series S on A.series_id = S.rowid
        """
        print('You have selected all')
        cursor.execute(select)
    else:
        view_by      = new_list[int(series)]
        print('You have selected ' + view_by)
        select = """
        SELECT *
        FROM amiibo A
        INNER JOIN series S on A.series_id = S.rowid
        WHERE series_id = (?)
        """
        series = int(series) + 1
        cursor.execute(select, (series,))
    data = cursor.fetchall()
    print_data(data)
    return

def view_needed():
    print('View Needed')
    return

def drop_tables():
    try:
        drop_table = """
        DROP TABLE amiibo
        """
        cursor.execute(drop_table)
        print_message('DROPPED AMIIBO')
    except OperationalError:
        print('Amiibo already dropped\n')
    
    try:
        drop_table = """
        DROP TABLE series
        """
        cursor.execute(drop_table)
        print_message('DROPPED SERIES')
    except OperationalError:
        print('Series already dropped\n')

def main():
    print("Welcome to the amiibo db!")
    print_menu()
    c = input("What would you like to do? \n")
    while c != -1:
        determine_function(c)
        print_menu()
        c = input("What would you like to do? \n")

if __name__ == "__main__":
    main()