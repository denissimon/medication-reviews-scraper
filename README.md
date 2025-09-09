# Medication Reviews Scraper

This scraper collects a list of medications and reviews on them from [AskaPatient.com](https://www.askapatient.com). At the moment, there are more than 100k patient reviews for 2171 medications A-Z. The collected data is processed and saved in a structured JSON format for subsequent use in NLP tasks, ML model training.

The folder where the results are saved is [`output`](https://github.com/denissimon/medication-reviews-scraper/tree/main/output). The [`output/examples`](https://github.com/denissimon/medication-reviews-scraper/tree/main/output/examples) folder contains some examples of finished results.

`proxies.txt` - a set of proxy server addresses.

`useragents.txt` - a set of user-agent strings.

## script1.py 

The first step is to extract the medications we want to get reviews for later and generate `all_medications.json` in the following format:

```json
[{
    "medication": "...",
    "link": "...",
    "ingredients": ["...", "..."]
}]
```

### Usage

If the argument is not provided, the script will start working on all letters of the English alphabet:

```sh
python script1.py
```

This is equivalent to the following call:

```sh
python script1.py "'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'"
```

To start working only with a specific one or several letters:

```sh
python script1.py "'Y'"
python script1.py "'A','B'"
```

As an option, you can run the script sequentially for each letter and rename the output `all_medications.json` to a file corresponding to the letter, for example, `medications_Y.json`.

In case, for some reason (e.g., due to an error 403), part of the letters was not fully processed, this list is displayed in the terminal:

```sh
======================
Not processed letters:
['M', 'N']
======================
```

Then you can run the script again, passing the list of these letters:

```sh
python script1.py "'M','N'"
```

The extracted data will be added to the resulting file `all_medications.json`.

## script2.py

The second step is to extract data from the review pages for each medication found in `all_medications.json` and generate `all_reviews.json` in the following format:

```json
[{
  "medication": "...",
  "link": "...",
  "rating": "5",
  "reason": "...",
  "side effects": "...",
  "comments": "...",
  "sex": "...",
  "age": "21",
  "duration_and_dosage": "2 months / 1X day",
  "date added": "10/29/2024"
 }]
```

### Usage

```sh
python script2.py
```

When running the script, all links are first taken from `output/all_medications.json`, and written to the cache `output/cache`.

During the script's execution, successfully processed links are removed from the cache, and `cache` is overwritten.

If some of the links were not fully processed for some reason, this list is displayed in the terminal:

```sh
====================
Not processed links:
['https://www.askapatient.com/viewrating.asp?drug=21676&name=YAZ']
====================
```

When the script is run again, the number of links remaining to be processed will decrease until all of them have been processed.

The extracted data is appended to the existing data and written to `all_reviews.json`.

You can also pass the `check_for_uniqueness` argument to check each new review for uniqueness before adding it, and reliably avoid duplicates if any:

```sh
python script2.py check_for_uniqueness
```

When the script finishes running, if there are no links left in `cache`, it is deleted automatically.

Note that, by default, `script1.py` collects links only from the 1st page of medication reviews. There may be several pages. In order to get reviews from other pages, you need to edit the `all_medications.json`, adding `&page=N` to each link of interest.

Example:

1st page: https://www.askapatient.com/viewrating.asp?drug=18662&name=ACCUTANE

2nd page: https://www.askapatient.com/viewrating.asp?drug=18662&name=ACCUTANE&page=2

## Installation

The code was written and tested in Python 3.13.7. Make sure that you're using Python 3.10+.

1. Clone or download this repo.

2. Create a Python virtual environment and run `pip install -r requirements.txt` inside this repo.
