# 🕒 Attendance Tool - Track, Manage & Optimize!

## 🚀 What is This?
The **Attendance Tool** is your ultimate go-to web app for managing employee attendance like a pro! Built with **Python Flask**, **HTML**, **CSS**, **JavaScript**, **Bootstrap**, and **MySQL**, this tool seamlessly connects with **ZK Machines**, grabs attendance records, and processes them to calculate **working hours, overtime, and late penalties** – so you don’t have to!

## 🔥 Key Features
✅ **Real-time Attendance Sync** – Connects with **ZK Machines** to pull attendance records instantly.  
✅ **Smart Data Storage** – Saves all attendance data securely in a MySQL database.  
✅ **Automated Calculations** – Computes daily working hours, overtime, and late penalties effortlessly.  
✅ **Excel Import & Export** – Import employee details from **MS Excel** and export attendance reports with just a click!  
✅ **Easy-to-Use Interface** – Built with Bootstrap for a sleek and responsive design.  

## 🛠 Tech Stack
🔹 **Backend:** Python (Flask)  
🔹 **Frontend:** HTML, CSS, JavaScript, Bootstrap  
🔹 **Database:** MySQL  
🔹 **Hardware Integration:** ZK Attendance Machines  

---

## 🚀 Get Started in Minutes!
### 🛑 Prerequisites
Make sure you have the following installed:
- **Python (>=3.7)**
- **MySQL Server**

### 🛠 Installation Steps
1️⃣ Clone the repo:
   ```sh
   git clone https://github.com/your-repo/attendance-tool.git
   cd attendance-tool
   ```
2️⃣ Set up a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3️⃣ Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4️⃣ Set up the database:
   - Create a MySQL database (e.g., `attendance_db`).
   - Import the schema:
     ```sh
     mysql -u root -p attendance_db < database/schema.sql
     ```
5️⃣ Configure your `.env` file:
   - Rename `.env.example` to `.env` and update database credentials.
6️⃣ Fire it up! 🚀
   ```sh
   flask run
   ```
   Now, head over to **`http://127.0.0.1:5000/`** and start managing attendance like a boss!

---

## 🎯 How It Works
1️⃣ **Sync Data** – Connect and fetch attendance from ZK Machine.  
2️⃣ **Manage Attendance** – View, edit, and store records in the database.  
3️⃣ **Automate Calculations** – Let the system do the heavy lifting (working hours, overtime, penalties).  
4️⃣ **Import Employees** – Upload an MS Excel file to quickly add employees.  
5️⃣ **Export Reports** – Download raw or processed attendance data in Excel format.  

---

## 📡 API Endpoints
| Method | Endpoint | Description |
|--------|----------|--------------|
| GET | `/get_attendance_data` | Fetch all attendance records |
| POST | `/api/import_employees` | Upload an Excel file to import employees |
| GET | `/api/export_attendance` | Download attendance reports as an Excel file |

---

## 🌟 What’s Next?
🔜 **User Authentication & Roles** – Secure login and different user levels.  
🔜 **Dashboard & Analytics** – Interactive charts and insights.  
🔜 **Email Notifications** – Auto-email attendance summaries to managers.  

---

## 📜 License
Licensed under the **MIT License** – feel free to tweak and improve!  

## 🤝 Contribute
Want to make it even better? Fork the repo, submit a PR, or drop me a message!

## 📬 Need Help?
Drop an email at [ahmed.h.morgan2050@gmail.com](mailto:ahmed.h.morgan2050@gmail.com) – let's chat!

