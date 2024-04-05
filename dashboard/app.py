from shiny import reactive, render
from shiny.express import ui

# Python Standard Library Imports
import random
from datetime import datetime
from collections import deque
import plotly.express as px
from shinywidgets import render_plotly
from scipy import stats

from faicons import icon_svg

# Pandas import for data
import pandas as pd

# Add icons
from faicons import icon_svg

# Update interval to simulate live data
UPDATE_INTERVAL_SECS: int = 2

# Initializing a reactive value to store the data
DEQUE_SIZE: int = 10
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))

# Initializing a reactive calc to display the latest data
@reactive.calc()
def reactive_calc_combined():
    # Invalidate this calculation every UPDATE_INTERVAL_SECS to trigger updates
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)

    # Data generation code
    temp = round(random.uniform(74, 99), 1)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_dictionary_entry = {"temp": temp, "timestamp": timestamp}

    # Get the deque and append the new entry
    reactive_value_wrapper.get().append(new_dictionary_entry)

    # Get a snapshot of the current deque for any further processing
    deque_snapshot = reactive_value_wrapper.get()

    # For Display: convert deque to DataFrame for display
    df = pd.DataFrame(deque_snapshot)

    # For Display: get the latest dictionary entry
    latest_dictionary_entry = new_dictionary_entry

    # Return a tuple with everything
    return deque_snapshot, df, latest_dictionary_entry

# Page layout

ui.page_opts(title="PyShiny Express: Live Data", fillable=True)

# Sidebar setup
with ui.sidebar(open="open"):
    ui.h2("Southern Florida Explorer", class_="text-center")
    ui.p(
        "A demonstration of real-time temperature readings in Florida.",
        class_="text-center",
    )
    ui.hr()
    ui.h6("Quick Links:")
    ui.a(
        "GitHub Source", href="https://github.com/nhansen23/cintel-05-cintel",target="_blank",
    )
    ui.a(
        "GitHub App", href="https://github.com/nhansen23/cintel-05-cintel/blob/main/dashboard/app.py",target="_blank",
    )

# Main panel setup
with ui.layout_columns():
    with ui.value_box(
        showcase=icon_svg("sun"),
        theme="bg-yellow",
    ):
        
        "Current Temperature"

        @render.text
        def display_temp():
            """Get the latest reading and return a temperature string"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['temp']} C"

        "warmer than usual"

    #with ui.card(full_screen=True, min_height="40%"):
    with ui.card(full_screen=True):
        ui.card_header("Most Recent Readings")

        @render.data_frame
        def display_df():
            """Get the latest reading and return a dataframe with current readings"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            pd.set_option('display.width', None)        # Use maximum width
            return render.DataGrid( df,width="100%")


with ui.card(full_screen=True):
    ui.card_header("Current Date and Time")

    @render.text
    def display_time():
        """Get the latest reading and return a timestamp string"""
        deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
        return f"{latest_dictionary_entry['timestamp']}"
    
    with ui.card():
        ui.card_header("Chart with Current Trend")

        @render_plotly
        def display_plot():
        # Fetch from the reactive calc function
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()

         # Ensure the DataFrame is not empty before plotting
            if not df.empty:
                # Convert the 'timestamp' column to datetime for better plotting
               df["timestamp"] = pd.to_datetime(df["timestamp"])

                # Create scatter plot for readings
                # pass in the df, the name of the x column, the name of the y column,
                # and more
        
            fig = px.scatter(df,
                x="timestamp",
                y="temp",
                title="Temperature Readings with Regression Line",
                labels={"temp": "Temperature (°C)", "timestamp": "Time"},
                color_discrete_sequence=["blue"] )
            
                # Linear regression - we need to get a list of the
                # Independent variable x values (time) and the
                # Dependent variable y values (temp)
                # then, it's pretty easy using scipy.stats.linregress()

                # For x let's generate a sequence of integers from 0 to len(df)
            sequence = range(len(df))
            x_vals = list(sequence)
            y_vals = df["temp"]

            slope, intercept, r_value, p_value, std_err = stats.linregress(x_vals, y_vals)
            df['best_fit_line'] = [slope * x + intercept for x in x_vals]

            # Add the regression line to the figure
            fig.add_scatter(x=df["timestamp"], y=df['best_fit_line'], mode='lines', name='Regression Line')

            # Update layout as needed to customize further
            fig.update_layout(xaxis_title="Time",yaxis_title="Temperature (°C)")

            return fig
