-- schema.sql (最終版)

-- 既存のテーブルを一旦削除（実行順を考慮）
DROP TABLE IF EXISTS Clinic_Treatments;
DROP TABLE IF EXISTS Concern_Procedure_Links;
DROP TABLE IF EXISTS Doctors;
DROP TABLE IF EXISTS Institutions;
DROP TABLE IF EXISTS Clinics;
DROP TABLE IF EXISTS Concerns;
DROP TABLE IF EXISTS Procedures;

-- クリニック情報
CREATE TABLE Clinics (
    clinic_id INT AUTO_INCREMENT PRIMARY KEY,
    clinic_name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 所属機関テーブル
CREATE TABLE Institutions (
    institution_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 医師情報テーブル
CREATE TABLE Doctors (
    doctor_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    is_specialist BOOLEAN NOT NULL DEFAULT FALSE,
    institution_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (institution_id) REFERENCES Institutions(institution_id)
);

-- お悩みカテゴリテーブル
CREATE TABLE Concerns (
    concern_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 施術マスタテーブル
CREATE TABLE Procedures (
    procedure_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    demerits TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- お悩みと施術の関連付けテーブル
CREATE TABLE Concern_Procedure_Links (
    link_id INT AUTO_INCREMENT PRIMARY KEY,
    concern_id INT NOT NULL,
    procedure_id INT NOT NULL,
    FOREIGN KEY (concern_id) REFERENCES Concerns(concern_id),
    FOREIGN KEY (procedure_id) REFERENCES Procedures(procedure_id),
    UNIQUE(concern_id, procedure_id)
);

-- クリニックの取扱施術テーブル
CREATE TABLE Clinic_Treatments (
    treatment_id INT AUTO_INCREMENT PRIMARY KEY,
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
