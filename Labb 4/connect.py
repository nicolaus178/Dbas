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

    
def choose_task(cur):
    select_task = input("Select which task to perform: \n1. Search for airports\n2. List language speakers\n")
    if select_task not in ["1", "2", "3"]:
        print("Invalid task. Please select a valid task.")
        return choose_task(cur)
    if select_task == "1":
        print("Task 1: Search for airports")
        search_term = input("Search for airports by name or IATA code: ")
        search_airports(cur, search_term)
    elif select_task == "2":
        print("Task 2: List language speakers")
        language_name = input("Enter the language name to search: ")
        language_speakers(cur, language_name)
        
        

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
            print("Exiting...")
            break

    # Close cursor and connection
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
