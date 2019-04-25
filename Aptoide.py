from utils import *
from SupportFiles.AptoideAppData import GetAptoideAppData
from SupportFiles.AptoideData import GetAptoideData

# Ok bear with me here,
# The minimum search criteria on Aptoide is 2 characters,
# so I figure, get all the possible pairs of numbers/letters
# and search using those pairs. Sue me.
def crawl():
    url_begin = "https://co.aptoide.com/search/view?search="
    url_end = "&x=0&y=0"
    first_letter_counter = 0
    second_letter_counter = 0
    first_number = 0
    second_number = 0
    visitedLinks = set()

    # all pairs of letters
    while first_letter_counter < 26:
        first_letter = chr(97+first_letter_counter)
        while second_letter_counter < 26:
            second_letter = chr(97+second_letter_counter)
            url = url_begin + first_letter + second_letter + url_end
            findLinks(url)
            second_letter_counter += 1
        first_letter_counter += 1
        second_letter_counter = 0

    # all pairs of numbers
    while first_number < 10:
        while second_number < 10:
            url = url_begin + chr(first_number) + chr(second_number) + url_end
            # findLinks(url)
            second_number += 1
        first_number += 1
        second_number = 0

    second_letter_counter = 0
    first_number = 0

    # all pairs, number then letter
    while first_number < 10:
        while second_letter_counter < 26:
            second_letter = chr(97 + second_letter_counter)
            url = url_begin + chr(first_number) + second_letter + url_end
            # findLinks(url)
            second_letter_counter +=1
        first_number += 1
        second_letter_counter = 0

    first_letter_counter = 0
    second_number = 0

    # all pairs, letter then number
    while first_letter_counter < 26:
        first_letter = chr(97 + first_letter_counter)
        while second_number < 10:
            url = url_begin + first_letter + chr(second_number) + url_end
            # findLinks(url)
            second_number +=1
        first_letter_counter += 1
        second_number = 0


# Calls function in utility file to find all the app links on a given page
def findLinks(url):
    links = scrollToBottom(url)

    for l in links:
        getMoreVersions(l)


# Gets info on the base app and finds all the versions for a given app
def getMoreVersions(url):
    soup = requestHTML(url)

    # Get base app first
    common_data = getBaseApp(url, soup)
    app_name = common_data[0]
    app_id = common_data[1]

    # open up the versions list
    url_versions = url + "/versions"
    version_links = []
    more_pages = True

    # Obtain links to all the versions
    while more_pages:
        soup_versions = requestHTML(url_versions)
        version_link_soup = soup_versions.find_all("span", {"class": "bundle-info--version"})

        for v in version_link_soup:
            a = v.find("a", {"class": None})
            version_links.append(a.get("href"))

        next_button = soup_versions.find("div", {"class": "widget-pagination__next"})
        if next_button.find("a"):
            next_page = next_button.find("a").get("href")
            url_versions = next_page
            continue
        else:
            more_pages = False

    # Open every version
    for vl in version_links:
        openVersion(vl, app_name, app_id)


# Open versions and get their info and write them to the db
def openVersion(link, app_name, app_id):
    soup = requestHTML(link)


    versionDataSite = GetAptoideData(link, soup).getAll()
    vnumber = versionDataSite.get('Version')

    # check that version doesn't already exist in db
    # version_entry = checkVersionDB(app_id, vnumber)
    # if version_entry is None:
        # id_version = writeVersionDB("Aptoide", app_name, app_id, vnumber, versionDataSite)


# Getting the base app is just getting the most recent app
def getBaseApp(url, soup):
    # app_entry = checkAppDB(url)
    app_entry = 0
    common_data = []

    # if app already exists skip all the hard stuff
    if app_entry is 0:

        popup_arr = openPopups(soup)

        detailed_info = popup_arr[0]
        package_location = detailed_info[7]

        index = 0
        package = ""
        package_rows = package_location.find_all("td")
        for p in package_rows:
            if index == 1:
                package = p.text
                break
            else:
                index += 1

        name = soup.find("h1", {"class": "header__title"}).text
        common_data.append(name)

        appDataSite = GetAptoideAppData(url, soup).getAll()
        # idApp = writeAppDB("Aptoide", name, url, package, appDataSite)
        idApp = 0
        common_data.append(idApp)
        return common_data

    # if app already exists pull its info from the db
    else:
        idApp = app_entry.get('app_id')
        name = app_entry.get('app_name')
        common_data.append(name)
        common_data.append(idApp)
        return common_data


# this open popups for the base app function, uses the same code as the versions does to open the popups
def openPopups(soup):
    popup_arr = []

    # detailed info rows
    detailed_info = soup.find_all("tr", {"class": "app-info__row"})
    popup_arr.append(detailed_info)

    # permissions
    permissions = soup.find_all("div", {"class": "app-permissions__row"})
    popup_arr.append(permissions)

    return popup_arr


# this is a main function, in coding a main function is the function that starts everything, isn't coding fun
def main():
    crawl()



if __name__ == '__main__':
    main()
