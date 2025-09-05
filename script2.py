import requests
from bs4 import BeautifulSoup
from random import choice, uniform, shuffle
from time import sleep
import json
import sys
from typing import (
    Any, 
    List
)

# Function to read data from JSON
def read(filename: str) -> Any:
    with open(filename) as json_file:
        return json.load(json_file)

def get_html(url: str, headers = None, proxy = None) -> str:
    print(get_html.__name__)

    r = requests.get(url, headers=headers, proxies=proxy, timeout=30)
    if r.status_code == 200:
        return r.text
    else:
        print(r.status_code)
        return ""

def get_data(soup: BeautifulSoup) -> List[List[str]]:
    print(get_data.__name__)

    data: List[List[str]] = []

    table = soup.find("table", attrs={"class":"ratingsTable"})
    
    tds = table.find_all("td", attrs={"valign":"top"})
    tds = [ele.text.strip() for ele in tds]

    cols_count = 8
    tr_count = int(len(tds)/cols_count)

    i = 1
    while i <= tr_count:
        i = i + 1
        data.append(tds[slice(cols_count)])
        for _ in range(cols_count):
            tds.pop(0)

    return data

def update_cache(processed_link: str) -> None:
    print(update_cache.__name__ + " for " + processed_link)
    
    cache = read("output/cache")
    print("len of cache: ", len(cache))
    cache.remove(processed_link)
    print("len of cache after removing processed_link: ", len(cache))

    with open("output/cache", "w") as outfile:
        json.dump(cache, outfile)

def rewrite_json_file(data: List[str], file: str) -> None:
    """Rewrite the existing JSON file by appending new data
    """
    try:
        result_json = read("output/"+file)
        print("\n")
        print("len of " + file.split(".")[0] + ": ", len(result_json))
        for item in data:
            result_json.append(item)            
        print("len of " + file.split(".")[0] + " after appending: ", len(result_json))
        with open("output/" + file, "w") as outfile:
            json.dump(result_json, outfile)
    except:
        with open("output/" + file, "w") as outfile:
            json.dump(data, outfile)

def print_log_info(message: str, data: List[str]) -> None:
    print("\n")
    print("====================")
    print(message + ":")
    print(data)
    print("====================")
    print("\n")
    
def main(check_for_uniqueness: bool = False):
    useragents = open("useragents.txt").read().split("\n")
    proxies = open("proxies.txt").read().split("\n")

    current_links: List[str] = []

    try:
        current_links = read("output/cache")
    except:
        drugs = read("output/all_drugs.json")
        for drug in drugs:
            current_links.append(drug["link"])
        with open("output/cache", "w") as outfile:
            json.dump(current_links, outfile)

    # shuffle(current_links) # Optionally
    
    not_processed_links: List[str] = []

    for i, link in enumerate(current_links):
        print("\n")
        print("----------------------------------------------------------------------------")

        current_data: List[str] = []

        if i > 0:
            random_number = uniform(2,4)
            sleep(random_number)

        url = link
        print("Url:", url)

        proxy = {"http": "http://" + choice(proxies)}
        headers = {
            "User-Agent": choice(useragents), 
            "referer":"https://www.bing.com/",
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.8,image/webp,image/apng,*/*;q=0.7,application/signed-exchange;v=b3",
            "Accept-Encoding":"gzip",
            "Accept-Language":"en-US,en;q=0.8,es;q=0.7",
            "Upgrade-Insecure-Requests":"1"
        }

        try:
            html = get_html(url, headers, proxy)

            if html != "":
                soup = BeautifulSoup(html, "lxml")

                drug_name = soup.title.string.split(":")[0]
                
                data = get_data(soup)
                print("Number of reviews:", len(data))

                if len(data) == 0:
                    not_processed_links.append(link)
                    print_log_info("Not processed links", not_processed_links)
                else:                    
                    for number, row in enumerate(data):
                        print("\n")
                        print("#", number+1)
                        
                        rating = row[0]
                        print("Rating:", rating)

                        reason = row[1].strip()
                        print("Reason:", reason)

                        side_effects = row[2].strip()
                        print("Side effects:", side_effects)

                        comments = row[3].strip()
                        comments = comments.replace("Email this patient","")                           
                        print("Comments:", comments)

                        sex = row[4]
                        print("Sex:", sex)

                        age = row[5]
                        print("Age:", age)
                        
                        duration_and_dosage = row[6]
                        duration_and_dosage = duration_and_dosage.replace("years","years / ")
                        duration_and_dosage = duration_and_dosage.replace("months","months / ")
                        duration_and_dosage = duration_and_dosage.replace("weeks","weeks / ")
                        duration_and_dosage = duration_and_dosage.replace("days","days / ")
                        duration_and_dosage = duration_and_dosage.strip()
                        if duration_and_dosage[-2:] == " /":
                            duration_and_dosage = duration_and_dosage[:-2]
                        print("Duration / Dosage:", duration_and_dosage)

                        date_added = row[7]
                        date_added = date_added.replace("Email","")    
                        print("Date added:", date_added)

                        try:
                            check_reviews = read("output/all_reviews.json")
                            
                            if check_for_uniqueness:
                                is_unique = True
                                for review in check_reviews:
                                    if review["rating"] == rating and review["reason"] == reason and review["side_effects"] == side_effects and review["comments"] == comments and review["sex"] == sex and review["age"] == age and review["duration_and_dosage"] == duration_and_dosage and review["date added"] == date_added:
                                        is_unique = False
                                        break
                                if is_unique:
                                    current_data.append({"drug":drug_name, "link":link, "rating":rating, "reason":reason, "side_effects":side_effects, "comments":comments, "sex":sex, "age":age, "duration_and_dosage":duration_and_dosage, "date added":date_added})                                    
                            else:
                                current_data.append({"drug":drug_name, "link":link, "rating":rating, "reason":reason, "side_effects":side_effects, "comments":comments, "sex":sex, "age":age, "duration_and_dosage":duration_and_dosage, "date added":date_added}) 
                        except:
                            current_data.append({"drug":drug_name, "link":link, "rating":rating, "reason":reason, "side_effects":side_effects, "comments":comments, "sex":sex, "age":age, "duration_and_dosage":duration_and_dosage, "date added":date_added})
                            rewrite_json_file([], "all_reviews.json")
                    
                    rewrite_json_file(current_data, "all_reviews.json")

                    update_cache(link)
            else:
                not_processed_links.append(link)
                print_log_info("Not processed links", not_processed_links)
                continue 
        except:
            not_processed_links.append(link)
            print_log_info("Not processed links", not_processed_links)
            continue

    print_log_info("Not processed links", not_processed_links)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ini_str = sys.argv[1]
        if ini_str == "check_for_uniqueness":
            main(check_for_uniqueness = True)
        else:
            main()
    else:
        main()
