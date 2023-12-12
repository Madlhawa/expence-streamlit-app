import streamlit as st
import pandas as pd
import psycopg2
import os

# Function to create a connection to the database
def create_connection():
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

    return psycopg2.connect(**db_params)

# Function to insert data into the PostgreSQL table
def insert_data(transaction_date, spender_name, account_name, category_name, remarks_text, amount, importance):
    conn = create_connection()
    try:
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

# Function to view data from the "expence" table with filters
def view_data(transaction_date_filter, spender_name_filter, account_name_filter, category_name_filter, amount_filter, importance_filter):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        
        # Construct the SQL query with optional filters
        select_query = """
        SELECT transaction_date,spender_name,account_name,category_name,remarks_text,amount,importance 
        FROM edwp.expence
        """
        
        # Filter by transaction date
        if transaction_date_filter:
            select_query += f" WHERE transaction_date = '{transaction_date_filter}'"
        
        # Filter by spender name
        if spender_name_filter:
            if 'WHERE' in select_query:
                select_query += f" AND spender_name = '{spender_name_filter}'"
            else:
                select_query += f" WHERE spender_name = '{spender_name_filter}'"
        
        # Filter by account name
        if account_name_filter:
            if 'WHERE' in select_query:
                select_query += f" AND account_name = '{account_name_filter}'"
            else:
                select_query += f" WHERE account_name = '{account_name_filter}'"
        
        # Filter by category name
        if category_name_filter:
            if 'WHERE' in select_query:
                select_query += f" AND category_name = '{category_name_filter}'"
            else:
                select_query += f" WHERE category_name = '{category_name_filter}'"
        
        # Filter by amount
        if amount_filter:
            if 'WHERE' in select_query:
                select_query += f" AND amount = {amount_filter}"
            else:
                select_query += f" WHERE amount = {amount_filter}"
        
        # Filter by importance
        if importance_filter:
            importance_value = "Y" if importance_filter else "N"
            if 'WHERE' in select_query:
                select_query += f" AND importance = '{importance_value}'"
            else:
                select_query += f" WHERE importance = '{importance_value}'"

        cursor.execute(select_query)
        data = cursor.fetchall()

        # Display the data in a Pandas DataFrame
        df = pd.DataFrame(data, columns=["Transaction Date", "Spender Name", "Account Name", "Category Name", "Remarks", "Amount", "Importance"])
        
        st.dataframe(df)

        if data:
            # Allow the user to select a row for editing
            selected_row = st.selectbox("Select a row to edit", [i for i in range(len(data))])

            # Create a form for editing the selected row
            with st.form("edit_data_form"):
                col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

                # Input fields for editing data
                edited_transaction_date = col1.date_input("Transaction Date", pd.to_datetime(df["Transaction Date"][selected_row]))
                edited_spender_name = col2.text_input("Spender Name", df["Spender Name"][selected_row])
                edited_account_name = col3.text_input("Account Name", df["Account Name"][selected_row])
                edited_category_name = col4.text_input("Category Name", df["Category Name"][selected_row])
                edited_remarks_text = col5.text_input("Remarks", df["Remarks"][selected_row])
                edited_amount = col6.number_input("Amount", df["Amount"][selected_row])
                edited_importance = col7.checkbox("Importance (Yes/No)", df["Importance"][selected_row] == "Y")

                # Use st.form_submit_button for editing
                edit_button = st.form_submit_button("Edit Data")

            if edit_button:
                conn = create_connection()
                try:
                    cursor = conn.cursor()

                    # Map "Yes" to "Y" and "No" to "N"
                    edited_importance_value = "Y" if edited_importance else "N"

                    # Update the selected row in the "expence" table
                    update_query = """
                    UPDATE edwp.expence
                    SET transaction_date = %s, spender_name = %s, account_name = %s, category_name = %s, remarks_text = %s, amount = %s, importance = %s
                    WHERE rowid = %s
                    """
                    data = (edited_transaction_date, edited_spender_name, edited_account_name, edited_category_name, edited_remarks_text, edited_amount, edited_importance_value, selected_row+1)
                    cursor.execute(update_query, data)

                    conn.commit()
                    st.success("Data updated successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")
                finally:
                    conn.close()

        else:
            st.info("No data available based on the applied filters.")
    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        conn.close()

# Streamlit app
if __name__ == '__main__':
    st.title("Expense Data Entry App")

    # Create a sidebar navigation
    page = st.sidebar.radio("Select Page", ("Data Entry", "View Data"))

    if page == "Data Entry":
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

    elif page == "View Data":
        # Display data viewing page
        st.header("View Data")

        # Filter options
        transaction_date_filter = st.date_input("Filter by Transaction Date")
        spender_name_filter = st.text_input("Filter by Spender Name")
        account_name_filter = st.text_input("Filter by Account Name")
        category_name_filter = st.text_input("Filter by Category Name")
        amount_filter = st.number_input("Filter by Amount")
        importance_filter = st.checkbox("Filter by Importance (Yes/No)")

        # Apply filters and display data
        view_data(transaction_date_filter, spender_name_filter, account_name_filter, category_name_filter, amount_filter, importance_filter)
