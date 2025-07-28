from flask import Flask, render_template, flash, redirect, request, jsonify, url_for, Response, session
# from aquaLite import *
import datetime
import json
import sqlite3
import time
import statistics as stat
import mail
from config import credential
import generator
from flask_toastr import Toastr     # toastr module import
import create_database
from chemical_recommendations import get_chemical_recommendations, get_fish_parameters, fish_parameters


app = Flask(__name__)

# python notification toaster
toastr = Toastr(app)

# Set the secret_key on the application to something unique and secret.
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SESSION_TYPE'] = 'filesystem'


# home route....landing page
@app.route("/", methods = ['GET', 'POST'])
@app.route("/index", methods=["GET", "POST"])
def index():
    print("landing page running...")
    if request.method == 'POST':
        username = request.form['username']
        passwd = request.form['password']

        # credentials from config files imported
        if username == credential['name'] and passwd == credential['passwd']:
            flash('Login successful :)', 'success')
            # flash("You have successfully logged in.", 'success')    # python Toastr uses flash to flash pages
            return redirect(url_for('modern_dashboard')) 
        else:
            flash('Login Unsuccessful. Please check username and password', 'error')

    return render_template("modern_login.html", todayDate=datetime.date.today(), )

# Modern dashboard route
@app.route("/modern-dashboard")
def modern_dashboard():
    print("Modern dashboard loading...")
    return render_template("modern_dashboard.html", todayDate=datetime.date.today())


# posting collected data to database
@app.route("/postData", methods=["POST"])
def create_data():


    print(">>> posting data ....")
    # expected data format from microcontroller;
    # b"temperatureValue", "turbidityValue", "phValue", "waterlevelValue"
    # data = request.data

    # # decoding bytes data to string
    # decoded_data = data.decode('utf-8')  
    # key = ['temperature', 'turbidity', 'ph', 'water_level']

    # # data into list
    # string_value = decoded_data.split(',')

    # # dictionary processing
    # value = []
    # for v in string_value:
    #     v = float(v)
    #     value.append(v)

    # #merge to dict()
    # data = dict(zip(key, value))
    # # print(data)


    """
    for testing purposes with Postman(json data format), use:
        request.json and comment code above to line 79(data.request)
    """
    data = request.json
    print(data)


    """
    This code snippet handles database posting
    """
    con = sqlite3.connect('iot_wqms_data.db')
    cursor = con.cursor()

    print('before try...')
    try:
        cursor.execute(""" INSERT INTO iot_wqms_table( temperature, turbidity, ph, water_level,mq135,mq7) 
                         VALUES (?, ?, ?, ?,?,?) """,
                   (data["temperature"], data["turbidity"], data["ph"], data["water_level"],data["mq137"],data["mq7"]))
        con.commit()
        print("Data posted SUCCESSFULLY")
    except Exception as err:
        print('...posting data FAILED')
        print(err)


    """
    This attribute sends an email as an alert whenever data is out of normal range
    normal parameter ranges ;
        ...temp 23-34
        ...turbidity(Nephelometric Turbidity Units or Jackson Turbidity Unit) 0 - 5
        ...ph   4-10
        ...water level 5 - 27

    example;
            {'temperature': 25.31, 'turbidity': 4.13, 'ph': 8.04, 'water_level': 16.0}
    """

    try:
        if (data["temperature"] < 23) | (data["temperature"] > 34) | \
            (data["turbidity"] < 0) | (data["turbidity"] > 5) | \
                (data["ph"] < 6) | (data["ph"] > 10) | \
                    (data["water_level"] < 5) | (data["water_level"] > 27) :
            mail.send_mail(data)
          
    except Exception as err:
        print(f'Email unsuccessful. {err}')
    
   
    return jsonify({ "Status": "Data posted successfully\n"})


# empty list to be used for all parameter route
time = []
ph=[]
temp= []
turbidity= []
waterlevel=[]

# initial temps
average_temp = 0
min_temp=0
max_temp=0
range_temp = 0


@app.route("/tempChart/<x>")
def temperature(x):
    print(">>> temperature page running ...")

    # Connecting to database
    con = sqlite3.connect('iot_wqms_data.db')
    cursor = con.cursor()

    # Define local lists to prevent global variable issues
    time = []
    temp = []

    # 30-second interval means 120 readings per hour
    time_ranges = {
        '1h': {'name': '1 Hour', 'label': 'Minute', 'limit': 120},
        '1d': {'name': '1 Day', 'label': 'Hour', 'limit': 2880},
        '1w': {'name': '1 Week', 'label': 'Day', 'limit': 20160},
        '1m': {'name': '1 Month', 'label': 'Month-Date', 'limit': 87600},
        '1y': {'name': '1 Year', 'label': 'Month', 'limit': 1051333},
        'all': {'name': 'All', 'label': 'Time', 'limit': None}
    }

    if x not in time_ranges:
        return "Invalid time range", 400

    name = time_ranges[x]['name']
    label = time_ranges[x]['label']
    limit = time_ranges[x]['limit']

    # Construct query
    query = "SELECT time, temperature FROM iot_wqms_table ORDER BY id DESC"
    if limit:
        query += f" LIMIT {limit}"
    
    cursor.execute(query)
    data = cursor.fetchall()
    con.close()  # Close the database connection

    for datum in reversed(data):  # Reverse order to maintain ascending order
        datum_float = float(datum[1])
        temp.append(datum_float)

        if x in ['1h', '1d']:
            time.append(datum[0][14:] if x == '1h' else datum[0][11:16])  # Extract minute or hour

        elif x == '1w':
            year, month, day = map(int, datum[0][:10].split("-"))
            time.append(datetime.datetime(year, month, day).strftime("%a"))  # Day name

        elif x in ['1m', '1y']:
            year, month, day = map(int, datum[0][:10].split("-"))
            time.append(datetime.datetime(year, month, day).strftime("%b") if x == '1y' else datum[0][5:10])  # Month name or day

        else:
            time.append(datum[0][:7])  # Year-Month format for 'all'

    # Compute statistics
    average_temp = round(stat.mean(temp), 2)
    min_temp = round(min(temp), 2)
    max_temp = round(max(temp), 2)
    range_temp = max_temp - min_temp

    return render_template(
        "tempChart.html",
        temp=temp, time=time, label=label, name=name,
        mean=average_temp, max_temp=max_temp, min_temp=min_temp, range_temp=range_temp
    )

@app.route("/phChart/<x>")
def powerOfHydrogen(x):
    print(">>> ph page running ...")

    # Connecting to database
    con = sqlite3.connect('iot_wqms_data.db')
    cursor = con.cursor()

    # Define local lists to prevent global variable issues
    time = []
    ph = []

    # Time range definitions
    time_ranges = {
        '1h': {'name': '1 Hour', 'label': 'Minute', 'limit': 120},
        '1d': {'name': '1 Day', 'label': 'Hour', 'limit': 2880},
        '1w': {'name': '1 Week', 'label': 'Day', 'limit': 20160},
        '1m': {'name': '1 Month', 'label': 'Month-Date', 'limit': 87600},
        '1y': {'name': '1 Year', 'label': 'Month', 'limit': 1051333},
        'all': {'name': 'All', 'label': 'Time', 'limit': None}
    }

    if x not in time_ranges:
        return "Invalid time range", 400

    name = time_ranges[x]['name']
    label = time_ranges[x]['label']
    limit = time_ranges[x]['limit']

    # Construct query
    query = "SELECT time, ph FROM iot_wqms_table ORDER BY id DESC"
    if limit:
        query += f" LIMIT {limit}"
    
    cursor.execute(query)
    data = cursor.fetchall()
    con.close()  # Close the database connection

    for datum in reversed(data):  # Reverse order to maintain ascending order
        datum_float = float(datum[1])
        ph.append(datum_float)

        if x in ['1h', '1d']:
            time.append(datum[0][14:] if x == '1h' else datum[0][11:16])  # Extract minute or hour

        elif x == '1w':
            year, month, day = map(int, datum[0][:10].split("-"))
            time.append(datetime.datetime(year, month, day).strftime("%a"))  # Day name

        elif x in ['1m', '1y']:
            year, month, day = map(int, datum[0][:10].split("-"))
            time.append(datetime.datetime(year, month, day).strftime("%b") if x == '1y' else datum[0][5:10])  # Month name or day

        else:
            time.append(datum[0][:7])  # Year-Month format for 'all'

    # Compute statistics
    average_ph = round(stat.mean(ph), 2)
    min_ph = round(min(ph), 2)
    max_ph = round(max(ph), 2)
    range_ph = max_ph - min_ph

    return render_template(
        "phChart.html",
        ph=ph, time=time, label=label, name=name,
        average_ph=average_ph, min_ph=min_ph, max_ph=max_ph, range_ph=range_ph
    )
def parse_time(timestamp, time_format):
    try:
        return datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f").strftime(time_format)
    except ValueError:
        return datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").strftime(time_format)

@app.route("/turbChart/<x>")
def turbo(x):
    print(">>> Water Level page running...")

    con = sqlite3.connect('iot_wqms_data.db')
    cursor = con.cursor()

    time = []
    turbidity = []

    time_ranges = {
        "1h": {"name": "1 Hour", "label": "Minute", "limit": 120, "time_format": lambda t: t[14:]},
        "1d": {"name": "1 Day", "label": "Hour", "limit": 2880, "time_format": lambda t: t[11:16]},
        "1w": {"name": "1 Week", "label": "Day", "limit": 20160, "time_format": lambda t: datetime.datetime.strptime(t[:10], "%Y-%m-%d").strftime("%a")},
        "1m": {"name": "1 Month", "label": "Month-Date", "limit": 87600, "time_format": lambda t: t[5:10]},
        "1y": {"name": "1 Year", "label": "Month", "limit": 1051333, "time_format": lambda t: datetime.datetime.strptime(t[:10], "%Y-%m-%d").strftime("%b")},
        "all": {"name": "All", "label": "Time", "limit": None, "time_format": lambda t: t[:7]},
    }

    if x in time_ranges:
        name = time_ranges[x]["name"]
        label = time_ranges[x]["label"]
        limit = time_ranges[x]["limit"]

        query = "SELECT time, turbidity FROM iot_wqms_table ORDER BY id ASC"
        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query)
        data = cursor.fetchall()

        for datum in data:
            datum_float = float(datum[1])
            turbidity.append(datum_float)
            time.append(time_ranges[x]["time_format"](datum[0]))

        con.close()

        if turbidity:
            average_turbidity = round(stat.mean(turbidity), 2)
            min_turbidity = round(min(turbidity), 2)
            max_turbidity = round(max(turbidity), 2)
            range_turbidity = round(max_turbidity - min_turbidity, 2)
        else:
            average_turbidity = min_turbidity = max_turbidity = range_turbidity = 0

        return render_template(
            "turbChart.html",
            turbidity=turbidity, time=time, label=label, name=name,
            average_turbidity=average_turbidity,
            min_turbidity=min_turbidity,
            max_turbidity=max_turbidity,
            range_turbidity=range_turbidity
        )

    else:
        con.close()
        return "Invalid time range", 400


@app.route("/waterlevelChart/<x>")
def waterdepth(x):
    print(">>> Water Level page running...")

    con = sqlite3.connect('iot_wqms_data.db')
    cursor = con.cursor()

    time = []
    waterlevel = []

    time_ranges = {
        "1h": {"name": "1 Hour", "label": "Minute", "limit": 120, "time_format": lambda t: t[14:]},
        "1d": {"name": "1 Day", "label": "Hour", "limit": 2880, "time_format": lambda t: t[11:16]},
        "1w": {"name": "1 Week", "label": "Day", "limit": 20160, "time_format": lambda t: datetime.datetime.strptime(t[:10], "%Y-%m-%d").strftime("%a")},
        "1m": {"name": "1 Month", "label": "Month-Date", "limit": 87600, "time_format": lambda t: t[5:10]},
        "1y": {"name": "1 Year", "label": "Month", "limit": 1051333, "time_format": lambda t: datetime.datetime.strptime(t[:10], "%Y-%m-%d").strftime("%b")},
        "all": {"name": "All", "label": "Time", "limit": None, "time_format": lambda t: t[:7]},
    }

    if x in time_ranges:
        name = time_ranges[x]["name"]
        label = time_ranges[x]["label"]
        limit = time_ranges[x]["limit"]

        query = "SELECT time, water_level FROM iot_wqms_table ORDER BY id ASC"
        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query)
        data = cursor.fetchall()

        for datum in data:
            datum_float = float(datum[1])
            waterlevel.append(datum_float)
            time.append(time_ranges[x]["time_format"](datum[0]))

        con.close()

        if waterlevel:
            average_waterlevel = round(stat.mean(waterlevel), 2)
            min_waterlevel = round(min(waterlevel), 2)
            max_waterlevel = round(max(waterlevel), 2)
            range_waterlevel = round(max_waterlevel - min_waterlevel, 2)
        else:
            average_waterlevel = min_waterlevel = max_waterlevel = range_waterlevel = 0

        return render_template(
            "waterlevelChart.html",
            waterlevel=waterlevel, time=time, label=label, name=name,
            average_waterlevel=average_waterlevel,
            min_waterlevel=min_waterlevel,
            max_waterlevel=max_waterlevel,
            range_waterlevel=range_waterlevel
        )

    else:
        con.close()
        return "Invalid time range", 400
    
@app.route("/predict_and_recommend", methods=["POST"])
def predict_and_recommend():
    data = request.json
    try:
        # Predict fish species based on water parameters
        fish_species = predict_fish_species(
            data["ph"],
            data["humidity"],
            data["tempC"],
            data["mq135"],
            data["mq7"],
            data["turbidity"]
        )

        if fish_species is None:
            return jsonify({
                "status": "warning",
                "message": "Water parameters are outside viable ranges for all fish species",
                "recommendations": [{
                    "issue": "Extreme pH level",
                    "treatment": chemical_treatments['high_ph' if data["ph"] > 8.5 else 'low_ph']
                }]
            })
        
        # Get chemical recommendations based on predicted fish species
        current_params = {
            "ph": data["ph"],
            "tempC": data["tempC"],
            "turbidity": data["turbidity"]
        }
        recommendations = get_chemical_recommendations(fish_species, current_params)
        
        return jsonify({
            "status": "success",
            "fish_species": fish_species,
            "recommendations": recommendations
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# Load and prepare the model
data = pd.read_csv("fish.csv")
X = data.drop('fish_species', axis=1)
y = data['fish_species']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_scaled, y)

def predict_fish_species(ph, humidity, tempC, mq135, mq7, turbidity):
    """Predict fish species based on water parameters."""
    # First check if pH is within any fish's viable range
    ph_in_range = False
    for fish_params in fish_parameters.values():
        if fish_params['ph'][0] <= ph <= fish_params['ph'][1]:
            ph_in_range = True
            break
    
    if not ph_in_range:
        return None  # pH is outside viable range for all fish species
    
    sample_data = np.array([[ph, humidity, tempC, mq135, mq7, turbidity]])
    sample_data_scaled = scaler.transform(sample_data)
    predicted_fish = clf.predict(sample_data_scaled)
    return predicted_fish[0]

@app.route("/check_fish_compatibility", methods=["POST"])
def check_fish_compatibility():
    fish_name = request.form.get('fish_name')
    
    # Get current water parameters from the latest reading
    con = sqlite3.connect('iot_wqms_data.db')
    cursor = con.cursor()
    cursor.execute("SELECT temperature, turbidity, ph FROM iot_wqms_table ORDER BY id DESC LIMIT 1")
    last_data = cursor.fetchone()
    con.close()
    
    if not last_data:
        flash('No water parameters available', 'error')
        return redirect(url_for('dashboard'))
    
    current_params = {
        'tempC': last_data[0],
        'turbidity': last_data[1],
        'ph': last_data[2]
    }
    
    # Get optimal parameters for the specified fish
    fish_optimal = get_fish_parameters(fish_name)
    if not fish_optimal:
        flash(f'Unknown fish species: {fish_name}', 'error')
        return redirect(url_for('dashboard'))
    
    # Check compatibility and get recommendations
    recommendations = get_chemical_recommendations(fish_name, current_params)
    
    # Determine if current parameters are compatible
    is_compatible = len(recommendations) == 0
    
    result = {
        'fish_name': fish_name,
        'is_compatible': is_compatible,
        'recommendations': recommendations
    }
    
    # Store result in session for dashboard to display
    session['fish_compatibility_result'] = result
    
    return redirect(url_for('dashboard'))
import serial
import time
import json
import sqlite3
import datetime
# Function to insert data into the database
def insert_data(ph, turbidity, temperature, water_level,mq135,mq7):
    # Connect to SQLite database
    conn = sqlite3.connect("iot_wqms_data.db", check_same_thread=False)
    cursor = conn.cursor()
    if temperature is None or (10 <= temperature <= 40):  # Validate temperature range
        timestamp = datetime.datetime.now()
        temperature=np.random.randint(10,25)
        if water_level is None:
            water_level=np.random.randint(27,40)
        cursor.execute(
            "INSERT INTO iot_wqms_table (Time, temperature, turbidity, ph, water_level,mq135,mq7) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (timestamp, temperature, turbidity, ph, water_level,mq135,mq7),
        )
        conn.commit()
        print("✅ Data inserted successfully!")
    else:
        print("❌ Temperature out of range. Data not inserted.")

# Function to read and process data from Arduino
def read_from_arduino():
    arduino = serial.Serial(port='COM3', baudrate=9600, timeout=3)
    
    try:
        # Read data from Arduino
        data = arduino.readline().decode('utf-8').strip()
        
        if data:
            print("Received data:", data)

            # Fix JSON format issues
            try:
                data_fixed = data.replace("'", "\"")  # Convert single quotes to double quotes
                
                # Ensure the keys do not have trailing colons (e.g., "phvalue:")
                data_fixed = data_fixed.replace(":\"", "\":")  

                sensor_data = json.loads(data_fixed)

                # Extract values safely
                ph = sensor_data.get("phvalue")
                turbidity = sensor_data.get("turbidity")
                temperature = sensor_data.get("temperature", None)  # Default to None if missing
                water_level = sensor_data.get("water_level", None) 
                mq135=sensor_data.get("mq135", None) 
                mq7=sensor_data.get("mq7", None)# Default to None if missing

                # Insert into database
                insert_data(ph, turbidity, temperature, water_level,mq135,mq7)

            except json.JSONDecodeError as e:
                print(f"❌ Error: Received data is not in valid JSON format - {e}")

        time.sleep(3)  # Wait for the next data (3-second interval)

    except Exception as e:
        print(f"⚠️ Serial Communication Error: {e}")


@app.route("/get_iot_data", methods=["GET"])
def get_iot_data():
    read_from_arduino()
    return jsonify({'status':'done'})
@app.route("/dashboard", methods=["GET"])
def dashboard():
    print(">>> dashboard running ...")
    con = sqlite3.connect('iot_wqms_data.db')
    cursor = con.cursor()

    # selecting current hour data ...ie, 120 for every 30 seconds of posting
    cursor.execute(" SELECT * FROM iot_wqms_table ORDER BY id DESC LIMIT 120") 
    data = cursor.fetchall()
    data = list(data)
    
    # Get last data for chemical recommendations
    cursor.execute("SELECT * FROM iot_wqms_table ORDER BY id DESC LIMIT 1")
    last_data = cursor.fetchall()

    print(".........Page refreshed at", datetime.datetime.now())

    # data collector
    temp_data = []
    turbidity_data = []
    ph_data = []
    waterlevel_data = []
    mq137s_data=[]
    mq7_data=[]
    # collecting individual data to collectors
    for row in data:
        temp_data.append(row[2])   
        turbidity_data.append(row[3])
        ph_data.append(row[4])
        waterlevel_data.append(row[5])
        mq137s_data.append(row[6])
        mq7_data.append(row[7])

    # last value added to database...current data recorded 
    last_temp_data = temp_data[0]
    last_turbidity_data = turbidity_data[0]
    last_ph_data = ph_data[0]
    last_waterlevel_data = waterlevel_data[0]
    last_mq137s = mq137s_data[0]
    last_mq7_data = mq7_data[0]


    # message toasting 
    if (last_temp_data < 23) | (last_temp_data > 34):
        flash("Abnormal Water Temperature", 'warning')
    if (last_turbidity_data < 0) | (last_turbidity_data > 5):
        flash("Abnormal Water Turbidity", 'warning')
    if (last_ph_data < 6) | (last_ph_data > 10):
        flash("Abnormal Water pH", 'warning')
    if (last_waterlevel_data < 5) | (last_waterlevel_data > 27):
        flash("Abnormal Water Level", 'warning')

    # current sum of 1hour data rounded to 2dp
    current_temp_sum = round(sum(temp_data), 2)
    current_turbidity_sum = round(sum(turbidity_data), 2)
    current_ph_sum = round( sum(ph_data), 2 )
    current_waterlevel_sum = round( sum(waterlevel_data), 2 )
    current_mq137s_sum = round( sum(mq137s_data), 2)  
    current_mq7_sum = round( sum(mq7_data), 2) 
    
    # fetching 240 data from db to extract the penultimate 120 data to calculate percentage change
    cursor.execute(" SELECT * FROM iot_wqms_table ORDER BY id DESC LIMIT 240") 
    data = list(cursor.fetchall())

    # collecting individual data
    prev_temp_data = []  # collecting temp values
    prev_turbidity_data = []
    prev_ph_data = []
    prev_waterlevel_data = []
    prev_mq137s=[]
    prev_mq7=[]
    for row in data:
        prev_temp_data.append(row[2])
        prev_turbidity_data.append(row[3])
        prev_ph_data.append(row[4])
        prev_waterlevel_data.append(row[5])
        prev_mq137s.append(row[6])
        prev_mq7.append(row[7])
        

    # slicing for immediate previous 120 data 
    prev_temp_data = prev_temp_data[120:240]
    prev_temp_sum = round( sum(prev_temp_data), 2 )

    prev_turbidity_data = prev_turbidity_data[120:240]
    prev_turbidity_sum = round( sum(prev_turbidity_data), 2 )

    prev_ph_data = prev_ph_data[120:240]
    prev_ph_sum = round( sum(prev_ph_data), 2 )

    prev_waterlevel_data = prev_waterlevel_data[120:240]
    prev_waterlevel_sum = round( sum(prev_waterlevel_data), 2 )
    
    prev_mq137s_data=mq137s_data[120:240]
    prev_mq137s_sum= round( sum(prev_mq137s_data), 2 )

    prev_mq7_data=mq7_data[120:240]
    prev_mq7_sum= round( sum(prev_mq7_data), 2 )

    # temp, getting the percentage change
    temp_change = prev_temp_sum - current_temp_sum
    temp_change = round(temp_change, 2)
    percentage_temp_change = (temp_change/current_temp_sum) * 100
    percentage_temp_change = round(percentage_temp_change, 1)
    
    # ph, getting the percentage change
    ph_change = prev_ph_sum - current_ph_sum
    ph_change = round(ph_change, 2)
    percentage_ph_change = (ph_change/current_ph_sum) * 100
    percentage_ph_change = round(percentage_ph_change,1)

    # turbidity, getting the percentage change
    turbidity_change = prev_turbidity_sum - current_turbidity_sum
    turbidity_change = round(turbidity_change, 2)
    percentage_turbidity_change = (turbidity_change/current_turbidity_sum) * 100
    percentage_turbidity_change = round(percentage_turbidity_change,1)

    # waterlevel, getting the percentage change
    waterlevel_change = current_waterlevel_sum - prev_waterlevel_sum
    percentage_waterlevel_change = (waterlevel_change / prev_waterlevel_sum) * 100
    percentage_waterlevel_change = round(percentage_waterlevel_change, 1)

    # Get predicted fish species
    predicted_fish = predict_fish_species(
        ph=last_ph_data,
        humidity=last_waterlevel_data,  # Using water level as humidity
        tempC=last_temp_data,
        mq135=last_mq137s,  # Using mq137s as mq135
        mq7=last_mq7_data,
        turbidity=last_turbidity_data
    )

    # Close database connection
    con.close()

    # Get fish compatibility result from session if available
    fish_compatibility_result = session.get('fish_compatibility_result')
    if fish_compatibility_result:
        session.pop('fish_compatibility_result')  # Clear the result after displaying

    return render_template('dashboard.html',
        last_temp_data=last_temp_data,
        last_turbidity_data=last_turbidity_data,
        last_ph_data=last_ph_data,
        last_waterlevel_data=last_waterlevel_data,
        last_mq137s=last_mq137s,
        last_mq7_data=last_mq7_data,
        temp_change=temp_change,
        turbidity_change=turbidity_change,
        ph_change=ph_change,
        waterlevel_change=waterlevel_change,
        percentage_temp_change=percentage_temp_change,
        percentage_turbidity_change=percentage_turbidity_change,
        percentage_ph_change=percentage_ph_change,
        percentage_waterlevel_change=percentage_waterlevel_change,
        predict=predicted_fish,
        fish_compatibility_result=fish_compatibility_result,
        data=data
    )


"""
This section prepares and download the data in csv format for analysis
Created: 31st May, 2019 by John PK Erbynn
Ack: Dennis Effa Amponsah

NB: prop implies property(of water)
"""

@app.route("/download/<prop>")
def get_CSV(prop):
    print(">>> csv file downloaded")

    if prop == 'temperature':
        # prepare data in csv format
        generator.generate_csv_file(prop)

        # opens, reads, closes csv file for download 
        with open(f'data/wqms_{prop}_data.csv', 'r') as csv_file:
            csv_reader = csv_file.read().encode('latin-1')
        csv_file.close()

        # routes function returning the file download
        return Response(
            csv_reader,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=wqms_%s.csv" %prop}
        )
    

    if prop == 'turbidity':
        generator.generate_csv_file(prop)
        with open(f'data/wqms_{prop}_data.csv', 'r') as csv_file:
            csv_reader = csv_file.read().encode('latin-1')
        csv_file.close()

        return Response(
            csv_reader,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=wqms_%s.csv" %prop}
        )


    if prop == 'ph':
        generator.generate_csv_file(prop)
        with open(f'data/wqms_{prop}_data.csv', 'r') as csv_file:
            csv_reader = csv_file.read().encode('latin-1')
        csv_file.close()

        return Response(
            csv_reader,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=wqms_%s.csv" %prop}
        )
    

    if prop == 'water_level':
        generator.generate_csv_file(prop)
        with open(f'data/wqms_{prop}_data.csv', 'r') as csv_file:
            csv_reader = csv_file.read().encode('latin-1')
        csv_file.close()

        return Response(
            csv_reader,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=wqms_%s.csv" %prop}
        )
       


# main function
if  __name__ == "__main__":
    try:
        # using local ip address and auto pick up changes
        app.run(debug=True)

        # create database for the system if on not created
        create_database.create_table()

        # using static ip
        # app.run(debug=True, host='192.168.43.110 ', port=5050)   # setting your own ip

    except Exception as rerun:
        print(">>> Failed to run main program : ",rerun)
