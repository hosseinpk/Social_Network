# 🌐 Social Network API

A modern **Social Network REST API** built with **Django REST Framework**, featuring JWT + OTP authentication, user profiles, posts, comments, follow requests, and async email notifications.  
The project is fully containerized using **Docker**, served via **Gunicorn + Nginx**, and uses **PostgreSQL**, **Redis**, and **RabbitMQ** for backend services.

---

![Demo](./ezgif-16cd5b19917ef6.gif)

---

## 🚀 Features

### 🔐 Authentication
- Register new users and verify via email
- Login with **OTP** and **JWT tokens**
- Password reset via email
- Logout with token blacklist
- Account verification and resend verification email

### 👤 User Profiles
- View and edit user profiles
- Follow / unfollow other users
- Handle private profile follow requests (accept/reject/delete)
- View follower and following counts

### 📝 Posts & Interactions
- Create, update, and delete posts
- Like and comment on posts
- Manage posts with multiple statuses (Draft / Published / Deleted)

### 📬 Emails & Notifications
- Email templates for:
  - Account activation
  - Password reset
  - Follow request notifications  
- Asynchronous email sending via **Celery + RabbitMQ**

### ⚙️ System Architecture
- **Django REST Framework** for API logic  
- **PostgreSQL** as the main database  
- **Redis** for caching and Celery broker  
- **RabbitMQ** for async tasks  
- **Gunicorn + Nginx** for production serving  
- **Docker Compose** for multi-container orchestration  

---

## 📦 Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/hosseinpk/Social_Network.git
cd Social_Network
