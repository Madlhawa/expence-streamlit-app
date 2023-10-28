import streamlit as st
import psycopg2
import os

cockroachdb_username = os.environ['COCKROACHDB_USERNAME']
cockroachdb_password = os.environ['COCKROACHDB_PASSWORD']
cockroachdb_host = os.environ['COCKROACHDB_HOST']
cockroachdb_port = os.environ['COCKROACHDB_PORT']

# Database connection parameters
params = {
    'database': 'expence',
    'user': cockroachdb_username,
    'password': cockroachdb_password,
    'host': cockroachdb_host,
    'port': cockroachdb_port,
    'sslmode': 'require',
    # 'sslrootcert': '/path/to/your/root/cert.crt'
}

# Streamlit app
def main():
    st.title("CockroachDB Record Insertion")

    # Input fields
    field1 = st.text_input("Field 1")
    field2 = st.text_input("Field 2")

    if st.button("Insert Record"):
        insert_record(field1, field2)

def insert_record(field1, field2):
    try:
        # Connect to the database
        conn = psycopg2.connect(**params)

        # Create a cursor object
        cur = conn.cursor()

        # SQL query
        query = f"""INSERT INTO edwp.expence (spender_name, account_name)
                    VALUES('{field1}', '{field2}');"""

        # Execute the query
        cur.execute(query)

        # Commit the transaction
        conn.commit()

        # Close the cursor and connection
        cur.close()
        conn.close()

        st.success("Record inserted successfully!")

    except Exception as e:
        st.error(f"Error: {e}")

if __name__ == "__main__":
    main()