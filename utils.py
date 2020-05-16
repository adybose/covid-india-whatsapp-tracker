import requests
from lxml import html
import constants


def world_tracker():
    url = 'https://www.worldometers.info/coronavirus/'
    doc = get_document(url)
    print(url)
    country_relative_paths = doc.xpath(
        '//table[@id="main_table_countries_today"]/tbody/tr/td[2]/a[contains(@href, "country/")]/@href')
    country_absolute_paths = ['https://www.worldometers.info/coronavirus/' + each for each in country_relative_paths]
    country_absolute_paths.append(url)  # append world page at the end
    print(country_absolute_paths)

    country_names = doc.xpath(
        '//table[@id="main_table_countries_today"]/tbody/tr/td[2]/a[contains(@href, "country/")]/text()')
    country_names = [each.lower() if each != 'India' else '' for each in country_names]  # skipping India for sourcing from different source for India
    country_common_names = constants.country_common_names
    print(country_common_names)
    print(type(country_common_names))
    country_names.append('world')
    print(country_names)

    # country_common_names = [each for each in constants.country_common_names]
    return country_names, country_common_names, country_absolute_paths


def get_document(url):
    response = requests.get(url)
    doc = html.fromstring(response.content)
    return doc


def get_data_message(country, url, doc):
    total, deaths, recovered = doc.xpath('//div[@class="maincounter-number"]/span/text()')
    data_message = f'''
                    *Latest Covid-19 cases from {country.title()}*
Total cases: {total}
Recovered: {recovered}
Deaths: {deaths}
View more: {url}
'''
    return data_message


if __name__ == '__main__':
    world_tracker()
