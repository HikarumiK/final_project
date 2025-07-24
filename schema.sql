-- テーブルが存在する場合、依存関係も含めて削除
DROP TABLE IF EXISTS Clinic_Treatments, Concern_Procedure_Links, Doctors, Institutions, Clinics, Concerns, Procedures CASCADE;

-- SERIAL PRIMARY KEY は、MySQLの INT AUTO_INCREMENT PRIMARY KEY と同じ役割
CREATE TABLE Clinics (
    clinic_id SERIAL PRIMARY KEY,
    clinic_name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Institutions (
    institution_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Doctors (
    doctor_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    is_specialist BOOLEAN NOT NULL DEFAULT FALSE,
    institution_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (institution_id) REFERENCES Institutions(institution_id)
);

CREATE TABLE Concerns (
    concern_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Procedures (
    procedure_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    demerits TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Concern_Procedure_Links (
    link_id SERIAL PRIMARY KEY,
    concern_id INT NOT NULL,
    procedure_id INT NOT NULL,
    FOREIGN KEY (concern_id) REFERENCES Concerns(concern_id),
    FOREIGN KEY (procedure_id) REFERENCES Procedures(procedure_id),
    UNIQUE(concern_id, procedure_id)
);

CREATE TABLE Clinic_Treatments (
    treatment_id SERIAL PRIMARY KEY,
    clinic_id INT NOT NULL,
    procedure_id INT NOT NULL,
    price INT,
    price_details TEXT,
    equipment_or_material VARCHAR(255),
    our_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (clinic_id) REFERENCES Clinics(clinic_id),
    FOREIGN KEY (procedure_id) REFERENCES Procedures(procedure_id)
);