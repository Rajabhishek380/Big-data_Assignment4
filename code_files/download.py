import subprocess
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import requests
import yaml
from tqdm import tqdm

def download_csv_files(base_url, year, output_file, temp_dir, max_files):
    # Download the HTML file containing CSV hyperlinks for the year
    subprocess.run(["curl", "-L", "-o", output_file, base_url + str(year)])
    
    # Parse the HTML file to extract CSV links
    with open(output_file, 'r') as file:
        html_data = file.read()
        parsed_html = BeautifulSoup(html_data, 'html.parser')
        
        # Find CSV links with corresponding memory size
        csv_links_with_memory = []
        for row in parsed_html.find_all('tr')[2:]:
            columns = row.find_all('td')
            if columns and columns[2].text.strip().endswith('M'):
                csv_link = urljoin(base_url + str(year) + '/', columns[0].text.strip())
                memory = float(columns[2].text.strip().replace('M', ''))
                csv_links_with_memory.append((csv_link, memory))
        
        # Filter CSV links based on memory size
        csv_links_above_45M = [link for link, memory in csv_links_with_memory if memory > 45][:max_files]
        
        # Create temporary directory if it doesn't exist
        os.makedirs(temp_dir, exist_ok=True)
        
        # Download CSV files to the temporary directory
        for link in csv_links_above_45M:
            response = requests.get(link)
            if response.status_code == 200:
                filename = os.path.join(temp_dir, os.path.basename(link))
                total_size = int(response.headers.get('content-length', 0))
                with open(filename, 'wb') as csv_file, tqdm(
                    total=total_size,
                    unit='iB',
                    unit_scale=True,
                    desc=os.path.basename(link)
                ) as progress_bar:
                    for data in response.iter_content(1024):
                        csv_file.write(data)
                        progress_bar.update(len(data))

def main():
    # Load parameters from YAML file
    with open("params.yaml", 'r') as params_file:
        params = yaml.safe_load(params_file)
    
    # Extract parameters
    base_url = params["data_source"]["base_url"]
    year = params["data_source"]["year"]
    output_file = params["data_source"]["output"]
    temp_dir = params["data_source"]["temp_dir"]
    max_files = params["data_source"]["max_files"]
    
    # Download CSV files
    download_csv_files(base_url, year, output_file, temp_dir, max_files)

if __name__ == "__main__":
    main()


