# Finance-App

This finance app aims to simplify personal finance management by providing powerful visualisations of spending patterns, and offering a suite of tools for budgeting, saving, and transaction management. Blending complex features with a user-friendly design, the app caters to a wide range of users, empowering those of all financial literacy levels to make strategic financial decisions, build strong habits, and ultimately improve financial wellbeing.

## Core Features:
- Secure Signup & Login features, with hashing and encryption applied.
- Password reset via email
- Functionality to connect bank accounts via the Plaid API
- Transaction management (filtering, sorting, editing, adding, deleting)
- Budgeting, with automatic tracking
- Setting savings goals
- Spending insights & Analytics

## Technologies:
- PostgreSQL
- Python
- Django
- Plaid API
- JS

## App Architecture:
The app leverage OOP, which allows for modular code development and separation of concerns. This was combined with the model-view-controller (MVC) achitecture, which created logical tiers withing the application for different duties to be handled. FInally, the app utilises an internal REST API, which links the front and backend in a seamless and secure manner. By using a combination of these design patterns, the app can leverage the benefits of each, whilst mitigating their downsides. Particularly, a finance app must prioritise security above all, which this app does, however i have also tried to maximise scalability, efficiency and usability.
