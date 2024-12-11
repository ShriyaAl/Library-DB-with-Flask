This is a simple Library Management System built using Flask with user authentication, book borrowing/returning functionalities, and admin management. The system supports user and admin roles, with features like browsing books, borrowing/returning books, managing users, and tracking transactions.

Features
* User Authentication: Users can register, log in, and manage their account.
* Admin Authentication: Admins can log in and manage users, books, and transactions.
* Book Catalog: Users can view the available books and borrow/return them.
* Transaction Tracking: Track borrow and return dates for each book.
* Role-Based Access: Differentiates between users and admins, with specific functionalities for each role.
* Password Hashing: Uses Flask-Bcrypt for secure password storage and authentication.

  
Technologies Used


* Flask: A lightweight WSGI web application framework.
* Flask-SQLAlchemy: ORM for interacting with a MySQL database.
* Flask-Login: For handling user sessions and authentication.
* Flask-WTF: For form handling and validation.
* MySQL: For database storage.
* Flask-Bcrypt: For password hashing and checking.

  
Prerequisites


Before setting up the project, ensure you have the following:

* Python 3.x or later
* MySQL or MariaDB server running locally (or adjust the configuration for your environment)
* Pip installed for managing dependencies


