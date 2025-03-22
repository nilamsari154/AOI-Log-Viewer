import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.colored_header import colored_header
import os

st.set_page_config(page_title="DEV Dashboard", page_icon=":computer:")

def dashboard_page():
    colored_header(
        label="Welcome to Dashboard",
        description="Quick access to important tools",
        color_name="blue-30",
    )
    add_vertical_space(2)
    num_cols = 3
    link_items = list(links.items())
    num_rows = (len(link_items) + num_cols - 1) // num_cols

    for i in range(num_rows):
        cols = st.columns(num_cols, gap="large")
        for j in range(num_cols):
            index = i * num_cols + j
            if index < len(link_items):
                name, data = link_items[index]
                link = data["link"]
                icon = data["icon"]
                cols[j].markdown(f'''
                    <a href="{link}" style="text-decoration: none;">
                        <button style="background-color:#09C6B5; color:white; border: 1px white solid; border-radius: 8px; padding: 15px 25px; font-size: 18px; display: flex; align-items: center; justify-content: center; width: 100%; height: 100px;">
                            <i class="fa fa-{icon}" style="margin-right: 10px;"></i> {name}
                        </button>
                    </a>
                ''', unsafe_allow_html=True)
                cols[j].markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">', unsafe_allow_html=True)

links = {
    "PICTURE VIEWER": {"link": "https://pictureviewer-bedev.infineon.com:8080/viewpictures", "icon": "image"},
    "CAMSTAR": {"link": "https://opcenter.bth.infineon.com/OpcenterPortal/default.htm#/login", "icon": "database"},
    "KLUSA": {"link": "https://klusa4.intra.infineon.com/klusa_ifx_projects/klusaweb/", "icon": "code"},
    "DEVSMETS": {"link": "https://jiradc.intra.infineon.com/secure/Dashboard.jspa", "icon": "calendar"},
    "PROJECT DOCUMENT": {"link": "https://ishare.infineon.com/sites/BE_DEV_PO/SitePages/Assembly%20Development.aspx", "icon": "folder"},
    "OE APPLICATION": {"link": "https://oe.bth.infineon.com/", "icon": "gear"},
    "PBHB": {"link": "https://intranet-content.infineon.com/explore/operations/TechnologyExcellence/ComplexityManagement/ProcessBlockCatalogPBC/Pages/index_en.aspx", "icon": "book"},
    "NICA": {"link": "https://nica.icp.infineon.com/en/search", "icon": "search"},
    "TBD VIEWER": {"link": "http://tbdviewer.rbg.infineon.com/", "icon": "eye"},
    "IFBT DEV SYSTEM": {"link": "file://sinsdv020.ap.infineon.com/Dev/09_Section_Process/01_FOL_Folder/01_Process/04.%20Wirebond/21.Spare%20Part%20Data%20Base%20System/IFBT_DEV_Spare_Part/Index.html", "icon": "server"},
    "HALO": {"link": "https://halo-cecipr.ap-sg-1.icp.infineon.com/", "icon": "globe"},
    "PDR+": {"link": "https://pdr-plus-prd.icp.infineon.com/", "icon": "plus-square"}
}

#------------------------Data System Monitoring----------------------------------------
month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

image_dict = {
    "DEVSPACE": {
        year: {
            month: f"DEVSPACE_{month_names[month-1]}_{year}.jpg"
            for month in range(1, 13)
        }
        for year in range(2023, 2026)
    },
    "NICA": {
        year: {
            month: f"NICA_{month_names[month-1]}_{year}.jpg"
            for month in range(1, 13)
        }
        for year in range(2023, 2026)
    },
    "PV": {
        year: {
            month: f"PV_{month_names[month-1]}_{year}.jpg"
            for month in range(1, 13)
        }
        for year in range(2023, 2026)
    }
}

def download_image_button(image_path, button_text, logo_path="logo.png"): # Tambahkan logo_path
    """Membuat tombol unduh gambar dengan logo."""
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()
    encoded_image = base64.b64encode(image_bytes).decode()
    href = f'<a href="data:image/jpeg;base64,{encoded_image}" download="{os.path.basename(image_path)}"><button class="download-button" title="Unduh gambar ini"><img src="{logo_path}" alt="Logo" class="logo"> {button_text}</button></a>'
    return href

def data_system_monitoring_page():
    st.title("Data System Monitoring")
    st.write("This page displays system monitoring data in monthly report. Select a year and month to view the available monitoring images.")

    report_year, report_month = show_report_month()

    data_sources = ["DEVSPACE", "NICA", "PV"]

    for data_source in data_sources:
        st.subheader(f"Data {data_source}")
        if data_source in image_dict and report_year in image_dict[data_source] and report_month in image_dict[data_source][report_year]:
            image_path = image_dict[data_source][report_year][report_month]
            if image_path and os.path.exists(image_path):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.image(image_path, caption=f"{data_source} - {report_year} - {report_month:02d}", use_container_width=True)
                with col2:
                    st.markdown(download_image_button(image_path, f"Download {data_source}"), unsafe_allow_html=True)
            elif image_path:
                st.error(f"Image '{image_path}' not found.")
            else:
                st.warning(f"Image for {data_source} - {report_month:02d} - {report_year} is not available.")
        else:
            st.error(f"No images available for {data_source}, {report_year}, and {report_month}.")

def show_report_month():
    this_year = datetime.now().year
    this_month = datetime.now().month
    report_year = st.selectbox("Select Year", range(this_year, this_year - 3, -1))
    report_month_str = st.radio("Select Month", month_names, index=this_month - 1, horizontal=True)
    report_month = month_names.index(report_month_str) + 1
    return report_year, report_month

# CSS kustom
st.markdown(
    """
    <style>
    .download-button {
        background-color: #4CAF50;
        border: none;
        color: white;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
    }
    .download-button:hover {
        background-color: #3e8e41;
    }
    .logo {
        height: 20px;
        margin-right: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

#------------------------DEV Training---------------------------------------------------------
def training_page():
    st.header("Training Resources")
    training_links = {
        "Success Factor": "https://infineon.plateau.com/learning",
        "Linkedin Learning": "https://www.linkedin.com/learning/",
        "UPD Training Document (PPT)": "C:/Users/SarSitiHanaf/Desktop/PROJECT/DEV DAHSBOARD/training_ppt.ppt"
    }
    def create_link_buttons(col, links):
        for name, link in links.items():
            if link.startswith("http"):
                col.markdown(f'''
                    <a href="{link}"><button style="background-color:#09C6B5; color:white; border: 1px white solid; border-radius: 5px; width: 200px; height: 100px; font-size: 20px;">{name}</button></a>
                ''', unsafe_allow_html=True)
            else:
                col.markdown(f'''
                    <button style="background-color:#09C6B5; color:white; border: 1px white solid; border-radius: 5px; width: 200px; height: 100px; font-size: 20px;" onclick="download_file('{link}')">{name}</button>
                ''', unsafe_allow_html=True)
    def download_file(file_url):
        import requests
        response = requests.get(file_url, stream=True)
        filename = file_url.split("/")[-1]
        if response.status_code == 200:
            st.success(f"Downloading {filename}...")
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            st.success(f"Download complete! {filename} is saved locally.")
        else:
            st.error(f"Failed to download {filename}. Error code: {response.status_code}")
    create_link_buttons(st.container(), training_links)

def dev_tools_page():
    st.header("Dev Tools")
    st.write("This is Dev Tools Page")


pages = {
    "Dashboard": dashboard_page,
    "Data System Monitoring": data_system_monitoring_page,
    "Training": training_page,
    "Dev Tools": dev_tools_page,
}

st.sidebar.title("People Dashboard")
with st.sidebar:
    selected_dash = option_menu(
        menu_title=None,
        options=list(pages.keys()),
        icons=["speedometer", "database", "universal-access", "wrench"],
        menu_icon="speedometer",
        default_index=0
    )

pages[selected_dash]()