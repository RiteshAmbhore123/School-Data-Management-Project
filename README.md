# 🏥 Hospital Management System

A modern desktop-based hospital record management system built with Java Swing and Oracle Database. This project helps hospital staff efficiently store, update, search, and manage patient information in a clean and user-friendly interface.

<p align="center">
  <img src="https://img.shields.io/badge/Java-17%2B-orange?logo=java&logoColor=white" alt="Java" />
  <img src="https://img.shields.io/badge/Oracle-Database-red?logo=oracle&logoColor=white" alt="Oracle Database" />
  <img src="https://img.shields.io/badge/Swing-GUI-blue?logo=java&logoColor=white" alt="Swing GUI" />
  <img src="https://img.shields.io/badge/Status-Active-success" alt="Status" />
</p>

## ✨ Features

- Add new patients with personal and medical details
- Update existing patient records
- Delete patient entries safely
- Search patients by name or phone number
- View all patient records in a table
- Input validation for age, phone number, and required fields
- Auto table creation for the `patients` table on startup
- Oracle database integration for persistent storage

## 🧩 Tech Stack

- Java Swing (desktop GUI)
- Oracle JDBC (`ojdbc8.jar`)
- Oracle Database XE / local Oracle instance
- Java SE / standard library

## 📁 Project Structure

```text
Hospital-Management-System-main/
├── lib/
│   └── ojdbc8.jar
├── src/
│   ├── HospitalManagementSystem.java
│   ├── Patient.class
│   ├── PatientDAO.class
│   ├── PatientFormPanel.class
│   ├── PatientTablePanel.class
│   └── ...
├── run.bat
├── Final Year Report Template.doc
└── README.md
```

## 🚀 Getting Started

### Prerequisites

Before running the app, make sure you have:

- Java JDK installed
- Oracle Database installed and running locally
- Oracle JDBC driver available in the `lib` folder
- A database user with access to the `system` schema or equivalent

### 1) Clone the repository

```bash
git clone https://github.com/RiteshAmbhore123/Hospital-Management-System-Java.git
cd Hospital-Management-System-Java
```

### 2) Configure database connection

The app connects to Oracle using the settings in `src/HospitalManagementSystem.java`:

```java
private static final String URL = "jdbc:oracle:thin:@localhost:1521:XE";
private static final String USER = "system";
private static final String PASSWORD = "Ritesh";
```

Update these values if your local Oracle database uses different credentials or port.

### 3) Compile and run

On Windows:

```bat
run.bat
```

Or manually:

```bash
javac -cp ".;lib/ojdbc8.jar" src/*.java
java -cp "src;lib/ojdbc8.jar" HospitalManagementSystem
```

## 🏗️ Database Behavior

On startup, the application checks whether a `patients` table exists. If it doesn't, it creates one automatically with fields such as:

- `id`
- `name`
- `age`
- `gender`
- `phone`
- `address`
- `blood_group`

## 🩺 Use Case

This system is designed for small to medium healthcare environments that need a simple desktop solution for managing patients without a heavy web framework. It is suitable for demos, academic projects, and hospital record tracking applications.

## 📌 Notes

- The project is primarily a Java Swing desktop application.
- It is not a full hospital ERP system; it focuses on patient registration and record management.
- If you are using a different Oracle instance, update the JDBC credentials in the database configuration section.

## 🤝 Contributing

Contributions are welcome! If you want to improve this project:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a pull request

## 📜 License

This project is for educational and demonstration purposes. Please check the repository license if one is added later.

## 👨‍💻 Author

Ritesh Ambhore

---

If you want, I can also make this README even more premium by adding:
- a project logo section
- screenshot placeholders
- architecture diagram
- a better "Why this project matters" section
- a dark-mode styled GitHub README version
