# Finance-App

## 📌 Overview

This finance app aims to simplify personal finance management by providing powerful visualisations of spending patterns, and offering a suite of tools for budgeting, saving, and transaction management. Blending complex features with a user-friendly design, the app caters to a wide range of users, empowering those of all financial literacy levels to make strategic financial decisions, build strong habits, and ultimately improve financial wellbeing.

## 🔐 Core Features
- Secure Signup & Login features, with hashing and encryption applied.
- Password reset via email
- Functionality to connect bank accounts via the Plaid API
- Transaction management (filtering, sorting, editing, adding, deleting)
- Budgeting, with automatic tracking
- Setting savings goals
- Spending insights & Analytics
- Alerts for important events

## 🛠️ Tech Stack
- PostgreSQL
- Python
- Django
- Plaid API
- JS

## 🧠 Architecture
- Object-Oriented Programming (OOP)
- Model-View-Controller (MVC) pattern
- Internal REST API

## 🚀 Getting Started
**Prerequisites**:
 - You must install Python 3.8 or higher from - https://www.python.org/downloads/
 - You must install PostgreSQL for your system and ensure that the GUI tool PgAdmin is also downloaded from - https://www.postgresql.org/download/
 - Follow this tutorial for help with setting up postgreSQL - https://www.w3schools.com/postgresql/postgresql_install.php


1) **Obtain the Project Code**
    - The project can be downloaded as a ZIP and extracted into a folder of your choice.
    - Alternatively, the repository can be cloned.
    - It is recommended to open the project in an IDE with a terminal such as VS Code

2) **Virtual Environment Setup**:
    - The project uses a Virtual Environment to isolate dependencies. The following steps can be used to activate one:
    1. Using the Terminal or Command Prompt, navigate to the project directory with:

        `cd [PATH_TO_DIRECTORY]/Finance\ App/Project/`

        **Ensure you're in the same directory as  `'requirements.txt'` before installing dependencies.**


    2. Once in the directory, create the environment with the following command:

     - For Windows - `python -m venv venv`

     - For Linux/Mac - `python3 -m venv venv`

    3. If this is done correctly, you should now see a file called `'venv'` in the project. Now we need to activate it:
    
     - For Windows - `venv\Scripts\activate`

     - For Linux/Mac - `source venv\bin\activate`
    
    - If correct, you should see `'venv'` at the start of the command line, indicating that the environment is activated.

3) **Installing Dependencies**:
    - The project uses the `'requirements.txt'` to house all dependencies. With the virual environment active, install them by running:

        `pip install -r requirements.txt`

    - This should install all of the dependencies needed for the project.

4) **Setting up the PostgreSQL database**:
    1. Make sure that PostgreSQL is installed and running with the command:

        `pg_isready`

     - If all is correct you should see a confirmation message similar to this:

        `/tmp:5432 - accepting connections`

    2. Create a database for the project
     - Open PgAdmin and create a database for the project. This guide may help:

        https://www.w3schools.com/postgresql/postgresql_pgadmin4.php
    
    3. Configure database settings in Django
     - Navigate to the following file:
     
        `Finance App/Project/secrets.env`
     
     - The second line in the file should be similar to this:

        `DATABASE_URL=postgres://[USERNAME]:[PASSWORD]@localhost:5432/[DATABASE_NAME]`

     - To complete the configuration, you will need to replace the sections `[USERNAME]`, `[PASSWORD]` and `[DATABASE_NAME]` with your real details. Be sure to use the same username and password used to sign up to postgreSQL.

5) **Run Database Migration**:
    - Now, we need to apply the project's database migration. Make sure that the virtual environment is active and run the following commands in the terminal:

        `python manage.py makemigrations`

        `python manage.py migrate`
    
     - This should add the required schema to the database, and you can check this in PgAdmin to make sure everything is successful.

6) **Run the Development Server**:
    - start the django server by running this command in the terminal:

        `python manage.py runserver`

    - Now everything is complete, you can access the app by visiting the url: 

        http://127.0.0.1:8000/signup/

7) **App Information**
    - The app uses 2-factor-authentication, where a code is sent to the email address used for registration. Be sure to use a real email you can access, as the verification code will be         sent there.
    - Alternatively, you can use the following site for a temporary email inbox where the verification code will be sent to:

        https://temp-mail.org/en

## 🎥 App Showcase:

### Homepage:
![Homepage Image](Project/assets/Homepage.png)

### Transactions Page:
![Transactions Image](Project/assets/Transactions.png)

### Budgets Page:
![Budgets Image](Project/assets/Budgets.png)

### Savings Page:
![Savings Image](Project/assets/Savings.png)

### Insights Page:
![Insights Image](Project/assets/Insights.png)
