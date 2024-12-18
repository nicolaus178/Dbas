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
            user="namn",
            password="losen"
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
def insert_desert(cur, name, area, country, province, coordinates):
    
    # Insert into Geo_desert table
    try:
        query = """
            INSERT INTO geo_desert (Desert, Country, Province)
            VALUES (%s, %s, %s);
        """
        cur.execute(query, (name, country, province))
        print(f"Desert '{name}' successfully added intro Geo_desert.")
    except psycopg2.Error as e:
        print("An error occurred while inserting into Geo_desert:", e)
    
    # Insert into Desert table if not already exists
    query = "SELECT 1 FROM desert WHERE name = %s LIMIT 1;"
    try:
        cur.execute(query, (name,))
        result = cur.fetchone()
        if not result:
            try:
                latitude, longitude = map(float, coordinates.split(","))
                
                query = """
                    INSERT INTO desert (Name, Area, Coordinates)
                    VALUES (%s, %s, ROW(%s, %s));
                """
                cur.execute(query, (name, area, latitude, longitude))
                print(f"Desert '{name}' successfully added into Desert.")
            except psycopg2.Error as e:
                print("An error occurred while inserting into Desert:", e)
    except psycopg2.Error as e:
        print("An error occurred while checking if desert exists:", e)
    

#Function to choose a task
def choose_task(cur):
    select_task = input("Select which task to perform: \n1. Search for airports\n3. Insert a new desert\n").strip()
    if select_task not in ["1", "2", "3"]:
        print("Invalid task. Please select a valid task.")
        return choose_task()
    if select_task == "1":
        print("Task 1: Search for airports")
        search_term = input("Search for airports by name or IATA code: ").strip()
        search_airports(cur, search_term)
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
