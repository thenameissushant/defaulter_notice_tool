# EMI Defaulter Segmentation & Legal Notice Generator

A small Python tool that reads a monthly loan data file (Excel), finds customers who have missed their EMIs, sorts them into stages, and creates a legal notice in Word for each one.

I built the original version of this idea at work to save the manual effort of preparing notices every month. This public version uses **only made-up sample data** and a **generic notice template** that I wrote myself.

## The problem

Every month, the team had to:
1. Go through a large data dump and find customers who missed payments.
2. Separate those who missed their 1st/2nd EMI from those who missed their 3rd EMI.
3. Prepare a separate legal notice for each customer.

Doing this by hand for 1,500-2,000 accounts takes a lot of time and is easy to get wrong.

## What the tool does

- Reads the Excel file you select
- Splits customers into two groups:
  - **Stage 1:** missed 1st or 2nd EMI
  - **Stage 2:** missed 3rd EMI
- Fills a Word notice template with each customer's details
- Saves all notices in an output folder, ready to review and print

## Built with

- Python
- Pandas (data handling)
- python-docx (creating Word notices)
- [Streamlit / Tkinter - write the one you used] (user interface)

## How to run it

1. Install Python 3.9 or newer.
2. Download this project and open the folder in a terminal.
3. Install the libraries:
   ```
   pip install -r requirements.txt
   ```
4. Start the app:
   ```
   [streamlit run app.py   OR   python app.py]
   ```
5. Choose `sample_data/sample_dump.xlsx` and click the button to generate notices.

## Project structure

```
.
├── app.py                  # user interface
├── [your_logic_file].py    # segmentation + notice generation
├── requirements.txt
├── sample_data/
│   └── sample_dump.xlsx    # fake data for testing
└── sample_output/
    └── example_notice.docx # an example generated notice
``
## Note on data

All names, loan numbers and amounts in `sample_data` are fictional. No real customer or company data is included in this repository.

## Possible improvements

- Support for more notice types
- A summary report of how many customers fall in each stage
- Handling larger files (5,000+ records) faster

## Author

Sushant Jha - Data & MIS Analyst
[https://www.linkedin.com/in/thenameissushant/]
