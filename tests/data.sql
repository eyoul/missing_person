INSERT INTO role (name, description) VALUES ('admin', 'Administrator');
INSERT INTO role (name, description) VALUES ('user', 'Regular User');

INSERT INTO user (finder_name, phone, finder_location, email, password, role_id) VALUES ('John', '123456789', 'New York', 'john@example.com', 'password123', 2);
INSERT INTO user (finder_name, phone, finder_location, email, password, role_id) VALUES ('Jane', '987654321', 'Los Angeles', 'jane@example.com', 'password456', 2);

INSERT INTO post (finder_id, missed_name, since, missing_from, gender, age, call_on, additional_info, photo_url, status) VALUES (1, 'Dog', '2022-06-01', 'New York', 'Male', '2 years', '555-555-5555', 'Black and white fur, friendly', 'https://example.com/dog.jpg', 'active');
INSERT INTO post (finder_id, missed_name, since, missing_from, gender, age, call_on, additional_info, photo_url, status) VALUES (2, 'Cat', '2022-06-02', 'Los Angeles', 'Female', '1 year', '555-555-5555', 'Grey fur, green eyes', 'https://example.com/cat.jpg', 'active');
