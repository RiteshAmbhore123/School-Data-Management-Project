CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no TEXT NOT NULL,
    name TEXT NOT NULL,
    class_name INTEGER NOT NULL,
    section TEXT DEFAULT 'A',
    gender TEXT DEFAULT 'Male',
    dob TEXT,
    parent_name TEXT,
    contact TEXT NOT NULL,
    address TEXT,
    admission_date TEXT,
    blood_group TEXT,
    UNIQUE(class_name, roll_no)
);

CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    class_name INTEGER NOT NULL,
    date TEXT NOT NULL,
    status TEXT NOT NULL,
    UNIQUE(student_id, date),
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
);
