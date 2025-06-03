# Wind Rose Generator

A Python-based application for generating and analyzing wind rose diagrams from meteorological data. This tool provides an intuitive graphical interface for visualizing wind patterns and exporting the results in various formats.

## Features

- Interactive GUI built with PyQt5
- Load and process wind data from Excel files
- Customizable wind direction bins (4-36 sectors)
- Adjustable wind speed categories (2-10 ranges)
- Date range filtering
- Real-time wind rose visualization
- Export capabilities:
  - Wind rose image
  - Frequency table
  - XML data format

## Requirements

- Python 3.x
- PyQt5
- pandas
- numpy
- matplotlib

## Installation

1. Clone this repository
2. Install the required dependencies:
```bash
pip install PyQt5 pandas numpy matplotlib
```

## Usage

1. Run the application:
```bash
python main.py
```

2. Load your wind data:
   - Click "Load Excel File" to select your data file
   - Configure the data columns (date/time, wind speed, wind direction)
   - Set the appropriate date format

3. Customize the visualization:
   - Adjust the number of direction bins
   - Modify wind speed categories
   - Select the desired date range

4. Generate and export:
   - Click "Update Wind Rose" to refresh the visualization
   - Use the export buttons to save the results in your preferred format

## Data Format

The application expects Excel files with the following columns:
- Date/Time column
- Wind Speed column (in m/s)
- Wind Direction column (in degrees)

## License

This project is open source and available under the MIT License. 