INSERT INTO users (id, username, oauth_provider, oauth_id, email, profile_image, created_at, updated_at)
VALUES 
(1, 'john_doe', 'google', 'oauth_12345', 'john@example.com', 'https://example.com/john.jpg', NOW(), NOW()),
(2, 'alice_smith', 'facebook', 'oauth_67890', 'alice@example.com', 'https://example.com/alice.jpg', NOW(), NOW()),
(3, 'bob_marley', 'github', 'oauth_54321', 'bob@example.com', 'https://example.com/bob.jpg', NOW(), NOW());

INSERT INTO tags (id, tagname)
VALUES 
(1, 'Python'),
(2, 'Flutter'),
(3, 'Machine Learning');

INSERT INTO videos (id, title, url, thumbnail, summation, video_length, user_id, created_at, updated_at)
VALUES 
(1, 'Learn Python Basics', 'https://example.com/python.mp4', 'https://example.com/python.jpg', 'Intro to Python', '120', 1, NOW(), NOW()),
(2, 'Flutter for Beginners', 'https://example.com/flutter.mp4', 'https://example.com/flutter.jpg', 'Flutter UI Basics', '95', 2, NOW(), NOW()),
(3, 'ML Algorithms Explained', 'https://example.com/ml.mp4', 'https://example.com/ml.jpg', 'Understanding ML', '150', 3, NOW(), NOW());

INSERT INTO video_tags (id, video_id, tag_id, created_at)
VALUES 
(1, 1, 1, NOW()),
(2, 2, 2, NOW()),
(3, 3, 3, NOW()), 
(4, 3, 1, NOW());

INSERT INTO user_tags (id, user_id, tag_id, created_at)
VALUES 
(1, 1, 1, NOW()),
(2, 2, 2, NOW()),
(3, 3, 3, NOW()),
(4, 3, 1, NOW()); 