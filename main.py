# demo support desk and ticket management system from terminal

# import modules
import json
from stdiomask import getpass
import hashlib
import os
from time import sleep
import gspread

# define a small terminal clear function
clear = lambda: os.system('clear')

# attempt to connect to google servers
try:
    # define the google sheets api credentials
    gc = gspread.service_account(filename="creds.json")

    # specify which google drive file
    sh = gc.open("python_helpdesk")

    # specify the tickets worksheet
    get_ticket_api = sh.worksheet("tickets")

    #specify the auth worksheet
    get_auth_api = sh.worksheet("auth")

    # specify user permissions worksheet
    get_permissions_api = sh.worksheet("user_permissions")

# if connection fails, exit the program
except:
    clear()
    print("Program could not connect to Google Servers.")
    sleep(5)
    exit()


#define global variables 
operator = ""
program = True


# define function for login authentication menu
def auth():

    # clear terminal and print the menu
    clear()
    print("--MAIN MENU--\n")
    print("1 ----- LOGIN")
    print("2 -- REGISTER")
    print("3 ------ QUIT\n")

    # check if the user chose a valid option
    while True:
        userChoice = str(input("Choose an option: "))
        if userChoice in ["1", "2", "3"]:
            break
    
    # user chose to login
    if userChoice == "1":
        login()

    # user chose to register
    elif userChoice == "2":
        register()

    # user chose to quit
    elif userChoice == "3":
        clear()
        exit()


# define register new user function
def register():

    # clear the terminal and print the register user menu
    clear()
    print("--REGISTER--")
    print("------------\n")

    # check if the user entered a valid username
    while True:
        userName = input("Enter your desired username: ").lower()
        if userName != "":
            break

    # send the username to be formatted
    userName = sanitizeName(userName)

    # ask the user for a password and check if it's valid
    while True:

        # using getpass as input to hide characters
        userPassword = getpass("Enter your unique password: ")
        if userPassword != '':
            break
    
    # ask user to confirm password and if it matches
    while True:
        confirmPassword = getpass("Confirm your password: ")

        # check the password matches
        if confirmPassword == userPassword:
            break

        # error message if passwords do not match
        else:
            print("Passwords do not match!\n")

    # send username and password to check if they already exist
    if userAlreadyExists(userName, userPassword):
        while True:
            print("")

            # if they do, give an error message
            error = input("You already registered!\n\nPress 'T' to try again\nPress 'L' to Login\n").lower()

            # user option to try again
            if error == 't':
                register()
                break

            # user option to login
            elif error == 'l':
                login()
                break

    # if new unique user, add the user info to a file via addUserInfo()
    addUserInfo([userName, hash_password(userPassword)])

    # print that the user is registered
    print("")
    print("Registered!")

    # set global userID for permission purposes
    global userID
    userID = userName

    # start the main program
    main_program()


# define login user function
def login():

    # clear the terminal and print login screen
    clear()
    print("LOGIN")
    print("-----")
    print()

    # define the users info as empty
    usersInfo = {}

    # get the user database and load into temp auth
    temp_auth = get_auth_api.get_all_values()

    # format the information into a dictionary
    usersInfo = { k[0]: k[1] for k in temp_auth }

    # ask user for username input
    while True:
        userName = input("Enter Your Username: ").lower()
        userName = sanitizeName(userName)

        # check if the user is in the user database
        if userName not in usersInfo:
            print("You Are Not Registered")
            print()

        # continue if they are
        else:
            break

    # ask the user for a password and encrypt
    while True:

        # use getpass to hide the user input
        userPassword = getpass("Enter Your Password: ")
        if not check_password_hash(userPassword, usersInfo[userName]):
            print("Incorrect Password")
            print()
        else:
            break

    # print login successful
    print()
    print("Logged In!")

    # set global username ID for permission purposes
    global userID
    userID = userName

    # open the main program
    main_program()

# define add new user information function
def addUserInfo(userInfo):

    #convert the username into a string
    user = str(userInfo[0])

    # convert the password hash into a string
    passw = str(userInfo[1])

    # convert the username and password into a list
    user_creds = [user, passw]

    #push the list to a new line in the users database
    get_auth_api.append_row(user_creds)


# check to see if a user already exists
def userAlreadyExists(userName, userPassword):

    # convert password input into hash
    userPassword = hash_password(userPassword)

    # define empty dictionary
    usersInfo = {}

    # load the user database into tempcheck
    temp_check = get_auth_api.get_all_values()

    # convert temp check into a dictionary (questionably unnessesary)
    full_check = { k[0]: k[1] for k in temp_check } 
    
    # create a loop to check the user input against the user database
    for line in temp_check:
        if line[0] == userName and line[1] == userPassword:
            usersInfo.update({line[0]: line[1]})
    if usersInfo == {}:
        return False
    return usersInfo[userName] == userPassword


# define sanitize name function
def sanitizeName(userName):

    # format the username
    userName = userName.split()
    userName = '-'.join(userName)
    return userName


# define hash password funciton
def hash_password(password):

    # use hashlib to encrypt the password
    return hashlib.sha256(str.encode(password)).hexdigest()


# define check password hash function
def check_password_hash(password, hash):

    # I'm not sure what this actually does
    return hash_password(password) == hash


#define the function to print the list of tickets
def view_tickets():
    # clear screen and print a blank line
    clear()
    print("\n")

    # load tickets.json as a list
    tickets = []

    #with open("tickets.json", 'r') as f:   
    #    tickets = json.load(f)

    # load the tickets into a list from google sheet api
    tickets = get_ticket_api.get_all_values()

    # print the number of tickets there are
    print("There are " + str(len(tickets)) + " tickets.")
    list_choice = 0

    # go through every item in the list
    for i in tickets:

        # check if each ticket is open or closed
        if tickets[list_choice][3] == "open":
            ticket_status = "(Open)"
        else:
            ticket_status = "(Closed)"

        # print each ticket with its number, brief description, and status
        print(str(int(list_choice) + 1) + ": " + str(tickets[list_choice][0]) + " " + ticket_status)

        # add one to list choice to go through the entire list
        list_choice += 1

    # ask the user which ticket they would like to view
    view_ticket = input("Which would you like to view? ")

    # add try exception in case of an error
    try:
        # set the user input to an integer starting at 0 instead of 1
        view_ticket = int(view_ticket)
        view_ticket = view_ticket - 1
        
        clear()

        # print the support ticket information
        print("\nNow viewing ticket " + str(int(view_ticket) + 1) + ".")
        print("\nUser: " + str(tickets[view_ticket][2]))
        print("Subject: " + str(tickets[view_ticket][0]))
        print("Description: " + str(tickets[view_ticket][1]))

        
        # if the ticket is open, inform user
        if tickets[view_ticket][3] == "open":
            print("Ticket " + str(int(view_ticket) + 1) + " is still open.")

        # if the ticket has been resolved, inform the user of the user who resolved it and solution
        else:
            print("Ticket " + str(int(view_ticket) + 1) + " was closed by " + str(tickets[view_ticket][5]) + ".")
            print("The reason given was '" + str(tickets[view_ticket][4]) + "'")

        wait = input("\nPress enter to return to menu.")


    # handle possible errors with a simple error message
    except:
        print("I'm sorry, there was an error with your selection.\n")
        sleep(3)


# define the function to add a new support ticket
def add_ticket():
    
    # clear screen
    clear()


    # define all the parts of a ticket and gather input
    employee_name = userID
    ticket_name = input("Please give a brief description of your issue: ")
    ticket_description = input("Please give a detailed description of your issue: ")
    support_name = ""
    support_desc = ""
    resolved = "open"
    
    # combine ticket parts into a list
    ticket_temp = list((ticket_name, ticket_description, employee_name, resolved, support_desc, support_name))

    # push the new ticket out to the server
    get_ticket_api.append_row(ticket_temp)

    print("")
    sleep(3)


# define the function to modify tickets
def modify_tickets():
    clear()
    print("--CHOOSE A SUPPORT TICKET TO MODIFY--")

    # load tickets.json as a list
    tickets = []
    #with open("tickets.json", 'r') as f:   
    #    tickets = json.load(f)

    # get all the tickets from sheets
    tickets = get_ticket_api.get_all_values()


    # print the number of tickets there are
    print("There are " + str(len(tickets)) + " tickets.")
    list_choice = 0

    # go through every item in the list
    for i in tickets:

        # check if each ticket is open or closed
        if tickets[list_choice][3] == "open":
            ticket_status = "(Open)"
        else:
            ticket_status = "(Closed)"

        # print each ticket with its number, brief description, and status
        print(str(int(list_choice) + 1) + ": " + str(tickets[list_choice][0]) + " " + ticket_status)

        # add one to list choice to go through the entire list
        list_choice += 1

    # ask the user which ticket they would like to view
    view_ticket = input("Which ticket would you like to modify: ")

     # add try exception in case of an error
    
    # set the user input to an integer starting at 0 instead of 1
    view_ticket = int(view_ticket)
    view_ticket = view_ticket - 1
        
    clear()

    # print the support ticket information
    print("\nNow viewing ticket " + str(int(view_ticket) + 1) + ".")
    print("\nUser: " + str(tickets[view_ticket][2]))
    print("Subject: " + str(tickets[view_ticket][0]))
    print("Description: " + str(tickets[view_ticket][1]))

    print("How would you like to modify the support ticket?")
    print("1 ------------------------------- Resolve Ticket")
    print("2 -------------------------------- Delete Ticket")
    print("3 -------------------------------- Cancel Action\n")

    # ask for menu selection
    action = str(input(""))

    # RESOLVE TICKET SELECTION
    if action == "1":
        it_admin = ""
        resolution = ""

        # ask for admin name
        it_admin = input("Please enter your username: ")

        # ask for ticket solution/resolution
        resolution = input("Please enter the solution to this ticket: ")

        # push the ticket parts to the correct parts of the database
        get_ticket_api.update('D' + str(int(view_ticket) + 1), 'closed')
        get_ticket_api.update('E' + str(int(view_ticket) + 1), resolution)
        get_ticket_api.update('F' + str(int(view_ticket) + 1), it_admin)

        # print ticket updated
        print("Ticket updated!")
        sleep(3)

    # DELETE TICKET SELECTION
    elif action == "2":

        # clear screen and print confirmation notice
        clear()
        print("-------- C O N F I R M --------")
        print("Are you sure you want to delete \nthe following ticket?")
        print("\nUser: " + str(tickets[view_ticket][2]))
        print("Subject: " + str(tickets[view_ticket][0]))
        print("Description: " + str(tickets[view_ticket][1]))
        print("")

        # ask user to confirm
        confirm = input("y/n: ")
        if confirm.lower() == "y" or confirm.lower() == "yes" or confirm.lower() == "confirm":
            
            # delete the row of the selected ticket in the database
            get_ticket_api.delete_rows(int(view_ticket) + 1) 

            # print success message
            print("Ticket deleted successfully.")
            sleep(3)
        
        # print error message.
        else:
            print("Error: Returning to main menu...")
            sleep(3)

    # return to main menu
    elif action == "3":
        print("Returning to the main menu...")
        sleep(3)


# create the modify users interface
def modify_users():
     
     # clear the terminal screen
    clear()

    # setup the input program
    loop_program = True
    while loop_program == True:
        
        # print the menu
        print("-- MODIFY USER PERMISSIONS --")
        print("-----------------------------")
        print("1 ----------- View Admin List")
        print("2 ------- Add New Admin (WIP)")
        print("3 -------------- Remove Admin")
        print("4 ------- Return to Main Menu")

        # ask for user input
        operator = str(input(""))

        # view admins
        if operator.lower() == "1":

            # create a list of all the admins
            admins = get_permissions_api.get_all_values()
            counter = 0

            # print each admin
            for i in admins:
                print(str(counter + 1) + ": " + admins[counter][0])
                counter = counter + 1

            # on user input, return to menu
            print(input("Press enter to return to menu..."))
            sleep(3)
            modify_users()
            
        # add an admin
        elif operator.lower() == "2":

            print("")

            # ask for new admin name
            new_admin = (str(input("Please enter new admin username: ")))

            # convert input into a list
            temp_list = []
            temp_list.append(new_admin)

            # push the list to the google api database
            get_permissions_api.append_row(temp_list)

            # print success messages
            print("\nNew admin added successfully")
            print("\nReturning to Menu...")
            sleep(3)
            modify_users()

        # remove an admin selection menu
        elif operator.lower() == "3":

            # define list and fill with current admins from database
            admins = []
            admins = get_permissions_api.get_all_values()

            # print title
            print("")
            print("Current Admins:\n")
            counter = 0

            # print list of current admins
            for i in admins:
                print(str(int(counter + 1)) + ": " + admins[counter][0])
                counter = counter + 1

            # create loop for valid input
            while True:
                remove = 0

                # try exception
                try:
                    
                    #ask for user input
                    remove = int(input("\nEnter the number of the admin to remove: "))

                    # if input is greater than number of admins, error message
                    if remove > counter:
                        print("Please enter a valid response.")

                    # if user attempts to remove it_admin, error message
                    elif remove == 1 or remove == "it_admin":
                        print("it_admin cannot be removed.")

                    # if user makes valid request
                    else:

                        # print success message
                        print("Removing admin...\n")

                        # remove admin from database
                        get_permissions_api.delete_rows(remove)
                        break

                # handle any errors with except statement
                except:
                    print("Invalid response.")
                    break

            # return to menu
            sleep(3)
            modify_users()

        # return to main menu
        elif operator.lower() == "4" or operator.lower() == "exit" or operator.lower() == "back" or operator.lower() == "menu":
            print("\nReturning to Main Menu...")
            sleep(3)
            loop_program = False
            break
        
    main_program()


# create the interactive initial interface
def main_program():

    # create program loop
    loop_program = True
    while loop_program == True:

        # print the main program menu
        clear()
        print("--Welcome to Tovin's IT Support Desk!--")
        print("---------------------------------------")
        print("1 ---------------- View Support Tickets")
        print("2 --------- Create a New Support Ticket")
        print("3 ---- Close or Update a Support Ticket")
        print("4 ------------- Modify User Permissions")
        print("5 -------------------- Exit the Program\n")

        # ask for user input
        operator = str(input(""))

        # call view tickets function
        if str(operator.lower()) == "1":
            view_tickets()

        # call add ticket function
        elif str(operator.lower()) == "2":
           add_ticket()

        # call the modify tickets function
        elif str(operator.lower()) == "3":

            # load the admins database into a list
            permissions = get_permissions_api.get_all_values()

            # check if the user is the it_admin or their username is in the admin database
            if userID == "it_admin" or str(userID) in str(permissions):
                modify_tickets()

            # if they are not, print error message
            else:
                print("You do not have permissions to access this menu!")
                print("Please contact your network admin.")
                sleep(3)

        # call the modify users function
        elif str(operator.lower()) == "4":
            
            # load the admins database into a list
            permissions = get_permissions_api.get_all_values()

            # check if user is it_admin or username is in the admin database
            if userID == "it_admin" or str(userID) in str(permissions):
                modify_users()

            # if they are not, print error message
            else:
                print("You do not have permissions to access this menu!")
                print("Please contact your network admin.")
                sleep(3)

        # quit the program
        elif operator.lower() == "stop" or operator.lower() == "exit" or operator.lower() == "quit" or str(operator.lower()) == '5':
            loop_program = False
            exit()
            

        # handle any program exceptions with input
        else:
            print("I'm sorry, there was an error with your input.\n")


# start the program in the auth screen
auth()