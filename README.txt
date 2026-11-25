FOOD DELIVERY PROJECT - HOW TO RUN

1. Install MySQL and keep it running (user: root, port: 3306).
2. Open a terminal INSIDE the MajorProject folder (the folder that has main.py, dataset and SQL).
3. Install the libraries (only the first time):
       pip install -r requirements.txt
4. Run the project:
       python main.py
   Press Enter to run all the steps, then type the MySQL password when asked.
   At the end you should see: All selected steps finished.

Notes
- If you use Spyder or Jupyter, restart the console/kernel before running again.
- The program can be run again and again, it removes the old MySQL tables by itself.
- Charts are saved in eda_charts, statistics_charts and regression_charts.
