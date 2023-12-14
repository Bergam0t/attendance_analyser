A small streamlit app for analysing Zoom meeting logs.

These are the logs that are accessed from the Zoom website by going to Reports --> Usage Reports --> Usage.

Click on the Number of Participants - this should be in blue, and is actually a hyperlink - and will bring up a window that allows you to export the log as a csv.

![image](https://github.com/Bergam0t/attendance_analyser/assets/29951987/adba9b4c-6b27-4393-8c63-6eae3ca9f85a)

The app will process the file to generate graphs and summary metrics. 



Deployed as a serverless on github pages using the stlite package, so all processing will take place in the browser.

Concept inspired by the work done by the strategy unit in [this repository](https://github.com/The-Strategy-Unit/WebinarStats)
