import streamlit as st
import pandas as pd
import os
from datetime import datetime

#test command
#st.logo("smt_logo.png", size='large', link=None, icon_image="smt_logo.png")
st.set_page_config(page_title="SMT-Stock Ledger", layout="wide")

# File paths
STOCK_FILE = "stock_data.xlsx"
TRANSACTIONS_FILE = "transactions_data.xlsx"

# Load data from files if they exist
if os.path.exists(STOCK_FILE):
    stock_df = pd.read_excel(STOCK_FILE)
else:
    stock_df = pd.DataFrame(columns=['Item Name', 'Supplier', 'Quantity'])

if os.path.exists(TRANSACTIONS_FILE):
    transactions_df = pd.read_excel(TRANSACTIONS_FILE)
else:
    transactions_df = pd.DataFrame(columns=['Item Name', 'Quantity', 'Type', 'Board/Project', 'Employee Name', 'Date'])

# Store data in session state
st.session_state['stock'] = stock_df
st.session_state['transactions'] = transactions_df

# Add logo in the sidebar
st.sidebar.image("smt_logo.png", use_container_width=True)

# Dummy user authentication
def authenticate(username, password):
    users = {'admin': 'admin123', 'user': 'user123'}
    return users.get(username) == password

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['username'] = ''

# Login Page
if not st.session_state['logged_in']:
    st.title("Stock Maintenance Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if authenticate(username, password):
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.rerun()
        else:
            st.error("Invalid username or password")
else:
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Go to", ["Dashboard", "Add Item", "Receive Stock", "Take Out Stock", "Check Stock"])
    
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = ''
        st.rerun()
    
    st.title("Stock Maintenance System")
    
    if choice == "Dashboard":
        st.header("Low Stock Items (Qty < 5)")
        low_stock = st.session_state['stock'][st.session_state['stock']['Quantity'] < 5]
        st.table(low_stock)
        
        st.header("Recent 5 Takeout Transactions")
        recent_txns = st.session_state['transactions'][st.session_state['transactions']['Type'] == 'Take Out'].tail(5)
        st.table(recent_txns)
        
    elif choice == "Add Item" and st.session_state['username'] == 'admin':
        st.header("Add New Item")
        item_name = st.text_input("Item Name")
        supplier = st.text_input("Supplier")
        if st.button("Add Item"):
            new_item = pd.DataFrame([[item_name, supplier, 0]], columns=['Item Name', 'Supplier', 'Quantity'])
            st.session_state['stock'] = pd.concat([st.session_state['stock'], new_item], ignore_index=True)
            st.session_state['stock'].to_excel(STOCK_FILE, index=False)
            st.success("Item added successfully")
    
    elif choice == "Receive Stock" and st.session_state['username'] == 'admin':
        st.header("Receive Stock")
        item = st.selectbox("Select Item", st.session_state['stock']['Item Name'].unique())
        qty = st.number_input("Quantity", min_value=1, step=1)
        inv_num = st.text_input("Invoice Number (Optional)")
        inv_date = st.date_input("Invoice Date (Optional)")
        if st.button("Update Stock"):
            st.session_state['stock'].loc[st.session_state['stock']['Item Name'] == item, 'Quantity'] += qty
            new_txn = pd.DataFrame([[item, qty, 'Receive', '', '', datetime.now().strftime('%Y-%m-%d')]], 
                                   columns=['Item Name', 'Quantity', 'Type', 'Board/Project', 'Employee Name', 'Date'])
            st.session_state['transactions'] = pd.concat([st.session_state['transactions'], new_txn], ignore_index=True)
            st.session_state['stock'].to_excel(STOCK_FILE, index=False)
            st.session_state['transactions'].to_excel(TRANSACTIONS_FILE, index=False)
            st.success("Stock updated successfully")
    
    elif choice == "Take Out Stock":
        st.header("Take Out Stock")
        item = st.selectbox("Select Item", st.session_state['stock']['Item Name'].unique())
        available_qty = st.session_state['stock'].loc[st.session_state['stock']['Item Name'] == item, 'Quantity'].values[0]
        st.write(f"Available Quantity: {available_qty}")
        qty = st.number_input("Quantity", min_value=1, step=1)
        project = st.text_input("Board/Project (Optional)")
        employee_name = st.text_input("Employee Name")
        if st.button("Take Out"):
            if available_qty >= qty:
                st.session_state['stock'].loc[st.session_state['stock']['Item Name'] == item, 'Quantity'] -= qty
                new_txn = pd.DataFrame([[item, qty, 'Take Out', project, employee_name, datetime.now().strftime('%Y-%m-%d')]], 
                                       columns=['Item Name', 'Quantity', 'Type', 'Board/Project', 'Employee Name', 'Date'])
                st.session_state['transactions'] = pd.concat([st.session_state['transactions'], new_txn], ignore_index=True)
                st.session_state['stock'].to_excel(STOCK_FILE, index=False)
                st.session_state['transactions'].to_excel(TRANSACTIONS_FILE, index=False)
                st.success("Stock take out recorded")
            else:
                st.error("Not enough stock available")
    
    elif choice == "Check Stock":
        st.header("Check Stock")
        item_filter = st.text_input("Filter by Item Name")
        supplier_filter = st.text_input("Filter by Supplier")
        filtered_stock = st.session_state['stock']
        if item_filter:
            filtered_stock = filtered_stock[filtered_stock['Item Name'].str.contains(item_filter, case=False, na=False)]
        if supplier_filter:
            filtered_stock = filtered_stock[filtered_stock['Supplier'].str.contains(supplier_filter, case=False, na=False)]
        st.table(filtered_stock)
