# Orders Data Diagnosis, Cleaning & Revenue Analysis (pandas)

A homework project that takes a deliberately messy `orders.csv`, **diagnoses** it interactively in the terminal, **cleans** it with a set of small helper functions, and then calculates **revenue per customer per month**.

Diagnosis and analysis live in **one script**: every run walks through the same inspect, convert, clean, re-inspect flow before the analysis starts.

## How the script works

The functions are declared at the top of the script and the main flow calls them in order. Run it in a terminal, because most steps pause (`Press Enter to continue...`) or ask a `y/n` question.

| Phase | What happens | Functions involved |
|-------|--------------|--------------------|
| 1. Load | Reads `orders.csv` from the script's own folder | `pd.read_csv` |
| 2. Diagnose | Prints dtypes, the first 5 rows, missing values per column, and exact duplicate rows (offers to drop them) | `check_data_types_and_duplicates` |
| 3. Check and convert | Checks that `order_id`, `customer_id`, `amount` are numeric and that `created_at` parses as datetime. For each problem it asks whether to convert | `check_columns_numeric`, `check_is_datetime` (these call the convert functions) |
| 4. Clean | Drops every row with a missing value, then every row with an invalid or future date | `drop_missing_values`, `drop_incorrect_date` |
| 5. Final types | Casts `order_id` and `customer_id` to `int` | `convert_simple_types` |
| 6. Re-diagnose | Runs the same inspection again to confirm types, nulls and duplicates are correct | `check_data_types_and_duplicates` |
| 7. Analyze | Sums `amount` per customer per month, sorts by revenue, and filters to positive totals | `groupby`, `sort_values` |

In short: **check, convert, check again, and only then analyze.** Coercing bad values to `NaN`/`NaT` in phase 3 is what lets the drop functions in phase 4 remove them.

## The functions

Checking and converting are deliberately **separate** functions: the check functions look and ask, the convert functions do the work.

### Checking (read-only, or optional action after asking)

| Function | Purpose |
|----------|---------|
| `check_data_types_and_duplicates(df)` | Prints dtypes, head, missing-value counts and exact duplicate rows. Optionally drops duplicates if the user answers `y` |
| `check_columns_numeric(df, columns)` | Reports non-numeric columns and offers to convert them with `convert_columns_to_numeric` |
| `check_is_datetime(df, column_name, dformat)` | Tests whether the column parses with the given format and offers to convert it with `convert_datetime` |

### Converting

| Function | Purpose |
|----------|---------|
| `convert_columns_to_numeric(df, columns)` | Converts string columns to numeric with `errors="coerce"`, so invalid values become `NaN`. The result is a float when decimals or missing values are present; to force `int`, use `convert_simple_types` |
| `convert_datetime(df, column_name, dformat)` | Strips whitespace and parses to datetime. Default format is `"%Y-%m-%d %H:%M:%S"`, editable through `dformat`. Invalid values become `NaT` |
| `convert_simple_types(df, columns_name, new_type)` | Casts columns with `astype` to `int`, `float` or `str`. It also accepts things like `category`, but that is not the intended use. Not for datetimes |

### Dropping (these act directly, with no prompt)

| Function | Purpose |
|----------|---------|
| `drop_missing_values(df)` | Removes every row that has a null in **any** column |
| `drop_incorrect_date(df, column_name, dformat)` | Removes rows whose date cannot be parsed or lies in the future (later than the current time), since those are not valid orders |

## The dataset

`orders.csv` is simulated data (about 200 orders, January to October 2026) with a few percent of intentionally damaged rows.

| Column        | Meaning                           | Expected type |
|---------------|-----------------------------------|---------------|
| `order_id`    | Order identifier                  | integer       |
| `customer_id` | Customer identifier               | integer       |
| `amount`      | Order amount                      | float         |
| `created_at`  | Timestamp (`YYYY-MM-DD HH:MM:SS`) | datetime      |

Injected problems include:

- empty values, whitespace-only cells and `NULL` / `N/A` text,
- negative and zero amounts, and non-numeric amounts (e.g. `abc`),
- malformed dates and a date far in the future,
- exact duplicate rows, and rows that reuse an `order_id` with different values.

On first load, the diagnosis typically shows columns with the wrong type (for example `order_id` as float because of missing values, and `amount` or `created_at` as strings because of bad entries). That is why the type check comes before any cleaning.

## Requirements

- Python 3.9+
- pandas

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux
python -m pip install pandas
```

## Usage

Put `orders.csv` in the same folder as the script and run it from a terminal:

```bash
python main.py
```

(Replace `main.py` with the actual script name.) Press Enter to move through the diagnosis screens and answer `y` or `n` when asked. At the end it prints two tables:

- `per_customer`: revenue per customer per month, including negative totals (e.g. returns),
- `per_customer_profit`: the same table limited to rows where `revenue > 0`.

```
   customer_id    month  revenue
59          16  2026-03  1096.47
136         35  2026-07   799.43
...
```

## Design decisions

- **Negative and zero amounts are kept** in `per_customer`, because the task did not say to exclude them. They are treated as possible returns. `per_customer_profit` then filters on the monthly **total**, so a customer-month is removed only if its net revenue is not positive.
- **Convert with coerce, then drop.** Invalid values are turned into `NaN`/`NaT` first and removed afterwards, rather than crashing the script.
- **Verify after cleaning.** The inspection runs twice, so the data is confirmed correct before it is analyzed.

## Weaknesses and limitations

**Structure**
- **Diagnosis and analysis are mixed in one repetitive script.** To get the analysis you must go through every diagnostic screen and prompt again, even when the data and the answers are the same as last time. The same inspection function is also called twice by design.
- **Not runnable unattended.** The `input()` prompts make it unsuitable for automation, scheduled runs or automated tests.
- **Hard-coded names and path.** Column names and the file location are written directly in the main flow.

**Cleaning**
- **Only exact duplicate rows are detected.** `df.duplicated()` compares whole rows, so rows that share an `order_id` but differ in amount or date stay in the data. Duplicates are also only removed if the user answers `y`.
- **Duplicates are dropped before type conversion**, so rows that would become identical only after cleaning are not caught.
- **`dropna()` is all-or-nothing.** A single missing value in any column removes the whole row, with no imputation and no way to choose columns.
- **Rows are dropped silently.** There is no report of how many rows each cleaning step removed.
- **The future-date cutoff is the time of the run** (`datetime.now()`), so it moves every time the script runs.
- **`check_is_datetime` tests whether values can be parsed, not whether the column is already a datetime dtype.** A string column that parses cleanly is reported as "in datetime format". It is only converted when the user accepts, or later inside `drop_incorrect_date`.

**Conversion**
- **`convert_simple_types` does not coerce.** Casting to `int` raises an error if any `NaN` or invalid value remains, so it must run after the drop steps.
- **The pipeline relies on the user's answers.** Declining a needed conversion at a prompt leaves bad values in place and can cause later steps to fail.
- **Functions modify the DataFrame they receive** (`inplace` drops and column assignment), so the original loaded data is changed as the script runs.

**Output**
- **The cleaned dataset is not saved.** Results are only printed to the terminal.
- **The "no duplicates, no missing values" claim in the script's comment** holds only if the user chose to drop duplicates.

## Possible improvements

- Split the project into a **diagnosis script** and a **clean-and-analyze script** (or a reusable `clean_orders()` function), so analysis can run without the prompts.
- Report row counts removed at each cleaning step.
- Detect duplicate `order_id` values separately from fully identical rows and define a rule for which one to keep.
- Save the cleaned DataFrame to a new CSV.

## Project structure

```
databek-python-homework-pandas/
├── main.py        # checks, conversions, cleaning and aggregation
├── orders.csv     # simulated, intentionally messy dataset
└── README.md
```

The script reads `orders.csv` through a path relative to the script file (`Path(__file__).parent`), so it works from any location on any machine.
