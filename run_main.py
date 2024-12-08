import streamlit as st
import pandas as pd
import plot_chart
from datetime import datetime
from sqlalchemy import create_engine

def update_db(record):
    # Connect to the database (example: SQLite)
    df_temp=pd.DataFrame([record])
    df_temp["ILevel"] = df_temp["ILevel"].apply(lambda x: ",".join(x) if isinstance(x, list) else x)

    # Append data to the 'users' table
    df_temp.to_sql('users', con=engine, if_exists='append', index=False)

#list of Market direction
market_dir ={
    f'price > EMA(50,200)',
    f'price > CPR',
    f'price > VWAP'
    }
engine = create_engine('sqlite:///example.db')  # Replace with your DB connection string
market_dir_vars = {}
for item in market_dir:
    market_dir_vars[item] = st.checkbox(item, key=item)
market_phase=''
market_img=""
if (market_dir_vars['price > EMA(50,200)']==True and market_dir_vars['price > CPR']==True and market_dir_vars['price > VWAP']==True):
    market_phase="Bullish market !"
    market_img='bull.jpg'
elif (market_dir_vars['price > EMA(50,200)']==False and market_dir_vars['price > CPR']==False and market_dir_vars['price > VWAP']==False):
    market_phase="Bearish market !"
    market_img='bear.jpg'
    
else:
    market_phase="Reversal phase !"
    market_img='pig.jpg'
st.markdown(f"<h1 style='color: #FF6347;'>{market_phase}</h1>", unsafe_allow_html=True)
st.image(market_img, width=200)


# List of conditions with weights
condition_check = {
    'EntryTime':0,
    'Trend':0,
    'Initative Pattern':0,   
    'ATR > 8': 18,
    'ADX > 20': 12,
    'ILevel': 18,
    'Colored Candle': 18,
    'EMA(8,20)': 20,
    'BB Breakout': 8,
    'VSA Volume Occurred': 4,
    'CMA Direction Occurred': 2
}

# Initialize variables for storing result data in session state
if 'result_data' not in st.session_state:
    st.session_state.result_data = []
if 'calculated_row' not in st.session_state:
    st.session_state.calculated_row = None
if 'df_table' not in st.session_state:
    st.session_state.df_table = pd.DataFrame(columns=list(condition_check.keys()) + ["Score"])

# Define the score threshold
score_threshold = 85

# Title of the app
st.title("Trading entry check list ")

# Create checkboxes and input fields for each condition
condition_vars = {}
condition_vars['EntryTime']=None
for condition, weight in condition_check.items():
    if condition == 'ILevel':
        # For 'ILevel', use a selectbox
        condition_vars[condition] = st.multiselect(
            'Select ILevel:', 
            ['NA', 'open', 'pd/w/m high/low', 'pd poc', 'interval', 'CPR', 'TLine', 'S/R','pattern(M,W)','pattern(triangle)','pattern(flag/wedge)'], 
            key=condition
        )
    elif condition =="Trend":
        condition_vars[condition] = st.selectbox(
            'Select Trend:', 
            ['NA', 'start of trend','Mid of trend'], 
            key=condition
        )
    elif condition=="Initative Pattern":
        condition_vars[condition] = st.selectbox(
            'Select Trend:', 
            ['BO', 'BOF','BO with Test','BOF with Test','Test'], 
            key=condition
        )
    elif condition!='EntryTime':
        # For other conditions, use checkboxes
        condition_vars[condition] = st.checkbox(condition, key=condition)

# Initialize the success score variable
success_score = 0
result_row = {}

# Button to calculate the score
if st.button("Calculate Score"):
    # Get the current date and time
    current_datetime = datetime.now()
    entry_time=current_datetime.strftime('%d-%m-%Y %H:%M')
    condition_vars['EntryTime']=entry_time
    # Calculate the score based on selected conditions
    if st.session_state.df_table.empty or condition_vars['ATR > 8']==True or (st.session_state.df_table.iloc[-1]['ATR > 8'] == 'Yes' and condition_vars['ATR > 8']==False) :
        for condition, value in condition_vars.items():
            if condition == 'ILevel':
                result_row[condition] = value  # Store ILevel selection
                if value and value[0] in ['open', 'pd/w/m high/low', 'pd poc', 'interval', 'CPR', 'TLine', 'S/R','pattern(M,W)','pattern(triangle)','pattern(flag/wedge)']:
                    success_score += condition_check[condition]
            elif condition not in ['EntryTime','Trend','Initative Pattern']:
                result_row[condition] = "Yes" if value else "No"
                if value:
                    success_score += condition_check[condition]
            else:
                result_row[condition]=value
        result_row["Probablity %"] = success_score
        st.session_state.calculated_row = result_row  # Save the result row in session state
        isTrending=result_row['ATR > 8']=='Yes' and result_row['ADX > 20'] =='Yes'
        level_color_ema=result_row['ILevel'] != 'NA' and result_row['Colored Candle'] == 'Yes' and result_row['EMA(8,20)'] == 'Yes'
        bb_vsa_cma=result_row['BB Breakout'] == 'Yes' and result_row['VSA Volume Occurred'] == 'Yes' and result_row['CMA Direction Occurred'] == 'Yes'
    
        # Display the calculated score
        st.write(f"Calculated Score: {success_score}")
        if result_row['ATR > 8']=='No' or result_row['ADX > 20']=='No':
            st.write("Riskier trade bcaz no trend/Volatality !")
        decision_variable={'isTrending':[isTrending],'level_color_ema':[level_color_ema],'bb_vsa_cma':[bb_vsa_cma]}
        
        df_decision_variable = pd.DataFrame(decision_variable)

        st.dataframe(df_decision_variable)
       
        st.write(f"*atleast 2 should True to click go ahead !")
    else:
        st.write('Two consecutive trade of ATR < 8 not allowed !')
        
# Show the "Go Ahead" button if a result is calculated
if st.session_state.calculated_row:
    result_row = st.session_state.calculated_row
    if result_row["Probablity %"] >= score_threshold:
        result_row['entry'] = st.number_input(f"entry price: ", value=0)
        result_row['stop_loss'] = st.number_input(f"stop loss: ", value=0)
        result_row['exit']=st.number_input(f"exit price: ",value=0)
        result_row['profit/loss']=result_row['exit']-result_row['entry']
        result_row['comments']=st.text_input("comments: ")
        if st.button("Go Ahead"):
            # Append the result to session state
            st.session_state.result_data.append(result_row)
            update_db(result_row)
            st.session_state.calculated_row = None  # Clear the calculated row after adding
            st.success("Result added to the table!")
    else:
        st.warning(f"Score below threshold of {score_threshold}. Cannot proceed.")

# Display the updated result in a table
st.write("### Results Table")
if st.session_state.result_data:
    st.session_state.df_table = pd.DataFrame(st.session_state.result_data)
    st.session_state.df_table.index += 1 
    # Define a function to apply conditional formatting
    def highlight_no(val):
        color = 'background-color: red' if val == "No" else ''
        return color

    # Apply styling to the dataframe
    styled_df = st.session_state.df_table.style.applymap(highlight_no, subset=pd.IndexSlice[:, st.session_state.df_table.columns[:-1]])  # Exclude the "Score" column
    st.dataframe(styled_df)
    
    # Add a dropdown to select a column for plotting
    st.write("### Profit/loss Chart")
    column_to_plot = 'profit/loss'
    chart_html=plot_chart.draw_line_chart(st.session_state.df_table.index,st.session_state.df_table['profit/loss'])
    st.components.v1.html(chart_html, height=500)
    
    #draw yes-no chart
    st.write("### Entry analysis Chart")
    relevent_cols=['ATR > 8','ADX > 20','Colored Candle','EMA(8,20)','BB Breakout','VSA Volume Occurred','CMA Direction Occurred']

    df=st.session_state.df_table
    df=df[relevent_cols]
    chart_yes_no=plot_chart.draw_bar_chart(df,st)
    #st.components.v1.html(chart_yes_no, height=300)
    
     
    # Add delete buttons for each row
    st.write("### Delete a Row")
    for i in range(len(st.session_state.df_table)):
       col1, col2 = st.columns([10, 1])  # Create columns for data and delete button
       with col1:
           st.write(f"Row {i + 1}: {st.session_state.df_table.iloc[i].to_dict()}")  # Display row data as a dictionary
       with col2:
           if st.button("Delete", key=f"delete_{i}"):
               # Delete the row from session state
               st.session_state.result_data.pop(i)
               st.experimental_rerun()  # Refresh to update the table
else:
    # Create an empty DataFrame with condition columns if no data exists
    st.session_state.df_table = pd.DataFrame(columns=list(condition_check.keys()) + ["Score"])


# Option to export to Excel
if st.button("Export to Excel"):
    if not st.session_state.df_table.empty:
        file_path = "condition_check_results.xlsx"
        st.session_state.df_table.to_excel(file_path, index=False)
        st.download_button("Download Excel", file_path, file_name="condition_check_results.xlsx")
    else:
        st.warning("No results to export. Please calculate the score first.")

if st.button("show from database"):
    query = "SELECT * FROM users"  # Replace 'users' with your table name
    df_db = pd.read_sql(query, con=engine)

    # Display the data in Streamlit
    st.title("Database Table")
    if not df_db.empty:
        st.dataframe(df_db)
    else:
        st.write("The table is empty or does not exist.")
