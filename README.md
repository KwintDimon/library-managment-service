# Library Service Project

## Overview
The Library Service Project is a Django-based application designed to manage the borrowing of books by users. It consists of several key components, including services for managing books, users, and borrowings.

## Resources

### Book
- **Title**: `str`  
- **Author**: `str`  
- **Cover**: `Enum`: HARD | SOFT  
- **Inventory***: positive `int`  
- **Daily fee**: `decimal` (in $USD)  

> *Inventory - the number of this specific book available in the library

### User (Customer)
- **Email**: `str`  
- **First name**: `str`  
- **Last name**: `str`  
- **Password**: `str`  
- **Is staff**: `bool`  

### Borrowing
- **Borrow date**: `date`  
- **Expected return date**: `date`  
- **Actual return date**: `date`  
- **Book id**: `int`  
- **User id**: `int`  

## Components

### Borrowings Service
Manages users' borrowings of books.

#### API Endpoints
- **POST**: `/borrowings/`  
  - Add a new borrowing (when a book is borrowed, `inventory` is decremented by 1).
- **GET**: `/borrowings/?user_id=...&is_active=...`  
  - Get borrowings by user ID and whether the borrowing is still active or not.
- **GET**: `/borrowings/<id>/`  
  - Get specific borrowing details.
- **POST**: `/borrowings/<id>/return/`  
  - Set the actual return date (inventory is incremented by 1).

## Tasks

### 1. Implement CRUD Functionality for Books Service
- **Initialize books app**  
- **Add book model**  
- **Implement serializer & views for all endpoints**  
- **Add permissions to Books Service**  
  - Only admin users can create/update/delete books.
  - All users (including unauthenticated) can list books.
- **Use JWT token authentication** from users' service.

### 2. Implement CRUD for Users Service
- **Initialize users app**  
- **Add user model with email**  
- **Add JWT support**  

### 3. Implement Borrowing List & Detail Endpoint
- **Initialize borrowings app**  
- **Add borrowing model** with constraints for `borrow_date`, `expected_return_date`, and `actual_return_date`.
- **Implement read serializer** with detailed book info.
- **Implement list & detail endpoints**  

### 4. Implement Create Borrowing Endpoint
- **Implement create serializer**  
  - Validate that book inventory is not 0.
  - Decrease inventory by 1 for the book.
  - Attach the current user to the borrowing.
- **Implement create endpoint**

### 5. Add Filtering for the Borrowings List Endpoint
- Ensure all non-admins can see only their borrowings.
- Ensure borrowings are available only for authenticated users.
- Add the `is_active` parameter for filtering by active borrowings (not yet returned).
- Add the `user_id` parameter for admin users, allowing them to see all users’ borrowings, or for a specific user if specified.

### 6. Implement Return Borrowing Functionality
- Ensure you cannot return a borrowing twice.
- Increase the book's inventory by 1 upon returning.
- Implement an endpoint for returning a borrowing.
