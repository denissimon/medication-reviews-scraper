import requests
from bs4 import BeautifulSoup
from random import choice, uniform, shuffle
from time import sleep
import json
import sys
import os
from typing import (
    Any, 
    List
)
 
def read(filepath: str) -> Any:
    """Function to read data from JSON
    """
    with open(filepath) as json_file:
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

def update_cache(processed_link: str, filepath: str) -> None:
    print(update_cache.__name__ + " for " + processed_link)
    
    cache = read(filepath)
    print("len of cache:", len(cache))
    cache.remove(processed_link)
    print("len of cache after removing processed_link:", len(cache))

    with open(filepath, "w") as outfile:
        json.dump(cache, outfile)

def delete_file(filepath: str) -> None:
    print(delete_file.__name__ + " " + filepath)

    if os.path.exists(filepath):
        os.remove(filepath)

def rewrite_json_file(data: List[str], filepath: str) -> None:
    """Rewrite the existing JSON file by appending new data
    """
    try:
        result_json = read(filepath)
        print("\n")
        filename = os.path.basename(filepath).split('/')[-1]
        print("len of " + filename.split(".")[0] + ":", len(result_json))
        
        for item in data:
            result_json.append(item)            
        print("len of " + filename.split(".")[0] + " after appending:", len(result_json))
        
        with open(filepath, "w") as outfile:
            json.dump(result_json, outfile)
    except:
        with open(filepath, "w") as outfile:
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

    all_drugs_path = "output/all_drugs.json"
    all_reviews_path = "output/all_reviews.json"
    cache_path = "output/cache"

    current_links: List[str] = []

    try:
        current_links = read(cache_path)
    except:
        drugs = read(all_drugs_path)
        for drug in drugs:
            current_links.append(drug["link"])
        with open(cache_path, "w") as outfile:
            json.dump(current_links, outfile)

    # shuffle(current_links) # Optionally
    
    not_processed_links: List[str] = []

    for i, link in enumerate(current_links):
        print("\n")
        print("----------------------------------------------------------------------------")

        if i > 0:
            random_number = uniform(2,4)
            sleep(random_number)

        current_data: List[str] = []

        url = link
        print("Url:", url)

        headers = {
            "User-Agent": choice(useragents), 
            "referer":"https://www.bing.com/",
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.8,image/webp,image/apng,*/*;q=0.7,application/signed-exchange;v=b3",
            "Accept-Encoding":"gzip",
            "Accept-Language":"en-US,en;q=0.8,es;q=0.7",
            "Upgrade-Insecure-Requests":"1"
        }

        proxy = {"http": choice(proxies)}

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
                        duration_and_dosage = duration_and_dosage.replace("years","years / ").replace("months","months / ").replace("weeks","weeks / ").replace("days","days / ").strip()
                        if duration_and_dosage[-2:] == " /":
                            duration_and_dosage = duration_and_dosage[:-2]
                        print("Duration / Dosage:", duration_and_dosage)

                        date_added = row[7]
                        date_added = date_added.replace("Email","")    
                        print("Date added:", date_added)

                        try:
                            reviews = read(all_reviews_path)
                            
                            if check_for_uniqueness:
                                is_unique = True
                                for review in reviews:
                                    if review["rating"] == rating and review["reason"] == reason and review["side_effects"] == side_effects and review["comments"] == comments and review["sex"] == sex and review["age"] == age and review["duration_and_dosage"] == duration_and_dosage and review["date added"] == date_added:
                                        is_unique = False
                                        break
                                if is_unique:
                                    current_data.append({"drug":drug_name, "link":link, "rating":rating, "reason":reason, "side_effects":side_effects, "comments":comments, "sex":sex, "age":age, "duration_and_dosage":duration_and_dosage, "date added":date_added})                                    
                            else:
                                current_data.append({"drug":drug_name, "link":link, "rating":rating, "reason":reason, "side_effects":side_effects, "comments":comments, "sex":sex, "age":age, "duration_and_dosage":duration_and_dosage, "date added":date_added}) 
                        except:
                            current_data.append({"drug":drug_name, "link":link, "rating":rating, "reason":reason, "side_effects":side_effects, "comments":comments, "sex":sex, "age":age, "duration_and_dosage":duration_and_dosage, "date added":date_added})
                            rewrite_json_file([], all_reviews_path)
                    
                    rewrite_json_file(current_data, all_reviews_path)

                    update_cache(link, cache_path)
            else:
                not_processed_links.append(link)
                print_log_info("Not processed links", not_processed_links)
                continue 
        except:
            not_processed_links.append(link)
            print_log_info("Not processed links", not_processed_links)
            continue

    print_log_info("Not processed links", not_processed_links)
    
    cache = open(cache_path).read()
    if cache == "[]":
        delete_file(cache_path)        
    
if __name__ == "__main__":
    if len(sys.argv) > 1:
        ini_str = sys.argv[1]
        if ini_str == "check_for_uniqueness":
            main(check_for_uniqueness = True)
        else:
            main()
    else:
        main()
