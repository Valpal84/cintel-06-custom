# Add imports
from shiny import reactive, render
from shiny.express import ui
from shiny.express import input
import random
from datetime import datetime
from faicons import icon_svg
from collections import deque
import pandas as pd
import plotly.express as px
from shinywidgets import render_plotly
from scipy import stats
import seaborn as sns
from shinyswatch import theme

# Load diamonds dataset into a df
diamonds_df = sns.load_dataset('diamonds')

UPDATE_INTERVAL_SECS: int = 2

# Add a deque
DEQUE_SIZE: int = 5
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))

@reactive.calc()
def reactive_calc_combined():
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)
    
    # Data generation logic
    cost = round(random.uniform(100, 120), 2)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_dictionary_entry = {"cost":cost, "timestamp":timestamp}

    #Get the deque and append the new entry
    reactive_value_wrapper.get().append(new_dictionary_entry)

     #Get a snapshot of the current deque for any further processing
    deque_snapshot = reactive_value_wrapper.get()

    #For display Convert deque to dataframe for display
    df = pd.DataFrame(deque_snapshot)

    #For display-get the latest dictionary entry
    latest_dictionary_entry = new_dictionary_entry

    #Return a tuple with everything we need
    return deque_snapshot, df, latest_dictionary_entry

# Adding a page title
ui.page_opts(title="Valerie's Diamond Dashboard", fillable=True)

# Adding a page theme
theme.vapor()

# Adding a sidebar and sidebar components
with ui.sidebar(open="open"):
    ui.h3("Facts About Diamonds", class_="text-center", style="color:navy")
    ui.p(
        "A demonstration of real-time costs for sourced diamonds.",
        class_="text-center",
    )
    ui.input_numeric("plotly_bin_count", "Bin_count", 1, min=1, max=53940)
    ui.input_checkbox_group("selected_diamond_cut",
                           "cut",
                           ["Premium", "Ideal", "Very Good", "Good", "Fair"],
                           selected=["Very Good"],
                           inline=True,
                           )
    ui.input_slider("carat", "Carat", 0,2.5, 1)
    ui.hr()
    ui.h6("Helpful Links:")
    ui.a(
        "Valerie's GitHub Source",
        href="https://github.com/Valpal84/cintel-05-cintel", 
        target="_blank",
    )
    
    ui.a("PyShiny", href="https://shiny.posit.co/py/", target="_blank")
    ui.a(
        "Seaborn's Diamond Dataset",
        href="https://github.com/mwaskom/seaborn-data/blob/master/diamonds.csv",
        target="_blank",
    )

# Main content area

ui.h2("Current Cost", style="color:navy")

with ui.layout_columns():
    with ui.value_box(
        showcase=icon_svg("wallet")):
      
        "Current Diamond Cost"
        
        @render.text
        def display_temp():
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['cost']} $"


        "Higher than average costs"

    with ui.value_box(showcase=icon_svg("calendar")):

        "Current Date and Time"
        
        @render.text
        def display_time():
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            theme="bg-gradient-green-blue",
            return f"{latest_dictionary_entry['timestamp']}"

with ui.layout_columns():
    with ui.navset_card_pill(id="tab1"):
        with ui.nav_panel("Diamond Data Table"):

            @render.data_frame
            def diamonds_data_table():
                return render.DataTable(filtered_data())

        with ui.nav_panel("Diamond Data Grid"):

            @render.data_frame
            def diamonds_data_grid():
                return render.DataGrid(filtered_data())


    with ui.card(full_screen=True):
        ui.card_header("Most Recent Diamond Costs")

        @render.data_frame
        def display_df():
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            pd.set_option('display.width', None)
            return render.DataGrid(df,width="100%")
            
    with ui.card():
        ui.card_header("Chart with Current Trend")

        @render_plotly
        def display_plotly():
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()

            if not df.empty:
                df["timestamp"] = pd.to_datetime(df["timestamp"])

                fig = px.scatter(df,
                x="timestamp",
                y="cost",
                title="Diamond Costs with Regression Line",
                labels={"cost": "Cost in American Dollars ($)", "timestamp": "Timestamp"},
                color_discrete_sequence=["teal"])

                sequence = range(len(df))
                x_vals = list(sequence)
                y_vals = df["cost"]

                slope, intercept, r_value, p_value, std_err = stats.linregress(x_vals, y_vals)
                df['best_fit_line'] = [slope * x + intercept for x in x_vals]
                
                #add regresion line to figure
                fig.add_scatter(x=df["timestamp"], y=df['best_fit_line'], mode='lines', name='Regression Line')

                #update layout as needed to customize further
                fig.update_layout(xaxis_title="Time",yaxis_title="Diamond Cost in American Dollars ($)")
                return fig
            
@reactive.calc
def filtered_data():
    return diamonds_df[diamonds_df["cut"].isin(input.selected_diamond_cut())]
           
