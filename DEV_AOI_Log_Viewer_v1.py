# AOI_LOG_VIEWER
# 2024 OCT-DEC
# Version :1
# Task - read from master files and show visualizations, query features in Streamlit dashboard
# Code performs the following:
# Opens the Master csv files for each module
# dynamic visualizations within Streamlit page
# Will display generic stats on alarms and logs
# user to select the required module to deep dive
# option to query, download the filtered and compiled alarm data
# this is the code for streamlit dashboard hosted in HICP

# ----------------------------
# for Version 2, consider a master file combining all modules
# ------------------------

# Import Modules

import pandas as pd
import os
import matplotlib.pyplot as plt
from datetime import datetime as dt
from datetime import timedelta, timezone, date
import random
import string
import os
import numpy as np
import sys
from decouple import Config, RepositoryEnv
import smbclient
from smb.SMBConnection import *
import time
from time import time as t
import datetime
import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.add_vertical_space import add_vertical_space
from pandas.errors import EmptyDataError
from streamlit_dynamic_filters import DynamicFilters

# Helper function for a full-width rainbow divider
def custom_rainbow_divider():
    st.markdown(
        '<hr style="border: 0; height: 2px; background: linear-gradient(to right, red, orange, yellow, green, blue, indigo, violet); margin: 0 -20px; padding: 0;">', 
        unsafe_allow_html=True
    )
    
DOTENV_FILE = '.env'
env_config = Config(RepositoryEnv(DOTENV_FILE))

# Define base path local
local_base_path = r"C:\INSIG_AOI_LOG_VIEWER\EXTRACTED_LOGS"

#user = env_config.get('UN')

#print(user)
#serverName = 'BTHSDV006.infineon.com'
#print(serverName)
#shareName = 'INSIG_AOI_LOG_VIEWER'
#print(shareName)
#folderName = 'EXTRACTED_LOGS'
#print(folderName)

#sk = env_config.get('APPKEY')
#password = env_config.get('PASSWORD')

# setting up connection
#conn = SMBConnection(username=user, password=password, my_name="icp", remote_name=serverName, use_ntlm_v2=True)
#ip_address = socket.gethostbyname(serverName)
#print(conn.connect(ip_address, 139))
# path for  Data source, Static folder

# Support functions for HICP page
# boxplot
# bar chart
# alarmpareto
# genlogs- parse a csv file (master file) to generate a dataframe for dashboard functioning

def bxplt(direc, file, grpby, cols, plotname, title):
    df = pd.read_excel(file)
    try:
        fig = df.boxplot(by=grpby, column=cols, grid=False).get_figure()
        fig.suptitle(title)
        fig.savefig(direc + plotname)
        plt.close(fig)
    except ValueError:
        pass

    return print("{} plot has been generated".format(cols))


def piechart(direc, df, groupby, count_variable, title, plotname):
    try:
        df = df.groupby([groupby], as_index=False, sort=True)[count_variable].count()
        label = df[groupby].values.tolist()
        plt.style.use('dark_background')
        ax = df.plot(y=count_variable, kind='pie', autopct='%1.1f%%', startangle=0, figsize=(14, 7))
        # plt.legend(loc='upper left',labels=label)
        plt.title(title)
        plt.legend(loc='best', labels=label, bbox_to_anchor=(1, 1))
        plt.ylabel('')
        plt.autoscale(True)
        plt.tight_layout()
        plt.savefig(direc + plotname)
        plt.close()
    except ValueError:
        pass

    return print("{} has been generated".format(plotname))


def alarmpareto(df, groupby, count_variable, ylabel, title):
    try:
        df = df.groupby([groupby], as_index=False, sort=True)[count_variable].count()
        df = df.sort_values(by=count_variable, ascending=False)
        df = df.head(10)
        df["cumpercentage"] = df[count_variable].cumsum() / df[count_variable].sum() * 100
        # plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(14, 12))
        ax.bar(df[groupby], df[count_variable], color="C0")
        ax2 = ax.twinx()
        ax2.plot(df[groupby], df["cumpercentage"], color="C1", marker="D", ms=7)
        ax2.yaxis.set_major_formatter(PercentFormatter())
        for x_val, y_val in zip(range(len(df)), df["cumpercentage"]):
            # set the format of the text to %
            text = f"{y_val:.2f}"
            # place the text labels on the graph
            if y_val > .95:
                ax2.text(
                    x=x_val + 0.10,
                    y=y_val - 0.025,
                    s=text,
                    fontsize=8,
                    color="white",
                    ha="right",
                    va="center"
                )
            else:
                ax2.text(
                    x=x_val - 0.10,
                    y=y_val + 0.025,
                    s=text,
                    fontsize=8,
                    color="white",
                    ha="right",
                    va="center"
                )
        ax2.set_ylabel(ylabel)
        ax.tick_params(axis="x", rotation=90)
        ax2.tick_params(axis="y", rotation=0)
        plt.title(title)
        plt.autoscale(True)
        plt.tight_layout()
        return plt
    except ValueError:
        pass

    return print("plot has been generated")


def barchart(df, groupby, count_variable, xlabel, ylabel, title):
    # Zip Method to Concatnate element wise for 2 lists
    try:
        df.groupby(groupby)[count_variable].count().plot(kind='bar', colormap='Dark2', figsize=(14, 12))
        plt.xlabel(xlabel, fontweight='bold')
        plt.ylabel(ylabel, fontweight='bold')
        plt.title(title, fontweight='bold')
        plt.grid(False)
        plt.autoscale(True)
        plt.tight_layout()
        plt.show()
        # plt.savefig(direc + plotname)
        plt.close()
    except ValueError:
        pass

    return print("plot has been generated")


def genlogs(log_dir, log_name, col_headers):
    f = log_dir + log_name
    # print("filename is", f)
    df_file_name = pd.read_csv(f, encoding='utf-8', names=col_headers, on_bad_lines='skip',
                               header=None, engine='python', skiprows=[0])
    return df_file_name
    # df_file_name = pd.read_csv(f )
    # skiprows =[2]  skip specific row 2
    # skiprows =2 skip first 3
    # offending lines to be skipped. , header = 1)
    # header = 1 header : int, list of int, (Default ‘infer’) Row number(s) to use as the column names,
    # df_log = pd.read_csv(f, header= 0, sep= " ", on_bad_lines='skip'
    # df_img.columns = cl_list
    # df_log.to_excel((save_directory + df_file_name), engine='openpyxl', index=False)


alarm_dict = {"IMH": ["The IMHModule detected an invalid slot number to be processed",
                      "The IMHModule is still not completed its sequence",
                      "The IMHModule is still not completed its FirstSlot sequence",
                      "The IMHModule is still not completed its unloading sequence",
                      "The IMHModule failed to load the magazine at LoadingDeck",
                      "The IMHModule failed to unload the magazine at UnloadingDeck",
                      "The LF kicking sequence was stopped",
                      "The magazine loading sequence is stopped",
                      "The magazine unloading sequence is cancelled",
                      "The IMH unloading is already full of magazines",
                      "The IMH elevator is detected with magazine in it",
                      "The IMH elevator is detected without magazine in it",
                      "The IMH MagClamper failed to detect magazine in it.",
                      "The IMH MagClamper failed to detect magazine in it",
                      "The IMHModule detected an invalid slot number to be processed",
                      "There is no LF detected after kicking",
                      "IMH tried to wait for the magazine deck rear sensor to be cleared in a defined period of time",
                      "IMH tried to wait for the magazine deck rear sensor to be triggered in a defined period of time",
                      "IMH tried to wait for the unloading deck front sensor to be triggered in a defined period of time",
                      "IMH tried to wait for the unloading deck rear sensor to be triggered in a defined period of time",
                      "IMH tried to wait for the loading deck rear sensor to be triggered in a defined period of time",
                      "IMH tried to wait for the loading deck magazine sensor to be triggered in a defined period of time",
                      "IMH tried to wait for the Z clear sensor to be cleared in a defined period of time",
                      "The IMH MagClamper tried to wait for the MagClamperOpenSensor to be triggered",
                      "The IMH MagClamper tried to wait for the MagClamperCloseSensor to be triggered",
                      "The IMH MagClamper tried to wait for the KickerExtendSensor to be triggered",
                      "The IMH MagClamper tried to wait for the KickerRetractSensor to be triggered",
                      "IMH Lower Deck Puller Not At Rear Posn", "IMH Lower Deck Puller Not At Front Posn",
                      "Leadframe protrude detected an VM input track", "IMH mag unloader magazine present",
                      "IMH mag unloader magazine not present", "Timeout waiting clamper close",
                      "IMH Timeout Opening Magazine Cover",
                      "IMH Timeout Closing Magazine Cover", "IMH Magazine Cover Is Opened",
                      "IMH Magazine Cover Is Closed",
                      "Failed to read magazine ID", "Timeout reading magazine ID",
                      "Leadframe jam is detected at kicker",
                      ""
                      ],
              "OMH": ["The OMHModule detected an invalid slot number to be processed",
                      "The OMHModule is still not completed its sequence",
                      "The OMHModule is still not completed its unloading sequence",
                      "The OMHModule failed to load the magazine at LoadingDeck",
                      "The OMHModule failed to unload the magazine at UnloadingDeck",
                      "The magazine loading sequence is stopped", "The magazine unloading sequence is cancelled",
                      "The OMH unloading is already full of magazines",
                      "The OMH elevator is detected with magazine in it",
                      "The OMH elevator is detected without magazine in it",
                      "The OMH MagClamper failed to detect magazine in it",
                      "The OMHModule is still not completed its FirstSlot sequence",
                      "The OMH MagPicker is not in retracted position", "The OMH slot sensor is not properly aligned",
                      "There is an existing frame detected at the target slot",
                      "OMH tried to wait for the magazine deck rear sensor to be cleared in a defined period of time",
                      "OMH tried to wait for the magazine deck rear sensor to be triggered in a defined period of time",
                      "OMH tried to wait for the unloading deck front sensor to be triggered in a defined period of time",
                      "OMH tried to wait for the unloading deck rear sensor to be triggered in a defined period of time",
                      "OMH tried to wait for the loading deck rear sensor to be triggered in a defined period of time",
                      "OMH tried to wait for the loading deck magazine sensor to be triggered in a defined period of time",
                      "OMH tried to wait for the Z clear sensor to be cleared in a defined period of time",
                      "The OMH MagClamper tried to wait for the MagClamperOpenSensor to be triggered",
                      "The OMH MagClamper tried to wait for the MagClamperCloseSensor to be triggered",
                      "The OMH MagClamper tried to wait for the MagClamperCloseSensor to be triggered",
                      "The OMH MagClamper tried to wait for the MagClamperOpenSensor to be triggered",
                      "The OMH MagClamper tried to wait for the MagClamperCloseSensor to be triggered",
                      "The OMH MagClamper tried to wait for the MagClamperCloseSensor to be triggered",
                      "The OMH MagPicker is not in extended position", "The OMH MagPicker is not in extended position",
                      "IX2 not in safe position for OMH", "Leadframe not detected at OMH slot",
                      "OMH Lower Deck Puller Not At Rear Posn", "OMH Lower Deck Puller Not At Front Posn",
                      "OMH Timeout Opening Magazine Cover", "OMH Timeout Closing Magazine Cover",
                      "OMH Magazine Cover Is Opened", "OMH Magazine Cover Is Closed", "Failed to read magazine ID",
                      "Timeout reading magazine ID", "Could not start with magazine loaded."],
              "MAIN": ["Unknown error", "Main Air Pressure signal is triggered",
                       "Fan rotation sensor is not pulsing",
                       "Emergency stop signal is triggered",
                       "One of the modules is still processing the HOMING sequence",
                       "Main door is opened"],
              "COMMON": ["Motion / IO card cannot be initialized",
                         "Failed to enable the axis", "Axis contactor is not activated",
                         "Invalid axis parameter value", "Specific axis is still processing its HOMING sequence",
                         "Axis failed to execute / complete the HOMING sequence",
                         "Axis failed to execute / complete the MOVE sequence",
                         "IO failed to execute commands",
                         "Sequence was not completed within the specified period of time",
                         "One of the axis is not homed yet", "Error detected at Vision"],
              "RM": ["One of the RM axes are still homing",
                     "Incorrect hole number is returned when querying for index hole",
                     "The RejectModule failed to query reject position data due to several parameter failures",
                     "The Puncher is at its DOWN position state",
                     "The puncher not able to reached to its UP state within a defined time",
                     "The puncher not able to reached to its DOWN state within a defined time",
                     "The DieBlock not able to reached to its UP state within a defined time",
                     "The DieBlock not able to reached to its DOWN state within a defined time",
                     "The IX2 Gripper not able to reached to its CLOSED state within a defined time",
                     "The IX2 Gripper not able to reached to its OPENED state within a defined time",
                     "The IX2 Upper Jaw not able to reached to its UP state within a defined time",
                     "The IX2 Upper Jaw not able to reached to its DOWN state within a defined time",
                     "The RejectModule failed to generate index mapping due to several parameter failures",
                     "The RejectModule failed to query indexing data due to several parameter failures",
                     "The RejectModule failed to query reject position data due to several parameter failures",
                     "There is no LF detected at the input track when the IX2 will about to pick a LF",
                     "There is a LF detected at the input track of the RejectModule",
                     "There is a LF detected at the output track of the RejectModule",
                     "There is a jammed LF detected by the AUX2 encoder",
                     "The RejectModule is still not completed its sequence",
                     "The vauum leak is detected at DisposalStation of the RejectModule",
                     "The Puncher is at its UP position state",
                     "The DieBlock is at its DOWN state", "The DieBlock is at its UP state",
                     "The overtravel sensor at RMZ is triggered", "RM Curtain Sensor is blocked",
                     "RM Curtain Sensor FAIL signal is triggered",
                     "The IX2 Lower Jaw not able to reached to its UP state within a defined time",
                     "The IX2 Lower Jaw not able to reached to its DOWN state within a defined time",
                     "The Frame Clamper not able to reached to its DOWN state within a defined time",
                     "The Frame Clamper not able to reached to its UP state within a defined time",
                     "The Wire Clamper not able to reached to its DOWN state within a defined time",
                     "The Wire Clamper not able to reached to its UP state within a defined time",
                     "The Disposal Bin not able to reached to its RETRACTED state within a defined time",
                     "The Disposal Bin not able to reached to its EXTENDED state within a defined time",
                     "The Engraver not able to reached to its DOWN state within a defined time",
                     "The Engraver not able to reached to its UP state within a defined time",
                     "Not able  to detect the Engraver Vacuum within a defined time",
                     "Not able  to detect the Disposal Vacuum within a defined time",
                     "RM ITW move timeout", "RM IX2 move timeout", "RM RMY move timeout",
                     "RM RMYx move timeout", "RM RMYy move timeout", "RM RMYz move timeout", "RM RMYt move timeout",
                     "RM ITW move timeout", "RM IX2 move timeout", "RM RMY move timeout", "RM RMYx move timeout",
                     "RM RMYy move timeout", "RM RMYz move timeout", "RM RMYt move timeout",
                     "RM Wrong Puncher Tool Detected",
                     "RM Rotate To Angle0 Timeout", "RM Rotate To Angle90 Timeout", "RMX Motor Error",
                     "RMX Move Timeout",
                     "RMZ Motor Error", "RMZ Move Timeout", "RM Picker Down Timeout", "RM Picker Up Timeout",
                     "RM Pusher Down Timeout",
                     "RM Pusher Up Timeout", "RM Bent Frame Detected", "RM LMZ Motor Error", "RM LMZ Move Timeout",
                     "RM Laser Mark Command Error", "RM Wire Clamper Close Timeout", "RM Wire Clamper Open Timeout",
                     "RM Laser Fan Not Detected", "RM Failed To Get Units For Reject",
                     "RM Laser Module Not In Safe Mode",
                     "RM Laser Module In Safe Mode", "RM Dustbin Not Present", "RM Timeout Waiting For Disposal",
                     "RM CAMY motor error", "RM CAMY move timeout", "RM Kicker Top LF Present",
                     "RM Protrude LF Not Present",
                     "RM Kicker Down Timeout", "RM Kicker Up Timeout", "RM Kicker Extend Timeout",
                     "RM Kicker Retract Timeout", "RM Displacement sensor is not yet initialized.",
                     "RM Displacement sensor has empty data."],
              "SECSGEM": ["SECSGEM client is null", "SECSGEM is not enabled", "SECSGEM is not in connected state",
                          "SECSGEM is not initialized", "Machine received inproper S14F2 from host. "],
              "STRIPMAP": ["Failed to download strip map", "Wait for request map timeout",
                           "Wait for upload map timeout",
                           "Mismatch strip id", "Null or empty map from host", "Null or empty map from equipment",
                           "Null or empty StripId from host", "Null or empty StripId from equipment",
                           "Duplicate map detected",
                           "No enabled units", "Failed to upload strip map", "Stripmap client is null",
                           "Stripmap is not enabled", "Incorrect strip map information", "Failed to request stripmap",
                           "The equipment received ACK which is not in U1 format",
                           "The equipment received map which is not in Ascii format",
                           "The downloaded map has ACK not equal to 0", "The uploaded map has ACK not equal to 0"],
              "VISION": ["Unable to complete multi-object data storage", "Result for multi-object is missing",
                         "Mismatch multi-object in motion/vision", "ailed to cut dies",
                         "Duplicate Position Data From Indexer",
                         "Failed to find dies", "PPI fail check", "OCR fail check", "2D fail check",
                         "Camera exposure timeout"],
              "VM": ["The IX1 motor is within the critical positions when the CenterTrackY will about to move",
                     "The CenterTrackY is not inline with the side tracks when the IX1 with LF will about the enter the CenterTrack",
                     "The IndexerModule failed to generate index mapping due to several parameter failures",
                     "Prepick-up parameter value may hit the negative limit of the IX1",
                     "There is no LF detected at the input track when the IX1 will about to pick a LF",
                     "There is no LF detected at the input track when the IX1 will about to pick a LF",
                     "There is a LF detected at the input track",
                     "There is a LF detected at the IndexerModule output track",
                     "There is a LF detected by the CenterTrack overtravel sensor",
                     "There is a LF detected by the CenterTrack undertravel sensor",
                     "There is no LF detected at the input track when the IX1 will about to pick a LF",
                     "There is a collision detected between CenterTrack and Backlight",
                     "There is a collision detected between CenterTrack and SideTrack",
                     "Timeout waiting for IX1 gripper close status", "Timeout waiting for IX1 gripper open status",
                     "Timeout waiting for track2 clamper close status",
                     "Timeout waiting for track2 clamper open status",
                     "Timeout waiting while the camera is being switch to different magnification type",
                     "Timeout waiting while the camera is being switch to different angle type",
                     "There is LF jammed detected at indexer track", "Track2Y is not in-line with the track1",
                     "VM VH Position Ready Sensor Not Detected", "VM IX1 move timeout", "VM VHX move timeout",
                     "VM VHY move timeout", "VM VHZ move timeout", "VM Tr2Y move timeout", "VM Tr1W move timeout",
                     "VM Tr2W move timeout", "VM VHZSubM move timeout", "VM VHZSubA move timeout",
                     "VM VHZSubB move timeout",
                     "VM VHZSubC move timeout", "VM VHZSubD move timeout", "VM IX1 motor error", "VM VHX motor error",
                     "VM VHY motor error", "VM VHZ motor error", "VM Tr2Y motor error", "VM Tr1W motor error",
                     "VM Tr2W motor error", "VM VHZSubM motor error", "VM VHZSubA motor error",
                     "VM VHZSubB motor error",
                     "VM VHZSubC motor error", "VM VHZSubD motor error", "VM Vacuum Pad Down Timeout",
                     "VM Vacuum Pad Up Timeout",
                     "VM Vacuum Pad Leak Detected", "VM Unload Kicker Timeout",
                     "VM Displacement sensor is not yet initialized",
                     "VM Dispalacement sensor has empty data.", "VM Displacement sensor reading timeout."]}

# -------------- STREAMLIT CODE -------------------
from ipyvizzu import Chart, Data, Config, Style, DisplayTarget
from streamlit.components.v1 import html
from streamlit_dynamic_filters import DynamicFilters
from ipyvizzustory import Story, Slide, Step
from streamlit_vizzu import VizzuChart, Data, Config, Style
from streamlit_option_menu import option_menu

st.markdown(":violet[ **INSiG brings in :green[automated] analysis and insights from AOI Log Data . "
            "Check out the :blue[features] and filters to seamlessly obtain :red[insights] for swift decision making, :orange[quick] output response and "
            ":rainbow[Data driven] development**]")

custom_rainbow_divider()

# display the IFX digital agenda
st.markdown(":green[ **INSiG syncs with Infineon's Digital Agenda. Check out Infineon Digital 2030 (ID2030) below.** ]")
st.page_link("https://intranet-content.infineon.com/explore/aboutinfineon/digitaltransformation/Pages/index_en.aspx",
             label="**IFX ID2030**", icon="🌐")

st.subheader("🎞️Dev-AOI Log viewer", divider='rainbow')


# Open and parse defect summary data for Story visualization

def clear_cache():
    keys = list(st.session_state.keys())
    for key in keys:
        st.session_state.pop(key)


# create a dataframe for AOI alarms

alarm_df = pd.DataFrame.from_dict(alarm_dict, orient='index')
alarm_df = alarm_df.transpose()

#  options forDynaminc filters
# view critical alarm list per module

button_alarm = st.toggle(":green[Activate to Option to view Critical Alarm list per module in AOI]🗓️")

if button_alarm:
    module_alarm_options = alarm_df.columns
    module_alarm = st.pills('Select Module', module_alarm_options, selection_mode="single")
    if module_alarm == None:
        pass
    else:
        st.dataframe(alarm_df[module_alarm])


# filters for machine and module to select the combined zip log
# select machine
st.subheader("Select the Machine to explore Log Data", divider='rainbow')
mc_options = ['FAVE104', 'FAVE112','FAVE113', 'FAVE118', 'FAVE119', 'FAVE120', 'FAVE121', 'FAVM205', 'FAVM206', 'FAVM212']
selected_machine = st.pills('Select Machine', mc_options, selection_mode="single")
st.markdown(f"Your selected options: {selected_machine}.")

# select module
st.subheader("Select the Module under the machine to view Log Data", divider='rainbow')
module_options = ["IMH", "OMH", "MOTIONMANAGER", "MOTIONUI", "INDEXER",
                  "SECSGEM", "STRIPMAP", "VISION", "VM", "RM", "MAIN", "COMMON"]
module_option = st.pills('Select Module', module_options, selection_mode="single")
st.markdown(f"Your selected options: {module_option}.")

# Static Folder for flask
dest = r'static/'
# from streamlit_autorefresh import st_autorefresh
# update every 5 mins
# t_autorefresh(interval=1 * 1 * 1000, key="dataframerefresh")

# selected_machine = option_menu("Select the Machine to explore the logs",
#                               ['FAVE104', 'FAVE118','FAVE119','FAVE120', 'FAVE121'],
#        icons=['house', 'gear'], menu_icon="cast", default_index=0,orientation="horizontal")

    # module_date_file = open(module_option + '_' + 'date_file.csv', "wb")
    # retrieve the module_date_list csv file
    # retrieve the file from server name, join path for foldernames and filenames and write to the destination ( static folder)
    #res3_attributes, res3size = conn.retrieveFile(shareName,
     #                                             os.path.join(folderName, selected_machine,
     #                                                          module_option, 'date_list.csv'),
     #                                             module_date_file)

    # display the selected module's date list as a drop down list at sidebar
    # open the date file as a dataframe
    #df_date_file = pd.read_csv(module_option + '_' + 'date_file.csv', encoding='unicode_escape')
    #date_list_display = df_date_file['shortlisted_date'].tolist()
    #print(date_list_display)
    #date_option = st.selectbox(
    #    "Select the required date", ('01-23','01-24','01-25','01-27'))

if module_option == None or selected_machine == None:
    st.write('Use filters to select an AOI machine/Module to explore the logs')

else:
    print("selected machine is ", selected_machine)
    print("selected module is ", module_option)

    # Start-End Date Selection
    custom_rainbow_divider()
    st.markdown(":green[ **Select the date range to display Tabulated Log Data for {} under {}**]".format(module_option, selected_machine))
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", date.today() - timedelta(days=7)) 
    with col2:
        end_date = st.date_input("End Date", date.today())  


#Retrieve the file from server name, join path for foldernames and filenames and write to the destination (static folder)

    if start_date > end_date:
        st.error("Start date must be before end date. Please select again.")
    else:
        try:
            module_folder = os.path.join(local_base_path, selected_machine, module_option)
            all_files = [f for f in os.listdir(module_folder) if f.endswith('.csv')]
            
            if not all_files:
                st.error("No CSV files found in the local folder.")
            else:
            # Filter file based on date range
                date_pattern = '%m-%d'  
                valid_files = []
                current_year = end_date.year  
                for file in all_files:
                    try:
                        file_date_str = file.split('.')[0]  
                        file_date_obj = dt.strptime(file_date_str, date_pattern)  # Parse as datetime (e.g. 01-23)
                        file_date_full = file_date_obj.replace(year=current_year)  
                        file_date = file_date_full.date() 
                        
                        
                        if start_date <= file_date <= end_date:
                            valid_files.append(os.path.join(module_folder, file))
                    except ValueError:
                        st.write(f"File {file} date format not correct, skipped.")  # Debugging
                        continue
                
                if not valid_files:
                    st.info(":red[No log data available in the selected date range for the Machine+Module combination]")
                else:
                    df_log_module = pd.DataFrame()
                    for file_path in valid_files:
                        try:
                            df_temp = pd.read_csv(file_path, encoding='unicode_escape')
                            
                            if 'Unnamed: 0' in df_temp.columns:
                                df_temp = df_temp.drop(columns=['Unnamed: 0'])
                            
                            # Rename column
                            if len(df_temp.columns) >= 3: 
                                df_temp.rename(columns={'0': 'Date', '1': 'Timestamp', '2': 'log_entry'}, inplace=True)
                            else:
                                st.error(f"File {file_path} does not have enough columns. Skip this file.")
                                continue  
                            
                            df_log_module = pd.concat([df_log_module, df_temp], ignore_index=True)

                        except Exception as e:
                            st.error(f"Error membaca file {file_path}: {str(e)}")
                    
                    if df_log_module.empty:
                        st.info(":red[No log data available after filtering]")
                    else:
                        st.markdown(":green[ **Search for AOI Alarms in the below Tabulated Log Data for {} under {}**] ".format(module_option, selected_machine))
                        
                    # Display dynamincally filtered dataframe
                        dynamic_filters_module = DynamicFilters(df_log_module, filters=['Date', 'Timestamp', 'log_entry'])
                        dynamic_filters_module.display_filters(location='columns', num_columns=3, gap='large')
                        dynamic_filters_module.display_df()
                        
                        custom_rainbow_divider()
                        st.markdown(":green[**Dynamic Visualizations on the Filtered Log Data.**]")
                        
                    try:
                        st.info(":red[If critical alarms occured on the selected date, it will be plotted below. Count of Critical Alarms occured and captured in Module Log]")
                        generic_plot = df_log_module.loc[df_log_module['log_entry'].isin(alarm_dict[module_option]), 'log_entry'].value_counts().to_frame().reset_index()
                        print(generic_plot)
                    except KeyError:
                        st.info(":red[Critical Alarms not found]")
                        
                    # Visualisations on Filtered Dataframe
                     
                    filtered_module = dynamic_filters_module.filter_df()
                    print(filtered_module)
                    print(type(filtered_module))
                    print(filtered_module.shape)
                    add_vertical_space(2)

                # ---- perform custom visualizations
                # # Bar chart on Filtered / selected log events
                st.write(":green[**Count of Selected/ filtered Log events**]")
                tempdf = filtered_module.groupby("log_entry")["Date"].count()
                print(tempdf)
                st.bar_chart(tempdf)
                add_vertical_space(2)
                
                # Bar chart to show count of events by date
                st.write(":green[**Count of Selected/ filtered Log events by Date**]")
                tempdf = filtered_module.groupby("Date")["log_entry"].count()
                print(tempdf)
                st.bar_chart(tempdf)
                add_vertical_space(2)
                
                # use matplotlib charts
                st.write(":green[**Top ten logged events**]")
                import matplotlib.pyplot as plt
                from matplotlib.ticker import PercentFormatter
                
                pareto_filter = alarmpareto(filtered_module, "log_entry", "Date", "Count of Alarms", "Pareto")
                st.pyplot(pareto_filter.gcf())
                add_vertical_space(2)

        except Exception as e:
            st.error(f"Error: {str(e)}.Unhandled error, please inform Admin")
        except OperationFailure:
            st.info(":red[No log data available for the Machine+Module combination]")
        except TypeError:
            st.info(":red[Encoding Error in Dataframe, please inform admin to re encode log data source file]")
        except EmptyDataError:
            st.info(":red[No log data available for the Machine+Module combination]")



    # on = st.toggle("Activate to Query the Module Data by Date🗓️")
    # df_log_module['Date'] =  pd.to_datetime(df_log_module['Date'], format='%d-%m')
    # print((df_log_module['Date']).dtype)
    # https://stackoverflow.com/questions/57061645/why-is-%C3%82-printed-in-front-of-%C2%B1-when-code-is-run

# dynamic visualisations for the content of selected module
# https://dynamic-filters-demo.streamlit.app/Columns_Example_Hierarchical

# total errors per week?
# modules with high errors
# pivot chart
