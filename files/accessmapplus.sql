-- ============================================================================
-- AccessMap+ Database - Complete Dump File
-- ============================================================================

DROP DATABASE IF EXISTS AccessMapPlus;
CREATE DATABASE AccessMapPlus;
USE AccessMapPlus;

-- ============================================================================
-- TABLE DEFINITIONS
-- ============================================================================

CREATE TABLE User (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    country VARCHAR(50),
    state VARCHAR(50),
    city VARCHAR(50),
    street VARCHAR(100),
    zip_code VARCHAR(10),
    disability_type VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Authority (
    authority_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Place (
    place_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(50) NOT NULL,
    state VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL,
    street VARCHAR(100),
    zip_code VARCHAR(10),
    category VARCHAR(50) NOT NULL,
    latitude DECIMAL(9,6) CHECK(latitude BETWEEN -90 AND 90),
    longitude DECIMAL(9,6) CHECK(longitude BETWEEN -180 AND 180),
    verified BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE Accessibility_Feature (
    feature_id INT PRIMARY KEY AUTO_INCREMENT,
    feature_type VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(500)
);

CREATE TABLE Feature_Instance (
    instance_id INT PRIMARY KEY AUTO_INCREMENT,
    place_id INT NOT NULL,
    feature_id INT NOT NULL,
    status ENUM('Working','Broken','Unavailable') NOT NULL DEFAULT 'Working',
    last_checked DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(place_id) REFERENCES Place(place_id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY(feature_id) REFERENCES Accessibility_Feature(feature_id) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    UNIQUE(place_id, feature_id)
);

CREATE TABLE Review (
    review_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    place_id INT NOT NULL,
    rating INT NOT NULL CHECK(rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, place_id, created_at),
    FOREIGN KEY(user_id) REFERENCES User(user_id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY(place_id) REFERENCES Place(place_id) 
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Review_Media (
    media_id INT PRIMARY KEY AUTO_INCREMENT,
    review_id INT NOT NULL,
    url VARCHAR(255) NOT NULL,
    media_type ENUM('image','video') NOT NULL,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(review_id) REFERENCES Review(review_id) 
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Issue_Report (
    report_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    place_id INT NOT NULL,
    issue_type VARCHAR(100) NOT NULL,
    severity ENUM('Low','Medium','High') NOT NULL,
    status ENUM('Open','In Progress','Resolved','Closed') NOT NULL DEFAULT 'Open',
    description TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME NULL,
    UNIQUE(user_id, place_id, created_at),
    CHECK(resolved_at IS NULL OR resolved_at >= created_at),
    FOREIGN KEY(user_id) REFERENCES User(user_id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY(place_id) REFERENCES Place(place_id) 
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Issue_Media (
    media_id INT PRIMARY KEY AUTO_INCREMENT,
    report_id INT NOT NULL,
    url VARCHAR(255) NOT NULL,
    media_type ENUM('image','video') NOT NULL,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(report_id) REFERENCES Issue_Report(report_id) 
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Maintenance_Responsibility (
    responsibility_id INT PRIMARY KEY AUTO_INCREMENT,
    authority_id INT NOT NULL,
    place_id INT NOT NULL,
    instance_id INT NOT NULL,
    role ENUM('Maintenance','Inspection','Cleaning') NOT NULL,
    since_date DATE NOT NULL,
    UNIQUE(authority_id, place_id, instance_id),
    FOREIGN KEY(authority_id) REFERENCES Authority(authority_id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY(place_id) REFERENCES Place(place_id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY(instance_id) REFERENCES Feature_Instance(instance_id) 
        ON DELETE CASCADE ON UPDATE CASCADE
);


-- ============================================================================
-- INDEXES
-- ============================================================================

CREATE INDEX idx_place_city_category ON Place(city, category);
CREATE INDEX idx_place_verified ON Place(verified);
CREATE INDEX idx_place_location ON Place(latitude, longitude);
CREATE INDEX idx_review_place ON Review(place_id);
CREATE INDEX idx_review_user ON Review(user_id);
CREATE INDEX idx_review_created ON Review(created_at);
CREATE INDEX idx_issue_place_status ON Issue_Report(place_id, status);
CREATE INDEX idx_issue_user ON Issue_Report(user_id);
CREATE INDEX idx_issue_severity ON Issue_Report(severity);
CREATE INDEX idx_issue_created ON Issue_Report(created_at);
CREATE INDEX idx_feature_instance_place ON Feature_Instance(place_id);
CREATE INDEX idx_feature_instance_status ON Feature_Instance(status);
CREATE INDEX idx_feature_instance_feature ON Feature_Instance(feature_id);
CREATE INDEX idx_maintenance_authority ON Maintenance_Responsibility(authority_id);
CREATE INDEX idx_maintenance_place ON Maintenance_Responsibility(place_id);
CREATE INDEX idx_maintenance_instance ON Maintenance_Responsibility(instance_id);
CREATE INDEX idx_review_media_review ON Review_Media(review_id);
CREATE INDEX idx_issue_media_report ON Issue_Media(report_id);
CREATE INDEX idx_user_email ON User(email);
CREATE INDEX idx_authority_email ON Authority(email);

-- ============================================================================
-- STORED PROCEDURES WITH ERROR HANDLING
-- ============================================================================

DELIMITER $$

CREATE PROCEDURE proc_create_issue(
    IN p_user_id INT,
    IN p_place_id INT,
    IN p_issue_type VARCHAR(100),
    IN p_severity ENUM('Low','Medium','High'),
    IN p_description TEXT,
    OUT p_report_id INT,
    OUT p_status VARCHAR(100)
)
BEGIN
    DECLARE user_exists INT;
    DECLARE place_exists INT;
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        SET p_status = 'ERROR: Failed to create issue report';
        SET p_report_id = -1;
        ROLLBACK;
    END;
    
    START TRANSACTION;
    
    SELECT COUNT(*) INTO user_exists FROM User WHERE user_id = p_user_id;
    SELECT COUNT(*) INTO place_exists FROM Place WHERE place_id = p_place_id;

    IF user_exists = 0 THEN
        SET p_status = 'ERROR: User does not exist';
        SET p_report_id = -1;
        ROLLBACK;
    ELSEIF place_exists = 0 THEN
        SET p_status = 'ERROR: Place does not exist';
        SET p_report_id = -1;
        ROLLBACK;
    ELSE
        INSERT INTO Issue_Report (user_id, place_id, issue_type, severity, description)
        VALUES (p_user_id, p_place_id, p_issue_type, p_severity, p_description);
        
        SET p_report_id = LAST_INSERT_ID();
        SET p_status = 'SUCCESS: Issue report created';
        COMMIT;
    END IF;
END$$

CREATE PROCEDURE proc_assign_responsibility(
    IN p_authority_id INT,
    IN p_instance_id INT,
    IN p_role ENUM('Maintenance','Inspection','Cleaning'),
    IN p_since_date DATE,
    OUT p_status VARCHAR(100)
)
BEGIN
    DECLARE v_place_id INT;
    DECLARE authority_exists INT;
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        SET p_status = 'ERROR: Failed to assign responsibility';
        ROLLBACK;
    END;
    
    START TRANSACTION;
    
    SELECT COUNT(*) INTO authority_exists FROM Authority WHERE authority_id = p_authority_id;
    IF authority_exists = 0 THEN
        SET p_status = 'ERROR: Authority does not exist';
        ROLLBACK;
    ELSE
        SELECT place_id INTO v_place_id 
        FROM Feature_Instance 
        WHERE instance_id = p_instance_id;

        IF v_place_id IS NULL THEN
            SET p_status = 'ERROR: Feature instance does not exist';
            ROLLBACK;
        ELSE
            INSERT INTO Maintenance_Responsibility (authority_id, place_id, instance_id, role, since_date)
            VALUES (p_authority_id, v_place_id, p_instance_id, p_role, p_since_date)
            ON DUPLICATE KEY UPDATE role = p_role, since_date = p_since_date;
            
            SET p_status = 'SUCCESS: Responsibility assigned';
            COMMIT;
        END IF;
    END IF;
END$$

CREATE PROCEDURE proc_add_review(
    IN p_user_id INT,
    IN p_place_id INT,
    IN p_rating INT,
    IN p_comment TEXT,
    OUT p_review_id INT,
    OUT p_status VARCHAR(100)
)
BEGIN
    DECLARE user_exists INT;
    DECLARE place_exists INT;
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        SET p_status = 'ERROR: Failed to add review';
        SET p_review_id = -1;
        ROLLBACK;
    END;
    
    START TRANSACTION;
    
    IF p_rating < 1 OR p_rating > 5 THEN
        SET p_status = 'ERROR: Rating must be between 1 and 5';
        SET p_review_id = -1;
        ROLLBACK;
    ELSE
        SELECT COUNT(*) INTO user_exists FROM User WHERE user_id = p_user_id;
        SELECT COUNT(*) INTO place_exists FROM Place WHERE place_id = p_place_id;

        IF user_exists = 0 THEN
            SET p_status = 'ERROR: User does not exist';
            SET p_review_id = -1;
            ROLLBACK;
        ELSEIF place_exists = 0 THEN
            SET p_status = 'ERROR: Place does not exist';
            SET p_review_id = -1;
            ROLLBACK;
        ELSE
            INSERT INTO Review (user_id, place_id, rating, comment)
            VALUES (p_user_id, p_place_id, p_rating, p_comment)
            ON DUPLICATE KEY UPDATE 
                rating = p_rating, 
                comment = p_comment,
                created_at = NOW();
            
            SET p_review_id = LAST_INSERT_ID();
            SET p_status = 'SUCCESS: Review added';
            COMMIT;
        END IF;
    END IF;
END$$

CREATE PROCEDURE proc_resolve_issue(
    IN p_report_id INT,
    IN p_authority_id INT,
    OUT p_status VARCHAR(100)
)
BEGIN
    DECLARE report_exists INT;
    DECLARE authority_exists INT;
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        SET p_status = 'ERROR: Failed to resolve issue';
        ROLLBACK;
    END;
    
    START TRANSACTION;
    
    SELECT COUNT(*) INTO report_exists FROM Issue_Report WHERE report_id = p_report_id;
    SELECT COUNT(*) INTO authority_exists FROM Authority WHERE authority_id = p_authority_id;

    IF report_exists = 0 THEN
        SET p_status = 'ERROR: Issue report does not exist';
        ROLLBACK;
    ELSEIF authority_exists = 0 THEN
        SET p_status = 'ERROR: Authority does not exist';
        ROLLBACK;
    ELSE
        UPDATE Issue_Report
        SET status = 'Resolved',
            resolved_at = NOW()
        WHERE report_id = p_report_id;
        
        SET p_status = 'SUCCESS: Issue resolved';
        COMMIT;
    END IF;
END$$

CREATE PROCEDURE proc_update_feature_status(
    IN p_instance_id INT,
    IN p_status ENUM('Working','Broken','Unavailable'),
    OUT p_result VARCHAR(100)
)
BEGIN
    DECLARE instance_exists INT;
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        SET p_result = 'ERROR: Failed to update feature status';
        ROLLBACK;
    END;
    
    START TRANSACTION;
    
    SELECT COUNT(*) INTO instance_exists FROM Feature_Instance WHERE instance_id = p_instance_id;

    IF instance_exists = 0 THEN
        SET p_result = 'ERROR: Feature instance does not exist';
        ROLLBACK;
    ELSE
        UPDATE Feature_Instance
        SET status = p_status,
            last_checked = NOW()
        WHERE instance_id = p_instance_id;
        
        SET p_result = 'SUCCESS: Feature status updated';
        COMMIT;
    END IF;
END$$

DELIMITER ;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

DELIMITER $$

CREATE FUNCTION get_average_rating(p_place_id INT)
RETURNS DECIMAL(3,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE avg_rating DECIMAL(3,2);
    SELECT COALESCE(AVG(rating), 0.0) INTO avg_rating
    FROM Review
    WHERE place_id = p_place_id;
    RETURN avg_rating;
END$$

CREATE FUNCTION get_open_issue_count(p_place_id INT)
RETURNS INT
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE issue_count INT;
    SELECT COUNT(*) INTO issue_count
    FROM Issue_Report
    WHERE place_id = p_place_id
      AND status IN ('Open', 'In Progress');
    RETURN issue_count;
END$$

CREATE FUNCTION count_working_features(p_place_id INT)
RETURNS INT
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE feature_count INT;
    SELECT COUNT(*) INTO feature_count
    FROM Feature_Instance
    WHERE place_id = p_place_id AND status = 'Working';
    RETURN feature_count;
END$$

DELIMITER ;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

DELIMITER $$

CREATE TRIGGER trg_before_insert_review
BEFORE INSERT ON Review
FOR EACH ROW
BEGIN
    IF NEW.rating < 1 OR NEW.rating > 5 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Rating must be between 1 and 5';
    END IF;
END$$

CREATE TRIGGER trg_before_update_issue_report
BEFORE UPDATE ON Issue_Report
FOR EACH ROW
BEGIN
    IF NEW.status = 'Resolved' AND OLD.status != 'Resolved' AND NEW.resolved_at IS NULL THEN
        SET NEW.resolved_at = NOW();
    END IF;
END$$

CREATE TRIGGER trg_after_update_feature_instance
AFTER UPDATE ON Feature_Instance
FOR EACH ROW
BEGIN
    IF NEW.status != OLD.status THEN
        UPDATE Place
        SET updated_at = NOW()
        WHERE place_id = NEW.place_id;
    END IF;
END$$

DELIMITER ;

-- ============================================================================
-- EVENTS
-- ============================================================================

SET GLOBAL event_scheduler = ON;

DELIMITER $$

CREATE EVENT ev_auto_close_old_resolved_issues
ON SCHEDULE EVERY 1 DAY
DO
BEGIN
    UPDATE Issue_Report
    SET status = 'Closed'
    WHERE status = 'Resolved'
      AND resolved_at < DATE_SUB(NOW(), INTERVAL 30 DAY);
END$$

CREATE EVENT ev_maintenance_reminder
ON SCHEDULE EVERY 1 WEEK
DO
BEGIN
    UPDATE Feature_Instance
    SET last_checked = NOW()
    WHERE last_checked < DATE_SUB(NOW(), INTERVAL 90 DAY)
      AND status = 'Working';
END$$

DELIMITER ;

-- ============================================================================
-- SAMPLE DATA
-- ============================================================================

INSERT INTO User (first_name, last_name, email, password_hash, country, state, city, street, zip_code, disability_type)
VALUES
('Alice', 'Smith', 'alice.smith@example.com', 'hash1', 'USA', 'California', 'Los Angeles', '123 Elm St', '90001', 'Mobility'),
('Bob', 'Johnson', 'bob.johnson@example.com', 'hash2', 'USA', 'New York', 'New York', '456 Oak St', '10001', 'Visual'),
('Charlie', 'Brown', 'charlie.brown@example.com', 'hash3', 'Canada', 'Ontario', 'Toronto', '789 Pine St', 'M4B1B3', 'Hearing'),
('Diana', 'Prince', 'diana.prince@example.com', 'hash4', 'USA', 'California', 'San Francisco', '321 Market St', '94102', 'Hearing'),
('Eve', 'Davis', 'eve.davis@example.com', 'hash5', 'USA', 'Texas', 'Austin', '654 Congress Ave', '78701', 'Mobility');

INSERT INTO Authority (first_name, last_name, email, phone, password_hash)
VALUES
('John', 'Doe', 'john.doe@example.com', '123-456-7890', 'hash_auth1'),
('Jane', 'Smith', 'jane.smith@example.com', '987-654-3210', 'hash_auth2'),
('Mike', 'Wilson', 'mike.wilson@example.com', '555-123-4567', 'hash_auth3');

INSERT INTO Place (name, country, state, city, street, zip_code, category, latitude, longitude, verified)
VALUES
('Central Park', 'USA', 'New York', 'New York', '5th Ave', '10022', 'Park', 40.785091, -73.968285, TRUE),
('City Mall', 'USA', 'California', 'Los Angeles', 'Sunset Blvd', '90028', 'Shopping', 34.052235, -118.243683, TRUE),
('Union Station', 'Canada', 'Ontario', 'Toronto', 'Front St', 'M5J1E6', 'Transport', 43.645233, -79.380296, FALSE),
('Golden Gate Park', 'USA', 'California', 'San Francisco', 'John F Kennedy Dr', '94122', 'Park', 37.769421, -122.486214, TRUE),
('Memorial Hospital', 'USA', 'Texas', 'Austin', 'Red River St', '78701', 'Hospital', 30.267153, -97.743061, TRUE),
('Downtown Library', 'USA', 'New York', 'New York', 'Madison Ave', '10016', 'Library', 40.752726, -73.981772, FALSE);

INSERT INTO Accessibility_Feature (feature_type, description)
VALUES
('Ramp', 'Wheelchair accessible ramp'),
('Elevator', 'Elevator for multi-floor access'),
('Braille Signage', 'Braille signage for visually impaired'),
('Accessible Restroom', 'Restroom designed for accessibility'),
('Accessible Parking', 'Designated accessible parking spaces'),
('Automatic Doors', 'Doors that open automatically');

INSERT INTO Feature_Instance (place_id, feature_id, status)
VALUES
(1, 1, 'Working'), (1, 2, 'Broken'), (1, 4, 'Working'),
(2, 3, 'Unavailable'), (2, 5, 'Working'),
(3, 4, 'Working'),
(4, 1, 'Working'),
(5, 2, 'Working'), (5, 4, 'Working'),
(6, 2, 'Broken');

INSERT INTO Review (user_id, place_id, rating, comment)
VALUES
(1, 1, 5, 'Great accessibility features!'),
(2, 2, 3, 'Needs improvement on signage.'),
(3, 3, 4, 'Good overall, but elevator was slow.'),
(1, 2, 4, 'Better accessibility than expected.'),
(4, 4, 5, 'Perfect for wheelchair users!');

INSERT INTO Issue_Report (user_id, place_id, issue_type, severity, description)
VALUES
(1, 1, 'Broken Elevator', 'High', 'Elevator at entrance B is not working.'),
(2, 2, 'No Braille Signage', 'Medium', 'Braille signage is missing in the food court.'),
(3, 3, 'Ramp Too Steep', 'Low', 'Ramp near platform 3 is steeper than standards.'),
(4, 6, 'Broken Elevator', 'High', 'Main elevator not functioning.');

INSERT INTO Issue_Media (report_id, url, media_type)
VALUES
(1, 'http://example.com/elevator.jpg', 'image'),
(2, 'http://example.com/braille.jpg', 'image'),
(4, 'http://example.com/library_elevator.jpg', 'image');

INSERT INTO Maintenance_Responsibility (authority_id, place_id, instance_id, role, since_date)
VALUES
(1, 1, 1, 'Maintenance', '2023-01-01'),
(1, 1, 2, 'Maintenance', '2023-01-01'),
(2, 2, 4, 'Inspection', '2023-02-01'),
(3, 3, 6, 'Cleaning', '2023-03-01'),
(1, 4, 7, 'Maintenance', '2023-04-01'),
(2, 5, 8, 'Inspection', '2023-05-01');
