import requests
import urllib.request
import re
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError, RequestException



visited_pages = set()
external_links = set()
dead_links = set()
base_url = "https://ngbank.com/"


def check_links(url, referer, output_filename, max_depth, depth):
    """
    Recursively check all links on the given URL (and its sub-pages up to a given depth) for dead external links
    """
    try:
        # Make a get request to the URL to check for a valid response
        response = requests.get(url)
    
    except RequestException:
        print(f"Skipping URL: {url} - Invalid URL")
    
    if is_external_link(base_url, url):
        if response.status_code != 200:
            dead_links.add(f"DEAD EXTERNAL LINK: {url} \nCODE: {response.status_code}\nREFERENCE: {referer} \n")
            print(f'URL-EXT RESPONSE {response.status_code}')
        return
    if response.status_code != 200:
        if url not in dead_links:
            dead_links.add(f"DEAD INTERNAL LINK: {url} \nCODE: {response.status_code} \nREFERENCE:{referer} \n")
            print(f'URL-INT RESPONSE {response.status_code}')              
        return
    
    if url not in visited_pages:
        visited_pages.add(url)
        
    
    # Add the current page to the set of visited pages
        # Use BeautifulSoup to parse the HTML and find all links on the page
    soup = BeautifulSoup(response.text, 'html.parser')
    links = [link.get('href') for link in soup.find_all('a')]
    
    
    # Check each link for validity
    for i, element in enumerate(links):
        link= requests.compat.urljoin(url, element)
        print(link)
        
        try:
            link_response = requests.get(link)
        except RequestException:
            print(f"Skipping URL: {link} - Invalid URL")
            continue
        #check if response fails
        if "https://www.google.com/maps" in link or "tel:" in link:
            continue
        if is_external_link(base_url, url):
            if response.status_code != 200:
                dead_links.add(f"DEAD EXTERNAL LINK: {link} \nCODE: {link_response.status_code}\nREFERENCE: {referer} \n")
                print(f'URL-EXT RESPONSE {link_response.status_code}')

        if link_response.status_code != 200:
            if link not in dead_links:
                dead_links.add(f"DEAD EXTERNAL LINK: {link} \nCODE: {link_response.status_code}\nREFERENCE: {referer}\n")
                print(f'LINK RESPONSE {link_response.status_code}')
        
        
        print(len(dead_links))
        # If the link is an internal link and we have not already visited it, recursively check its links
        if link not in visited_pages and depth < max_depth:
            depth +=1
            check_links(link, url, output_filename, max_depth, depth)
        
        
def is_external_link(base_url, link_url):
    """
    Check whether the given link URL is an internal link relative to the given base URL
    """
    base_domain = get_domain(base_url)
    external_domain = get_domain(link_url)
    return base_domain != external_domain
def get_domain(url):
    """
    Extract the domain name from the given URL
    """
    match = re.search(r'^(?:https?:\/\/)?(?:[^@\/\n]+@)?(?:www\.)?([^:\/\n]+)', url)
    return match.group(1)





def main():

    url = base_url
    output_filename = "results.txt"
    # Initialize the set of external links and visited pages
    with open(output_filename, 'w') as output_file:
        # Call the check_links function on the URL, passing external_only=True to only check external links
        check_links(url, url, output_filename, 20,0)
        for i in dead_links:
            output_file.write(str(i) + "\n")
    # Call the check_links function on the URL to recursively check all internal pages for external links
    #check_links(url, output_file, external_links, visited_pages)
    
    
    
        

    

if __name__ == '__main__':
    main()
