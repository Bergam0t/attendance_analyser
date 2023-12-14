import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import numpy as np
from st_aggrid import AgGrid

st.set_page_config(
     page_title="Zoom Log Analyser",
     layout="wide"
 )

with open("style.css") as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

st.title("Zoom Log Analyser")

st.markdown(
    """
    Upload a zoom log using the browser below. 

    All data processing is done in your browser - the log is not uploaded to an external server for processing. 
    """
)

uploaded_file = None

uploaded_file = st.file_uploader("Upload a Zoom Attendance Log", accept_multiple_files=False)

if uploaded_file is not None:

    attendance_log = pd.read_csv(uploaded_file)

    attendance_log["Duration (Minutes)"] = attendance_log["Duration (Minutes)"].astype(int) 
    attendance_log["Join Time"] = pd.to_datetime(attendance_log["Join Time"])
    attendance_log["Leave Time"] = pd.to_datetime(attendance_log["Leave Time"])

    attendance_log = attendance_log[attendance_log["In Waiting Room"] == "No"]

    total_duration_minutes = attendance_log["Duration (Minutes)"].sum()

    total_duration_hours = (total_duration_minutes / 60).round(2)

    distinct_attendees = len(attendance_log.drop_duplicates("Name (Original Name)"))

    distinct_attendees_guests = len(attendance_log[attendance_log["Guest"] == "Yes"]
                                    .drop_duplicates("Name (Original Name)")
                                    )

    guests = attendance_log[attendance_log["Guest"] == "Yes"] \
            .drop_duplicates("Name (Original Name)") \
            .sort_values("Name (Original Name)")["Name (Original Name)"] \
            .tolist()


    guests_duration = (attendance_log[attendance_log["Guest"] == "Yes"] \
                    .sort_values("Name (Original Name)") \
                    .groupby("Name (Original Name)"))["Duration (Minutes)"].agg(TotalDuration='sum')

    guests_duration.sort_values("TotalDuration")

    start = attendance_log["Join Time"].min()
    end =  attendance_log["Leave Time"].max()

    i = pd.date_range(start.replace(second=0, microsecond=0),
                    end.replace(second=0, microsecond=0) + timedelta(minutes=1),
                    freq='1min')

    interval_census_list = []

    for minute in i:
        interval_census_list.append(
            {"time": minute,
            "attendee_count": len(attendance_log[(attendance_log["Join Time"] <= minute) &
                                                (attendance_log["Leave Time"] >= minute)]
                                                )})

    concurrent_attendees_count_df = pd.DataFrame.from_dict(interval_census_list)

    attendee_history_fig = px.line(concurrent_attendees_count_df, 
                                x="time", y="attendee_count")

    attendee_history_fig.update_yaxes(
        tick0=0, dtick=10,
        range=[0, concurrent_attendees_count_df['attendee_count'].max()+10]
        )

    # attendee_history_fig.show()

    maximum_simultaneous_attendees = concurrent_attendees_count_df['attendee_count'].max()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="Maximum simultaneous Attendees", 
                value=maximum_simultaneous_attendees)
    with col2:
        st.metric(label="Total Unique Attendees", 
                value = len(guests),
                help="""
                This is a 'dumb' count of the unique attendees. 
                
                Attendees with identical names will only be counted once.
                (e.g. if you have two people with the name 'Mark' and no surname in the meeting at once, they will only be counted once)
                """
        )

        
    col4, col5, col6 = st.columns(3)

    with col4:
        mean_duration = np.mean(guests_duration['TotalDuration'])
        if mean_duration > 60:
            hours = int(mean_duration // 60)
            minutes = int(np.floor(mean_duration % 60))
            mean_duration = f"{hours} hours {minutes} minutes"
        else:
            mean_duration = f"{mean_duration} minutes"

        st.metric(label="Mean Duration of Attendance",
                  value = mean_duration)
        
    with col5:
        median_duration = np.median(guests_duration['TotalDuration'])
        if median_duration > 60:
            hours = int(median_duration // 60)
            minutes = int(np.floor(median_duration % 60))
            median_duration = f"{hours} hours {minutes} minutes"
        else:
            median_duration = f"{median_duration} minutes"

        st.metric(label="Median Duration of Attendance",
                  value = f"{median_duration} minutes")

    with col6:
        st.metric(label="Total Duration of Attendance",
                value = f"{sum(guests_duration['TotalDuration'])} minutes")

    st.plotly_chart(attendee_history_fig,
                    use_container_width=True)

    # st.select("Search for an attendee", )

    st.plotly_chart(
        px.histogram(guests_duration, x="TotalDuration"),
        use_container_width=True
        )

    with st.expander("Click here to view the length of time each person spent in the meeting"):
        AgGrid(guests_duration.sort_values("TotalDuration", ascending=False).reset_index(drop=False))

    with st.expander("Click here to view the full log"):
        AgGrid(attendance_log)
