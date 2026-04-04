CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    current_semester INTEGER DEFAULT 1,
    risk_category TEXT DEFAULT 'Safe'
);

CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_code TEXT UNIQUE NOT NULL,
    subject_name TEXT NOT NULL,
    credits INTEGER NOT NULL DEFAULT 3
);

CREATE TABLE IF NOT EXISTS faculty (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS faculty_subjects (
    faculty_id INTEGER,
    subject_id INTEGER,
    FOREIGN KEY(faculty_id) REFERENCES faculty(id) ON DELETE CASCADE,
    FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    PRIMARY KEY(faculty_id, subject_id)
);

CREATE TABLE IF NOT EXISTS marks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    semester INTEGER NOT NULL,
    marks INTEGER NOT NULL,
    grade TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    UNIQUE(student_id, subject_id, semester)
);

CREATE TABLE IF NOT EXISTS cgpa_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    semester INTEGER NOT NULL,
    sgpa REAL NOT NULL,
    cgpa REAL NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE(student_id, semester)
);
