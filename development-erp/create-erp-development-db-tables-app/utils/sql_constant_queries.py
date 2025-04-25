"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

PRIMARY_KEY_QUERY = """
    ALTER TABLE {table_name}
    MODIFY COLUMN {column_name} INT NOT NULL AUTO_INCREMENT PRIMARY KEY;
"""

# Query to count the number of rows in a table
TABLE_COUNT_QUERY = "SELECT COUNT(*) FROM {table_name};"

# Query to select sku_number and order_date from a table
SELECT_SKU_NUMBER_QUERY = "SELECT sku_number FROM {table_name};"

# Query to assign unique key
UNIQUE_KEY_QUERY = """
ALTER TABLE {table_name}
ADD CONSTRAINT unique_{column_name}
UNIQUE ({column_name});
"""

# Query to add a foreign key with ON DELETE CASCADE
FOREIGN_KEY_QUERY = """
ALTER TABLE {table_name}
ADD CONSTRAINT fk_{table_name}_{column_name}
FOREIGN KEY ({column_name})
REFERENCES {reference_table}({reference_column})
ON DELETE CASCADE;
"""

# Query to check if a user exists
CHECK_USER_EXISTS_QUERY = """
SELECT COUNT(*) 
FROM mysql.user 
WHERE user = '{username}' AND host = '{host}';
"""

# Query to create a new user
CREATE_USER_QUERY = """
CREATE USER '{username}'@'{host}' IDENTIFIED BY '{password}';
"""

# Query to grant privileges to the user
GRANT_PRIVILEGES_QUERY = """
GRANT {privileges} ON *.* TO '{username}'@'{host}';
"""

# Query to flush privileges
FLUSH_PRIVILEGES_QUERY = """
FLUSH PRIVILEGES;
"""

# Query to modify TEXT column to VARCHAR(255) (for MySQL indexing constraints)
MODIFY_TEXT_TO_VARCHAR_QUERY = """
ALTER TABLE {table_name}
MODIFY COLUMN {column_name} VARCHAR(255) NOT NULL;
"""
