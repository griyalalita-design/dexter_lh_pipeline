# Automation Pipeline

## Structure
```
pipeline/
├── jobs/
│   ├── day1.py       # DAY 1 orchestration
│   └── day2.py       # DAY 2 orchestration
└── utils/
    ├── metabase.py   # Extract raw data from Metabase/PNS
    ├── transform.py  # All pandas transformation logic
    ├── gsheet.py     # Google Sheets read/write operations
    └── email.py      # Email notifications
```

## How to Run
```bash
# Run Day 1 pipeline
python jobs/day1.py

# Run Day 2 pipeline
python jobs/day2.py
```

## TODO Before Production
- [ ] Replace mock data in `metabase.py` with real API calls
- [ ] Add real `gspread` credentials in `gsheet.py`
- [ ] Configure SMTP or Gmail API in `email.py`
- [ ] Update `SPREADSHEET_ID` in each job file
- [ ] Confirm staff list join key in `day2.py`
- [ ] Add scheduler (cron or Airflow) to trigger day1/day2 automatically
