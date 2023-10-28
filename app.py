import streamlit as st
import psycopg2
import os

cockroachdb_username = os.environ['COCKROACHDB_USERNAME']
cockroachdb_password = os.environ['COCKROACHDB_PASSWORD']
cockroachdb_host = os.environ['COCKROACHDB_HOST']
cockroachdb_port = os.environ['COCKROACHDB_PORT']

# Database connection parameters
db_params = {
    'database': 'expence',
    'user': cockroachdb_username,
    'password': cockroachdb_password,
    'host': cockroachdb_host,
    'port': cockroachdb_port,
    'sslmode': 'require',
    # 'sslrootcert': '/path/to/your/root/cert.crt'
}

# Function to insert data into the PostgreSQL table
def insert_data(transaction_date, spender_name, account_name, category_name, remarks_text, amount, importance):
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        # Map "Yes" to "Y" and "No" to "N"
        importance_value = "Y" if importance else "N"
        
        # Insert data into the "expence" table
        insert_query = """
        INSERT INTO edwp.expence (transaction_date, spender_name, account_name, category_name, remarks_text, amount, importance)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        data = (transaction_date, spender_name, account_name, category_name, remarks_text, amount, importance_value)
        cursor.execute(insert_query, data)
        
        conn.commit()
        st.success("Data inserted successfully!")
    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        conn.close()

# Streamlit app
if __name__ == '__main__':
    st.title("Expense Data Entry App")
    
    # Display success message at the top of the page
    success_message = st.empty()

    # Use st.form to enable Enter key submission
    with st.form("expense_data_form"):
        # Create a layout with two columns
        col1, col2 = st.columns(2)

        # Input fields for data
        transaction_date = col1.date_input("Transaction Date")
        
        # Vertically center the "Importance (Yes/No)" checkbox in col2
        with col2:
            st.text("")  # Add a space for vertical alignment
            st.text("")  # Add a space for vertical alignment
            importance = st.checkbox("Importance (Yes/No)")
        
        # Create a layout with two columns
        col1, col2 = st.columns(2)

        # Radio button for spender_name with the specified options in the first column
        spender_name_options = ["Madhawa", "Nimesha", "Common"]
        spender_name = col1.radio("Spender Name", spender_name_options)
        
        # Radio button for account_name with the specified options in the second column
        account_name_options = ["Commercial", "Frimi", "NTB -Debit Card", "NTB -Credit Card", "Seylan Card", "Sampath", "Cash"]
        account_name = col1.radio("Account Name", account_name_options)
        
        # Radio button for category_name with the specified options
        category_name_options = ["Food & Drink", "Groceries", "Clothes", "Bills", "Petrol & Vehicle", "Other", "Loans", "Cash",
                                "Home Items", "Electronics", "Entertainment", "N Family", "Gift", "M Family", "Education", "Health"]
        category_name = col2.radio("Category Name", category_name_options)

        amount = col1.number_input("Amount")    

        # Use a text input for remarks
        remarks_text = st.text_input("Remarks")

        # Use st.form_submit_button for Enter key submission
        submit_button = st.form_submit_button("Insert Data")

    if submit_button:
        insert_data(transaction_date, spender_name, account_name, category_name, remarks_text, amount, importance)
        # Display success message at the top of the page
        success_message.success("Data inserted successfully!")
