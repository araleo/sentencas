"""
This is the main file of the scrap module.

This module is heavily personalized to scrap data
from the Tribunal de Justiça do Estado de Minas Gerais
verdicts search page (BASE_URL).

This module was written to scrap all data at once.
If you plan to scrap data regularly, you might
want to add a query parameter to the search url
to filter a specific time frame and scrap your
data within that time frame.
"""

from typing import List
from typing import Tuple
from typing import Union
import time

import bs4
import os
import requests

from constants import COURTS
from constants import CSV_DATA_PATH
from constants import RAW_DIR
from constants import TXT_DIR
from csv_utils import save_list_as_csv
from my_logs import LogServices
from my_logs import log_err


RETRY_WAIT_SECS = 30
MAX_RETRIES = 3
BASE_URL = "https://www5.tjmg.jus.br/jurisprudencia/"
COUNTY = 24 # 24 is Belo Horizonte
EMPTY_RESULT = "Nenhum registro foi encontrado."
QUERY = "crime"


def search_all_courts():
    """
    Iterates though all courts listed in the COURTS dict
    to scrap data related to that specific court in the
    verdict search page using query params as filters.
    """
    for court_name, court_id in COURTS.items():
        search(court_id, court_name)


def search_court_from_page(court_name: str, page: int = 0):
    """
    Scraps data from a specific court starting from a specific page.
    Starting page defaults to 0.
    """
    court_id = COURTS.get(court_name, None)
    if court_id is None:
        print("Court not available.")
        return
    search(court_id, court_name, page)


def search(court_id: str, court_name: str, page: int = 0):
    """
    Iterates through the search pages until all results are scrapped.
    In case of https request errors, this breaks after MAX_RETRIES retries on the same endpoint.
    """
    print(f"Now scraping data from: {court_name}")
    last_visited_page = walk_search(court_id, court_name, page)
    while last_visited_page != 0:
        last_visited_page = walk_search(court_id, court_name, last_visited_page)


def walk_search(court_id: str, court_name: str, page: int = 0) -> int:
    """
    Walks through all pages of the verdicts search,
    starting from <page>, until it reachs a page with
    no results, when it assumes the search as over and returns 0.

    If an error occurs in a request, this function returns
    the number of the last visited page so you can try again.
    """
    while True:
        print(f"Getting page #{page}")
        search_url = get_search_url(court_id, page)
        res = get_page(search_url)

        if res is None:
            return page

        if EMPTY_RESULT in res.text:
            print("Got no result. Is the search over?")
            return 0

        page_data = parse_page(res.text, court_name)
        save_list_as_csv(RAW_DIR, "raw", page_data)

        page += 1


def get_search_url(court: str, page: int) -> str:
    """
    Returns the formatted url to the verdict search page at <page> number.
    """
    endpoint = "sentenca.do?"
    query = (
        f"palavrasConsulta={QUERY}",
        f"codigoComarca={COUNTY}",
        f"codigoOrgaoJulgador={court}",
        "resultPagina=50",
        f"pg={page}",
        "pesquisar=Pesquisar"
    )
    return BASE_URL + endpoint + "&".join(query)


def get_page(url: str) -> Union[requests.Response, None]:
    """
    Sends a get request to <url> and returns the response if
    the request was valid or None if the request failed.
    """
    tries = 0
    while tries < MAX_RETRIES:
        time.sleep(tries * RETRY_WAIT_SECS) # Progressively waits after each failure
        res = requests.get(url)

        if res.ok:
            return res

        tries += 1
        print(f"Response not ok. On try #{tries} got {res.status_code} when getting {url}")
        if tries != MAX_RETRIES:
            print(f"Trying again in {tries * RETRY_WAIT_SECS} seconds.")
        else:
            log_err(LogServices.SCRAP, f"ERR: {url}. Could not get {url}. Got status {res.status_code} and content {res.text}")

    return None


def parse_page(page: str, court_name: str) -> List[str]:
    """
    Parsers the search results into a list of strings
    formatted as a ';' separated csv.
    """
    soup = bs4.BeautifulSoup(page, "html.parser")
    nums = group_pairs_as_tuples(soup.select("#tabelaSentenca .caixa_processo a div"))
    desc = group_pairs_as_tuples(soup.select("#tabelaSentenca .corpo"))
    imgs = soup.select("#tabelaSentenca span img")
    data = []
    for num, desc, img in zip(nums, desc, imgs):
        old_num = num[0].getText().strip()
        cnj_num = num[1].getText().strip().replace(".", "").replace("-", "")
        judge = desc[0].getText().strip().split(":")[-1].strip()
        pub_date = desc[1].getText().strip().split()[-1].strip()
        file_id, file_hash = get_id_and_hash_from_img_tag(img)
        full_id = f"{file_id}{file_hash}"
        download_url = get_download_url(file_id, file_hash)
        data.append(";".join((court_name, old_num, cnj_num, judge, pub_date, full_id, file_id, file_hash, download_url)))
    return data


def group_pairs_as_tuples(elements: bs4.ResultSet) -> List[Tuple[bs4.element.Tag, bs4.element.Tag]]:
    """
    Groups pairs of contiguous related html elements into tuples.
    """
    return [(elements[i], elements[i+1]) for i in range(len(elements) - 1) if i % 2 == 0]


def get_id_and_hash_from_img_tag(img: bs4.element.Tag) -> List[str]:
    """
    Gets the file id and file hash from the imagem tag.
    This id and hash will be used to form the verdicts download url.
    """
    ids = img["onclick"].replace("'", "")
    _from = ids.find("(") + 1
    until = ids.rfind(")")
    codes = ids[_from:until].split(",")
    return codes[1:]


def get_download_url(file_id: str, file_hash: str) -> str:
    """
    Builds the verdict download url from the file id and hash.
    """
    endpoint = "downloadArquivo.do?"
    query = (
        "sistemaOrigem=1",
        f"codigoArquivo={file_id}",
        f"hashArquivo={file_hash}"
    )
    return BASE_URL + endpoint + "&".join(query)


def download_all_verdicts():
    """
    Downloads the text content from all the verdicts
    which info was scrapped and stored in a csv file.
    """
    with open(CSV_DATA_PATH) as f:
        lines = f.readlines()

    for line in lines:
        line_data = line.split(";")
        url = line_data[-1]
        full_id = line_data[5]
        download_verdit(full_id, url)


def download_verdit(full_id: str, url: str):
    """
    Requests the url for the verdict text content and saves
    it in a .txt file.
    If the text is empty or the verdict is stored in a .pdf
    file it is skipped. Request errors are also skipped
    and printed.
    """
    filepath = os.path.join(TXT_DIR, f"{full_id}.txt")

    if filepath in os.listdir(TXT_DIR):
        message = f"ERR: {full_id}. A file with that id already exists. Skipping for now"
        log_err(LogServices.SCRAP, message)
        return

    print(f"Downloading {full_id} from {url}")
    res = requests.get(url)

    if not res.ok:
        log_err(LogServices.SCRAP, f"ERR: {full_id}. Could not get {url}. Skipping for now.")
        return

    if res.text == "":
        log_err(LogServices.SCRAP, f"ERR: {full_id}. {url} appears to be empty. Skipping for now.")
        return

    if res.text.startswith("%PDF"):
        log_err(LogServices.SCRAP, f"ERR: {full_id}. {url} appears to be of a PDF file. Skipping for now.")
        return

    with open(filepath, "w") as f:
        f.write(res.text)


if __name__ == "__main__":
    pass
