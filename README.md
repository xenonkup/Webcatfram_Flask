## Table of Contents
- [Introduction](#introduction)
- [Technologies Used](#technologies-used)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Database Setup](#database-setup)


  ## Introduction
**Breeding Cat Booking** is a web application designed for cat breeders to manage breeding schedules, bookings, and customer inquiries. This application simplifies the process 
  of tracking available cats for breeding, managing bookings, and ensuring a smooth interaction between breeders and customers. The application is built using Flask as the
  backend framework and utilizes MySQL for data storage.

## Technologies Used
- **Backend:** Flask (Python)
- **Frontend:** HTML5, CSS3
- **Database:** MySQL
- **Other Libraries:**
  - Flask-MySQLdb
  - Jinja2 (for templating)
  - Flask-WTF (for form handling)
  - Bootstrap (for responsive design)

## Features
- **User Authentication:** Secure login and registration for breeders and customers.
- **Breeding Schedule Management:** Add, update, and delete breeding schedules for available cats.
- **Booking System:** Customers can view available cats and make bookings.
- **Customer Inquiries:** Manage and respond to customer inquiries regarding breeding services.

## Installation

### Prerequisites
Before running this project, ensure you have the following installed:
- Python
- MySQL
- Flask and necessary Python libraries (can be installed via `requirements.txt`)

### Steps

1. Clone this repository:
   ```bash
   git clone https://github.com/username/breeding-cat-booking.git

2. Navigate to the project directory:
   ```bash
   cd breeding-cat-booking

3. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv

4. Activate the virtual environment:
   ```bash
   For Windows : venv\Scripts\activate
   For macOS/Linux : source venv/bin/activate

5. Install the required dependencies:
   ```bash
   pip install -r requirements.txt

6. Configure MySQL database (see Database Setup).

7.Run the Flask application:
 ```bash
 flask run
 Access the application in your browser at http://127.0.0.1:5000.













  
   
