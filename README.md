# ⚡ Energy Consumption Anomaly Detector

A Python-based data pipeline that analyzes metered electricity consumption data to automatically flag anomalies indicative of **meter tampering or fraud** — inspired by real-world work at South Bihar Power Distribution Company Ltd. (SBPDCL).

---

## 🔍 Problem Statement

Electricity distribution companies lose significant revenue due to undetected meter fraud — where consumers tamper with meters to show artificially low consumption. Manual inspection of hundreds of connections is slow and error-prone.

This tool automates the detection process using statistical analysis.

---

## ⚙️ How It Works

1. **Loads** monthly consumption data from a CSV file
2. **Computes** each connection's mean and standard deviation
3. **Flags** a reading as anomalous if:
   - Its **Z-score** exceeds 2.0 (unusual spike or drop), OR
   - It **drops more than 50%** below the connection's own average (strong tampering signal)
4. **Visualizes** trends for every connection with anomalies highlighted
5. **Exports** a CSV report of all flagged connections

---

## 📊 Output

| Output File | Description |
|---|---|
| `output/consumption_analysis.png` | Trend charts for all connections with anomaly flags |
| `output/anomaly_summary.png` | Bar chart — flagged vs normal readings per connection |
| `output/flagged_connections.csv` | CSV report of all suspicious readings |

### Sample Output

```
============================================================
         ANOMALY DETECTION REPORT
============================================================
Total records analyzed : 60
Anomalies detected     : 5
Connections flagged    : 4
============================================================

⚠  C001 | Ramesh Kumar
   Month           : May
   Units Consumed  : 12  (Avg: 174.7)
   Z-Score         : -2.08
   Flag Reason     : Suspected Tampering (Sudden Drop)
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.x | Core language |
| Pandas | Data loading, cleaning, grouping |
| Matplotlib | Visualization & charts |
| NumPy | Statistical calculations |

---

## 🚀 How to Run

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/energy-anomaly-detector.git
cd energy-anomaly-detector
```

### 2. Install dependencies
```bash
pip install pandas matplotlib numpy
```

### 3. Run the detector
```bash
python detector.py
```

The script will read `consumption_data.csv`, print the report in terminal, and save charts + CSV to the `output/` folder.

---

## 📁 Project Structure

```
energy-anomaly-detector/
│
├── detector.py              # Main script
├── consumption_data.csv     # Sample dataset (10 connections, 6 months)
├── output/
│   ├── consumption_analysis.png
│   ├── anomaly_summary.png
│   └── flagged_connections.csv
└── README.md
```

---

## 💡 Real-World Context

This project was directly inspired by my internship at **South Bihar Power Distribution Company Ltd. (SBPDCL)**, where I performed fraud detection analysis on 100+ metered connections — identifying consumption anomalies that supported efforts reducing potential revenue losses by **12%**.

---

## 👤 Author

**Aditya Kumar**  
B.Tech Electrical Engineering — NIT Manipur  
[LinkedIn](https://linkedin.com/in/aditya-kumar-565772274) | [GitHub](https://github.com/itzzadityachaudhari)
