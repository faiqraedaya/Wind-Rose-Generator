import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QPushButton, QSpinBox, QLabel, QDateTimeEdit, QGroupBox, QMessageBox, QComboBox, QMenuBar, QMenu, QAction)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from datetime import datetime
import xml.etree.ElementTree as ET

from ui.speed_range_widget import SpeedRangeWidget
from ui.data_config_widget import DataConfigWidget

class WindRoseApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Wind Rose Analyzer')
        self.setGeometry(100, 100, 1200, 800)
        # Define default colors to match the image
        self.default_colors = ['blue', 'cyan', 'lightgreen', 'yellow', 'red', 'darkred']
        
        # Create menu bar
        self.create_menu_bar()
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        # Control panel
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)

        # Data configuration group
        data_config_group = QGroupBox('Data Configuration')
        self.data_config = DataConfigWidget()
        data_config_layout = QVBoxLayout()
        data_config_layout.addWidget(self.data_config)
        data_config_group.setLayout(data_config_layout)
        control_layout.addWidget(data_config_group)

        # Direction bins control
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel('Direction Bins:'))
        self.dir_bins = QSpinBox()
        self.dir_bins.setRange(4, 36)
        self.dir_bins.setValue(16)
        dir_layout.addWidget(self.dir_bins)
        control_layout.addLayout(dir_layout)

        # Number of speed categories control
        speed_cat_layout = QHBoxLayout()
        speed_cat_layout.addWidget(QLabel('Number of Speed Categories:'))
        self.num_speed_cats = QSpinBox()
        self.num_speed_cats.setRange(2, 10)
        self.num_speed_cats.setValue(6)
        self.num_speed_cats.valueChanged.connect(self.update_speed_categories)
        speed_cat_layout.addWidget(self.num_speed_cats)
        control_layout.addLayout(speed_cat_layout)

        # Wind speed categories group
        self.speed_group = QGroupBox('Wind Speed Categories (m/s)')
        self.speed_layout = QVBoxLayout()
        self.speed_group.setLayout(self.speed_layout)
        control_layout.addWidget(self.speed_group)

        # Initialize speed range widgets
        self.speed_ranges = []
        self.setup_default_ranges()

        # Date range selection group
        date_group = QGroupBox('Date Range')
        date_layout = QVBoxLayout()
        self.start_date = QDateTimeEdit()
        self.end_date = QDateTimeEdit()
        self.start_date.setDisplayFormat("yyyy-MM-dd HH:mm:ss") 
        self.end_date.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        date_layout.addWidget(QLabel('Start:'))
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(QLabel('End:'))
        date_layout.addWidget(self.end_date)
        date_group.setLayout(date_layout)
        control_layout.addWidget(date_group)

        # Update and Export buttons
        self.update_button = QPushButton('Update Wind Rose')
        self.update_button.clicked.connect(self.update_wind_rose)
        control_layout.addWidget(self.update_button)

        # Add control panel to main layout
        layout.addWidget(control_panel, stretch=1)
        # Matplotlib figure
        self.figure = Figure(figsize=(8, 8))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas, stretch=3)
        self.data = None
        self.csvdata = None
        self.raw_data = None
        self.current_filename = "Unknown File"

    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu('File')
        
        new_action = QAction('New', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction('Open Excel File', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.load_excel)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Export Menu
        export_menu = menubar.addMenu('Export')
        
        export_image_action = QAction('Export Wind Rose Image', self)
        export_image_action.triggered.connect(self.export_image)
        export_menu.addAction(export_image_action)
        
        export_table_action = QAction('Export Wind Rose Table', self)
        export_table_action.triggered.connect(self.export_table)
        export_menu.addAction(export_table_action)
        
        export_xml_action = QAction('Export Wind Rose XML', self)
        export_xml_action.triggered.connect(self.export_XML)
        export_menu.addAction(export_xml_action)
        
        # Help Menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        help_action = QAction('Help', self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

    def new_file(self):
        # Reset the application state
        self.raw_data = None
        self.data = None
        self.csvdata = None
        self.current_filename = "Unknown File"
        self.figure.clear()
        self.canvas.draw()
        
        # Reset date range to current date
        current_date = datetime.now()
        self.start_date.setDateTime(current_date)
        self.end_date.setDateTime(current_date)

    def show_about(self):
        QMessageBox.about(self, "About Wind Rose Generator",
                         "Wind Rose Generator\n\n"
                         "Simple tool for generating wind roses.\n"
                         "Version 1.0\n\n"
                         "© Faiq Raedaya 2025")

    def show_help(self):
        help_text = """
        <h3>Wind Rose Generator Help</h3>
        
        <p><b>Loading Data:</b><br>
        - Use File > Open Excel File to load your wind data<br>
        - Ensure your Excel file has columns for date/time, wind speed, and wind direction</p>
        
        <p><b>Configuring the Display:</b><br>
        - Adjust the number of direction bins (4-36)<br>
        - Set the number of speed categories (2-10)<br>
        - Configure speed ranges for each category</p>
        
        <p><b>Exporting Results:</b><br>
        - Export the wind rose as an image (PNG/JPEG)<br>
        - Export the frequency table as Excel<br>
        - Export the data in XML format</p>
        
        <p><b>Date Range:</b><br>
        - Select the start and end dates to analyze specific time periods</p>
        """
        QMessageBox.information(self, "Help", help_text)

    def setup_default_ranges(self):
        for widget in self.speed_ranges:
            widget.deleteLater()
        self.speed_ranges.clear()
        default_values = [
            (2, 4.9),
            (5, 6.9),
            (7, 9.9),
            (10, 14.9),
            (15, 19.9),
            (20, 100)
        ]
        num_categories = self.num_speed_cats.value()
        for i in range(num_categories):
            range_widget = SpeedRangeWidget()
            if i < len(default_values):
                range_widget.min_speed.setValue(default_values[i][0])
                range_widget.max_speed.setValue(default_values[i][1])
            else:
                prev_max = self.speed_ranges[-1].max_speed.value()
                range_widget.min_speed.setValue(prev_max)
                range_widget.max_speed.setValue(prev_max + 5)
            self.speed_layout.addWidget(range_widget)
            self.speed_ranges.append(range_widget)

    def update_speed_categories(self):
        self.setup_default_ranges()

    def process_data(self):
        if self.raw_data is None:
            return None
        try:
            date_time_col = self.data_config.date_time_col.text()
            wind_speed_col = self.data_config.wind_speed_col.text()
            wind_dir_col = self.data_config.wind_dir_col.text()
            first_row = self.data_config.first_row.value()
            last_row = self.data_config.last_row.value()
            if last_row == 0:
                df = self.raw_data.iloc[first_row:].copy()
            else:
                df = self.raw_data.iloc[first_row:last_row+1].copy()
            required_cols = [date_time_col, wind_speed_col, wind_dir_col]
            for col in required_cols:
                if col not in df.columns:
                    QMessageBox.critical(self, "Error", f"Column '{col}' not found in the data.")
                    return None
            date_format = self.data_config.date_format.text()
            py_date_format = date_format.replace('yyyy', '%Y').replace('MM', '%m').replace('dd', '%d')
            py_date_format = py_date_format.replace('HH', '%H').replace('mm', '%M').replace('ss', '%S')
            try:
                if isinstance(df[date_time_col].iloc[0], str):
                    df['Date & Time'] = pd.to_datetime(df[date_time_col], format=py_date_format)
                else:
                    df['Date & Time'] = df[date_time_col]
            except Exception as e:
                QMessageBox.critical(self, "Date Format Error", \
                                    f"Could not parse dates with format '{date_format}'.\nError: {str(e)}")
                return None
            df['Wind Speed'] = df[wind_speed_col]
            df['Wind Direction'] = df[wind_dir_col]
            return df
        except Exception as e:
            QMessageBox.critical(self, "Data Processing Error", f"Error processing data: {str(e)}")
            return None

    def update_wind_rose(self):
        self.data = self.process_data()
        if self.data is None:
            return
        mask = (self.data['Date & Time'] >= self.start_date.dateTime().toPyDateTime()) & \
            (self.data['Date & Time'] <= self.end_date.dateTime().toPyDateTime())
        filtered_data = self.data[mask]
        self.figure.clear()
        gs = self.figure.add_gridspec(2, 1, height_ratios=[4, 1])
        self.ax = self.figure.add_subplot(gs[0], projection='polar')
        dir_bins = np.linspace(0, 360, self.dir_bins.value() + 1)
        dir_centers = dir_bins[:-1] + np.diff(dir_bins) / 2
        dir_radians = np.radians(dir_centers)
        bottom = np.zeros(len(dir_centers))
        total_hist = np.zeros(len(dir_centers))
        for i, range_widget in enumerate(self.speed_ranges):
            min_speed = range_widget.min_speed.value()
            max_speed = range_widget.max_speed.value()
            mask = (filtered_data['Wind Speed'] >= min_speed) & \
                (filtered_data['Wind Speed'] <= max_speed)
            speeds = filtered_data[mask]['Wind Direction']
            hist, _ = np.histogram(speeds, bins=dir_bins)
            hist = hist / len(filtered_data) * 100
            total_hist += hist
            label = f'{min_speed:.1f}-{max_speed:.1f}' if max_speed < 100 else f'{min_speed:.1f}+'
            color = self.default_colors[i] if i < len(self.default_colors) else None
            self.ax.bar(dir_radians, hist, width=np.radians(360/self.dir_bins.value()),
                    bottom=bottom, label=f'{label} m/s', color=color)
            bottom += hist
        self.ax.set_theta_direction(-1)
        self.ax.set_theta_zero_location('N')
        self.ax.set_title('Wind Rose Diagram')
        self.ax.legend(bbox_to_anchor=(1.2, 0.5), loc='center left')
        wind_speeds = filtered_data['Wind Speed']
        avg_speed = wind_speeds.mean()
        prevailing_dir_idx = np.argmax(total_hist)
        prevailing_dir = dir_centers[prevailing_dir_idx]
        ax_text = self.figure.add_subplot(gs[1])
        ax_text.axis('off')
        start_date_str = self.start_date.dateTime().toString('yyyy-MM-dd HH:mm')
        end_date_str = self.end_date.dateTime().toString('yyyy-MM-dd HH:mm')
        filename = self.current_filename
        if '/' in filename:
            filename = filename.split('/')[-1]
        info_text = (
            f"Data Source: {filename}\n"
            f"Date Range: {start_date_str} to {end_date_str}\n"
            f"Prevailing Wind Direction: {prevailing_dir:.1f}°\n"
            f"Average Wind Speed: {avg_speed:.1f} m/s\n"
        )
        ax_text.text(0.05, 0.95, info_text, \
                    transform=ax_text.transAxes,
                    verticalalignment='top',
                    fontfamily='monospace')
        self.figure.tight_layout()
        self.canvas.draw()

    def load_excel(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select Excel file", "", \
                                                "Excel Files (*.xlsx *.xls);;All Files (*)")
        if filename:
            try:
                self.raw_data = pd.read_excel(filename)
                self.current_filename = filename
                self.data = self.process_data()
                if self.data is not None:
                    min_date = self.data['Date & Time'].min()
                    max_date = self.data['Date & Time'].max()
                    self.start_date.setDateTime(min_date)
                    self.end_date.setDateTime(max_date)
                    self.update_wind_rose()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error loading Excel file: {str(e)}")

    def create_frequency_table(self):
        if self.data is None:
            return None
        speed_bins = [0]
        speed_labels = []
        for range_widget in self.speed_ranges:
            speed_bins.append(range_widget.max_speed.value())
            min_val = range_widget.min_speed.value()
            max_val = range_widget.max_speed.value()
            label = f'{min_val}-{max_val}' if max_val < 100 else f'{min_val}+'
            speed_labels.append(label)
        dir_bins = np.linspace(0, 360, self.dir_bins.value() + 1)
        dir_labels = [f"{i:.1f}" for i in dir_bins[:-1]]
        mask = (self.data['Date & Time'] >= self.start_date.dateTime().toPyDateTime()) & \
               (self.data['Date & Time'] <= self.end_date.dateTime().toPyDateTime())
        filtered_data = self.data[mask]
        filtered_data['speed_bin'] = pd.cut(filtered_data['Wind Speed'], 
                                          bins=speed_bins, 
                                          labels=speed_labels, 
                                          include_lowest=True)
        filtered_data['dir_bin'] = pd.cut(filtered_data['Wind Direction'], 
                                         bins=dir_bins, 
                                         labels=dir_labels, 
                                         include_lowest=True)
        index = pd.Index(speed_labels, name='speed_bin')
        columns = pd.Index(dir_labels, name='dir_bin')
        freq_table = pd.DataFrame(0, index=index, columns=columns)
        counts = pd.crosstab(filtered_data['speed_bin'], 
                            filtered_data['dir_bin'], 
                            normalize=True) * 100
        freq_table.update(counts)
        return freq_table

    def export_image(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Wind Rose Image", "",
                                                 "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)")
        if file_path:
            try:
                self.figure.savefig(file_path, dpi=300, bbox_inches='tight')
                QMessageBox.information(self, "Export Successful", f"Image exported to \n{file_path}")
            except Exception as e:
                print(f"Error saving image: {e}")

    def export_table(self):
        freq_table = self.create_frequency_table()
        if freq_table is None:
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Wind Rose Table", "", 
                                                 "Excel Files (*.xlsx);;All Files (*)")
        if file_path:
            freq_table.to_excel(file_path)
            QMessageBox.information(self, "Export Successful", f"Table exported to \n{file_path}")

    def export_XML(self):
        freq_table = self.create_frequency_table()
        if freq_table is None:
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Wind Rose XML", "", 
                                                 "XML Files (*.xml);;All Files (*)")
        if file_path:
            root = ET.Element("Data")
            ET.SubElement(root, "Information").text = "Wind Rose Data"
            ET.SubElement(root, "Name").text = "WindRose"
            velocity_bands = " ".join(str(widget.max_speed.value()) 
                                    for widget in self.speed_ranges)
            ET.SubElement(root, "Velocity_Bands").text = velocity_bands
            headings_probabilities = ET.SubElement(root, "Headings_Probabilities")
            for column in freq_table.columns:
                heading_prob = ET.SubElement(headings_probabilities, "Heading_Probabilities")
                heading_prob.text = " ".join(f"{val/100:.4f}" for val in freq_table[column])
            tree = ET.ElementTree(root)
            tree.write(file_path, xml_declaration=True, encoding='utf-8', method="xml")
            QMessageBox.information(self, "Export Successful", f"XML exported to \n{file_path}") 