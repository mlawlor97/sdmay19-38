from SupportFiles.metaDataBase import DataCollectionBase
from utils import logToFile


class OpenPopups:

    def open(soup):
        popup_arr = []

        # detailed info rows
        detailed_info = soup.find_all("tr", {"class": "app-info__row"})
        popup_arr.append(detailed_info)

        # permissions
        permissions = soup.find_all("div", {"class": "app-permissions__row"})
        popup_arr.append(permissions)

        return popup_arr



class GetAptoideData(DataCollectionBase):

    def getDescription(self):
        desc = ""
        try:
            desc = self.soup.find("p", {"itemprop": "description"}).text
            desc = desc.replace('\n', '').replace('\r', '').replace('\t', '')
        except AttributeError:
            desc = None
            logToFile('DeveloperCheck.txt', self.url)
        self.metaData.update(Description=desc)

    def getPublisher(self):
        pub = self.soup.find("span", {"itemprop": "publisher"}).text
        pub = pub.replace('\n', '').replace('\r', '')
        self.metaData.update(Publisher=pub)

    def getCompatibility(self):
        op_sys = self.soup.find("span", {"itemprop": "operatingSystem"}).text
        self.metaData.update(Compatibility=op_sys)

    def getPermissions(self):
        perm = OpenPopups.open(self.soup)[1]
        permission_arr = []

        for p in perm:
            permission_arr.append(p.find_all("span")[0].text)

        self.metaData.update(Permissions=permission_arr)




    def getDetailedInfo(self):
        detailed_info = OpenPopups.open(self.soup)[0]
        detail_arr = []

        for d in detailed_info:
            info = d.find_all("td")
            index = 0
            for i in info:
                if index == 1:
                    detail_arr.append(i.text)
                    break
                else:
                    index += 1

        if detail_arr[6] is "":
            detail_arr[6] = "Not listed"

        self.metaData.update(Size=detail_arr[1])
        self.metaData.update(Downloads=detail_arr[2])
        self.metaData.update(Version=detail_arr[3])
        self.metaData.update(Date=detail_arr[4])
        self.metaData.update(MinScreen=detail_arr[5])
        self.metaData.update(Supported_CPU=detail_arr[6])

        self.metaData.update(MD5=detail_arr[8])
        self.metaData.update(SHA1=detail_arr[9])
        self.metaData.update(Developer=detail_arr[10])
        self.metaData.update(Organization=detail_arr[11])
        self.metaData.update(Locality=detail_arr[12])
        self.metaData.update(Country=detail_arr[13])
        self.metaData.update(State_or_City=detail_arr[14])


    def getStore(self):
        store = self.soup.find("span", {"class": "header__store-name"}).text
        self.metaData.update(Store=store)

    def getRating(self):
        rating_div = self.soup.find("div", {"class": "user-ratings-circle__number"})
        rating = rating_div.find("span").text
        self.metaData.update(Rating=rating)


