import requests
from bs4 import BeautifulSoup
from random import choice, uniform
from time import sleep
import json
import sys
from typing import (
    Any, 
    List, 
    Dict
)

def read(filepath: str) -> Any:
    """Function to read data from JSON
    """
    with open(filepath) as json_file:
        return json.load(json_file)

def get_html(url: str, headers = None, proxy = None) -> str:
    print(get_html.__name__)

    r = requests.get(url, headers=headers, proxies=proxy, timeout=60)
    if r.status_code == 200:
        return r.text
    else:
        print(r.status_code)
        return ""

def get_data(html: str) -> List[Dict[str, str | List[str]]]:
    print(get_data.__name__)

    splitted_html = html.split("By Ingredient Name:")

    html_part1 = splitted_html[0]

    data: List[Dict[str, str | List[str]]] = []

    drug_names: List[str] = []

    #### By brand name:
    soup = BeautifulSoup(html_part1, "lxml")
    all_elements = soup.find_all("font", {"face":"Arial, Helvetica, sans-serif", "size":1})
    
    for el in all_elements:
        ingredients = el.contents[1].strip()
        ingredients = ingredients[1:-1]
        ingredients_arr = ingredients.split(";")
        for i in range(len(ingredients_arr)):
            ingredients_arr[i] = ingredients_arr[i].strip()
        drug_name = el.contents[0].contents[0]
        data.append({"drug":drug_name, "link":"https://www.askapatient.com/"+str(el.a.get("href")), "ingredients":ingredients_arr})
        drug_names.append(drug_name)
    ####

    print("len of new data:", len(data))

    return data

def print_log_info(message: str, data: List[str]) -> None:
    print("\n")
    print("======================")
    print(message + ":")
    print(data)
    print("======================")
    print("\n")

def main(letters_for_processing: List[str]):
    useragents = open("useragents.txt").read().split("\n")
    proxies = open("proxies.txt").read().split("\n")
    
    site_url = "https://www.askapatient.com/drugalpha.asp?letter="
    url = ""

    not_processed_letters: List[str] = []

    for i, letter in enumerate(letters_for_processing):
        if i > 0:
            random_number = uniform(2,6)
            sleep(random_number)
        
        url = site_url + letter
        print("Url:", url)

        headers = {
            "User-Agent": choice(useragents), 
            "referer":"https://www.google.com/",
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Accept-Encoding":"gzip",
            "Accept-Language":"en-US,en;q=0.9,es;q=0.8",
            "Upgrade-Insecure-Requests":"1"
        }
        
        proxy = {"http": choice(proxies)}

        try:
            html = get_html(url, headers, proxy)
            data = get_data(html)
        except:
            not_processed_letters.append(letter)
            print_log_info("Not processed letters", not_processed_letters)
            continue

        # Rewrite existing JSON file by appending new data
        path = "output/all_drugs.json"
        try:
            result_json = read(path)
            print("len of result_json:", len(result_json))
            for item in data:
                result_json.append(item)
            print("len of result_json after appending:", len(result_json))
            if len(data) == 0:
                not_processed_letters.append(letter)
            else:
                with open(path, "w") as outfile:    
                    json.dump(result_json, outfile)
        except:
            len_data = len(data)
            if len_data == 0:
                not_processed_letters.append(letter)
            else:
                with open(path, "w") as outfile:
                    json.dump(data, outfile)
        
        print_log_info("Not processed letters", not_processed_letters)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ini_str = sys.argv[1]
        arr = ini_str.split(",")
        letters_for_doing = []    
        for letter in arr:
            l = (letter.strip())[1:-1]
            letters_for_doing.append(l)
        main(letters_for_doing)
    else:
        with open("output/all_drugs.json", "w") as outfile:
            json.dump("", outfile)
        main(["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"])
