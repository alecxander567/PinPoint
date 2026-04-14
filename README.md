# 🔍 QR-Based Item Finder

A web-based application that helps users recover lost items using QR codes. When someone finds a lost item, they can scan the QR code and instantly share its location with the owner.

---

## 🌐 Live Demo

🔗 [https://pin-point-client-ten.vercel.app/](https://pin-point-client-ten.vercel.app/)

---

## 🚀 Features

### 👤 Owner Side

* User authentication (Sign up / Login)
* Add and manage items
* Upload item images (stored via Cloudinary)
* Generate unique QR code per item
* Receive location updates when item is found

### 📍 Finder Side

* Scan QR code
* View item details
* Share current location to the owner
* Contact owner via messenger/Facebook

---

## 🛠️ Tech Stack

### Frontend

* React.js
* JavaScript
* Tailwind CSS

### Backend

* Python
* Django (Django REST Framework)
* Supabase (Database)

### Storage

* Cloudinary (Image storage)

### Deployment

* Backend: Render (Free Tier)
* Frontend: Vercel



## 🔄 How It Works

1. Owner registers and logs in
2. Owner adds an item and generates a QR code
3. QR code is attached to the item
4. If lost, finder scans the QR code
5. Finder shares location
6. Owner receives notification and retrieves the item

---

## 📄 License

This project is MIT License.

---

## 💡 Author

Developed by an aspiring Software Engineer 🚀

