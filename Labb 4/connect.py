import psycopg2

"""
Note: It's essential never to include database credentials in code pushed to GitHub. 
Instead, sensitive information should be stored securely and accessed through environment variables or similar. 
However, in this particular exercise, we are allowing it for simplicity, as the focus is on a different aspect.
Remember to follow best practices for secure coding in production environments.
"""

# Function to establish a connection to the database
def create_connection():
    try:
        conn = psycopg2.connect(
            host="psql-dd1368-ht23.sys.kth.se", 
            database="iggy",
            user="ncjsvg",
            password="3azXPjEq"
        )
        return conn
    except psycopg2.Error as e:
        print("Error connecting to the database:", e)
        return None

# Task 1: Search for airports
def search_airports(cur, search_term):
    query = """
        SELECT name, IATACode, country 
        FROM airport 
        WHERE name ILIKE %s OR IATACode ILIKE %s
    """
    try:
        search_term = f"%{search_term}%"
        cur.execute(query, (search_term, search_term))
        results = cur.fetchall()
        if results:
            print("Airports matching your search:")
            for name, IATACode, country in results:
                print(f"- {name} ({IATACode}), {country}")
        else:
            print("No airports found matching your search.")
    except psycopg2.Error as e:
        print("An error occurred while searching for airports:", e)

def language_speakers(cur, language_name):
    query = """
        SELECT c.name, s.language, 
               CAST(SUM(c.population * (s.percentage / 100.0)) AS BIGINT) AS numberspeaker
        FROM country c
        JOIN spoken s
        ON c.code = s.country
        WHERE s.language ILIKE %s
        GROUP BY c.name, s.language
        HAVING SUM(c.population * (s.percentage / 100.0)) > 0
        ORDER BY numberspeaker DESC;
    """
    try:
        cur.execute(query, (language_name,))
        results = cur.fetchall()
        if results:
            print(f"Countries that speak '{language_name}' and the number of speakers:")
            for country, language, speakers in results:
                print(f"- {country}: {speakers:,} speakers")
        else:
            print(f"No countries found where '{language_name}' is spoken.")
    except psycopg2.Error as e:
        print("An error occurred while searching for language speakers:", e)


def check_desert_province_count(conn, desert, country):
    # Check if a desert spans more than 9 provinces in a country
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM geo_desert 
            WHERE Desert = %s AND Country = %s
        """, (desert, country))
        count = cursor.fetchone()[0]
        if count >= 9:
            print(f"A desert can span a maximum of 9 provinces. '{desert}' already spans {count} provinces.")
            return False
        return True


def check_country_desert_count(conn, country):
    # Check if a country already has 20 deserts
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(DISTINCT Desert) 
            FROM geo_desert 
            WHERE Country = %s
        """, (country,))
        count = cursor.fetchone()[0]
        if count >= 20:
            print(f"A country can contain a maximum of 20 deserts. '{country}' already has {count} deserts.")
            return False
        return True

    
def check_desert_area(cur, desert, country, province, desert_area):
    # Query to get the area of the province
    query = "SELECT Area FROM Province WHERE Name = %s AND Country = %s"
    cur.execute(query, (province, country))
    province_area = cur.fetchone()

    # Ensure the province exists in the database
    if province_area is None:
        print(f"Province '{province}' not found in country '{country}'.")
        return False

    province_area = province_area[0]
    
    # Check if the desert's area exceeds 30 times the province's area
    if desert_area > 30 * province_area:
        print(f"The area of the desert '{desert}' cannot be more than 30 times the area of the province '{province}'.")
        return False
    else:
        return True

#Task 3a: Collect desert information
def get_desert_info(cur):
    print("Enter the following information to create a new desert:")
    # Get desert name
    name = input("Name: ").strip()
    while not name:
        print("Desert name cannot be empty.")
        name = input("Name: ").strip()
        
    # Get desert area
    while True:
        area_input = input("Area: ").strip()
        try:
            area = float(area_input)
            if area <= 0:
                print("Area must be a positive number. Please try again.")
                continue
            break
        except ValueError:
            print("Invalid input for area")
            
    # Get desert country code
    while True:
        country = input("Countrycode: ").strip()
        if not country:
            print("Countrycode cannot be empty. Please enter a valid country.")
            continue
        
        # Execute a parameterized query to prevent SQL injection
        query = "SELECT 1 FROM Province WHERE Country = %s LIMIT 1;"
        try:
            cur.execute(query, (country,))
            result = cur.fetchone()
            if result:
                break
            else:
                print(f"Countrycode '{country}' does not exist in the database. Please enter a valid countrycode.")
        except Exception as e:
            print(f"An error occurred while checking the countrycode: {e}")
            
    # Get desert province
    while True:
        province = input("Province: ").strip()
        if not province:
            print("Province cannot be empty. Please enter a valid province.")
            continue
        query = "SELECT 1 FROM Province WHERE Country = %s AND Name = %s LIMIT 1;"
        try:
            cur.execute(query, (country, province))
            result = cur.fetchone()
            if result:
                break
            else:
                print(f"Province '{province}' of country: '{country} does not exist in the database. Please enter a valid province.")
        except Exception as e:
            print(f"An error occurred while checking the province: {e}")
            
    # Get desert coordinates
    while True:
        coordinates = input("Coordinates: ").strip()
        if not coordinates:
            print("Coordinates cannot be empty. Please enter valid coordinates.")
            continue
        try:
            latitude, longitude = map(float, coordinates.split(","))
            if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                print("Invalid coordinates. Latitude must be between -90 and 90, and longitude between -180 and 180.")
                continue    
            break
        except ValueError:
            print("Invalid input for coordinates. Please enter latitude and longitude separated by a comma.")
    
    # Insert the desert into the database
    insert_desert(cur, name, area, country, province, coordinates)

#Task 3b: Insert desert information
def insert_desert(cur, desert, area, country, province, coordinates):
    # Check if the desert's area is valid
    if not check_desert_area(cur, desert, country, province, area):
        print("Desert cannot be inserted due to invalid area.")
        return False  # Exit the function if the area check fails

    # Check if the desert doesn't exceed the allowed provinces in the country
    if not check_desert_province_count(cur.connection, desert, country):
        print("Desert cannot be inserted due to exceeding the province limit.")
        return False  # Exit the function if the province count check fails

    # Check if the country has less than 20 deserts
    if not check_country_desert_count(cur.connection, country):
        print("Desert cannot be inserted due to exceeding the desert limit in the country.")
        return False  # Exit the function if the country desert count check fails
    # Insert into Geo_desert table

    try:
        query = """
            INSERT INTO geo_desert (Desert, Country, Province)
            VALUES (%s, %s, %s);
        """
        cur.execute(query, (desert, country, province))
        print(f"Desert '{desert}' successfully added into Geo_desert.")
    except psycopg2.Error as e:
        print("An error occurred while inserting into Geo_desert:", e)
    
    # Insert into Desert table if not already exists
    query = "SELECT 1 FROM desert WHERE name = %s LIMIT 1;"
    try:
        cur.execute(query, (desert,))
        result = cur.fetchone()
        if not result:
            try:
                latitude, longitude = map(float, coordinates.split(","))
                
                query = """
                    INSERT INTO desert (Name, Area, Coordinates)
                    VALUES (%s, %s, ROW(%s, %s));
                """
                cur.execute(query, (desert, area, latitude, longitude))
                print(f"Desert '{desert}' successfully added into Desert.")
            except psycopg2.Error as e:
                print("An error occurred while inserting into Desert:", e)
    except psycopg2.Error as e:
        print("An error occurred while checking if desert exists:", e)
        
    return True  # Return True if all checks passed and desert was successfully inserted


#Function to choose a task
def choose_task(cur):
    select_task = input("Select which task to perform: \n1. Search for airports\n2. List language speakers\n3. Insert a new desert\n").strip()
    if select_task not in ["1", "2", "3"]:
        print("Invalid task. Please select a valid task.")
        return choose_task(cur)
    if select_task == "1":
        print("Task 1: Search for airports")
        search_term = input("Search for airports by name or IATA code: ").strip()
        search_airports(cur, search_term)
    elif select_task == "2":
        print("Task 2: List language speakers")
        language_name = input("Enter the language name to search: ")
        language_speakers(cur, language_name)
    if select_task == "3":
        print("Task 3: Insert a new desert")
        get_desert_info(cur)
        
        

def main():
    # Establish database connection
    conn = create_connection()
    if not conn:
        return  # Exit if connection failed
    # Create a cursor
    cur = conn.cursor()
    
    print("Connection established successfully!")
    print("Welcome to lab 4:")
    
    while True:
        try:
            choose_task(cur)
        except KeyboardInterrupt:
            print("\nExiting...")
            break

    # Close cursor and connection
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
