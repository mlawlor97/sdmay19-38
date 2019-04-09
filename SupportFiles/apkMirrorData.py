from SupportFiles.metaDataBase import DataCollectionBase
from utils import logToFile
from bs4 import Tag, NavigableString


class SortMirrorData():
    # Returns list of hashes in order:
    # Certificate SHA-1, Certificate SHA-256, File MD5, File SHA-1, File SHA-256
    def splitSecurity(sec):
        cert_sha1_index = sec.find('SHA-1')
        cert_sha2_index = sec.find('SHA-256')
        end_cert = sec.find('The cryptographic')

        split_sec = sec[end_cert:]

        file_md5_index = split_sec.find('MD5')
        file_sha1_index = split_sec.find('SHA-1')
        file_sha2_index = split_sec.find('SHA-256')
        end_file = split_sec.find('Verify the file')

        cert_sha1 = sec[cert_sha1_index + 7:cert_sha2_index]
        cert_sha2 = sec[cert_sha2_index + 9:end_cert]

        file_md5 = split_sec[file_md5_index + 5:file_sha1_index]
        file_sha1 = split_sec[file_sha1_index + 7:file_sha2_index]
        file_sha2 = split_sec[file_sha2_index + 9:end_file]

        security_data = [cert_sha1, cert_sha2, file_md5, file_sha1, file_sha2]
        return security_data

    # Returns app specs in order:
    # Version number, Architecture, Package, Number of Downloads, File Size,
    # Minimum Android Version, Target Android Version, and Upload Date
    def splitSpecs(spec):
        find_architecture = False
        version_index = spec.find(')')
        package_index = spec.find('Package')
        if package_index - version_index > 1:
            architecture_index = spec.find('arm')
            find_architecture = True

        downloads_index = spec.find('downloads')
        size_index = spec.find('bytes)')
        min_android_index = spec.find('Min:')
        target_android_index = spec.find('Target:')

        version = spec[10:version_index + 1]

        if find_architecture is True:
            architecture = spec[architecture_index:package_index - 1]
        else:
            architecture = "No architecture found"

        download_sub = spec[package_index:downloads_index]
        real_downloads_index = 0

        for i, c in enumerate(reversed(download_sub)):
            if c.isalpha():
                real_downloads_index = i - 1
                break
        package = spec[package_index + 9:package_index + len(download_sub) - real_downloads_index - 1]
        downloads = spec[package_index + len(download_sub) - real_downloads_index - 1:downloads_index - 1]

        size = spec[downloads_index + 10:size_index + 6]

        min_android = spec[min_android_index + 5:target_android_index - 1]

        target_android_temp_sub = spec[target_android_index:]
        target_android_end_index = target_android_temp_sub.find(')')
        target_android = target_android_temp_sub[8:target_android_end_index + 1]

        uploaded_date_index = target_android_temp_sub.find('Uploaded')

        uploaded_end_index = target_android_temp_sub.find(' at ')

        uploaded_date = target_android_temp_sub[uploaded_date_index + 9:uploaded_end_index]

        spec_data = [version, architecture, package, downloads, size, min_android, target_android, uploaded_date]
        return spec_data


class GetMirrorData(DataCollectionBase):

    def getName(self):
        try:
            headerContents = self.soup.find("div", {"class": "site-header-contents"})
            if headerContents.find("h1", {"class": "marginZero wrapText app-title fontBlack noHover"}):
                t = headerContents.find("h1", {"class": "marginZero wrapText app-title fontBlack noHover"})
                name = t.text
        except AttributeError:
            name = None
            logToFile('NameCheck.txt', self.url)
        self.metaData.update(Name=name)

    def getDeveloper(self):
        try:
            headerContents = self.soup.find("div", {"class": "site-header-contents"})
            if headerContents.find("h3", {"class": "marginZero dev-title wrapText"}):
                n = headerContents.find("h3", {"class": "marginZero dev-title wrapText"})
                a = n.find("a", {"class": None})
                dev = a.text
        except AttributeError:
            dev = None
            logToFile('DeveloperCheck.txt', self.url)
        self.metaData.update(Developer=dev)


    def getDescription(self):
        desc = []
        try:
            tabPane = self.soup.find_all("div", {"class": "notes"})
            if tabPane:
                for note in tabPane:
                    desc.append(note.text)
            descStr = " "
            for d in desc:
                d = d.replace('\n', '').replace('\r', '')
                if d == "" or d == " ":
                    continue
                descStr = descStr + d
        except AttributeError:
            desc = None
            logToFile('DeveloperCheck.txt', self.url)
        self.metaData.update(Description=descStr)


    # def getRating(self):
    #     try:
    #         rating = self.soup.find('span', {'class': 'rating'})
    #         rating = rating.text
    #     except AttributeError:
    #         if self.validApplication:
    #             rating = '0.0'
    #         else:
    #             rating = None
    #             logToFile('RatingCheck.txt', self.url)
    #     self.metaData.update(Rating=rating)
    #
    # def getTags(self):
    #     tags = []
    #     try:
    #         tagList = self.soup.find('ul', {'class': 'tag_list'})
    #         tagList = tagList.find_all('li')
    #         for tag in tagList:
    #             if tag.text:
    #                 tags.append(tag.text)
    #     except AttributeError:
    #         tags = None
    #         logToFile('TagCheck.txt', self.url)
    #     self.metaData.update(Tags=tags)

    def getSecurity(self):
        sec = []
        try:
            shaAndSig = self.soup.find_all("div", {"class": "modal-body"})
            if shaAndSig:
                for s in shaAndSig[1]:
                    if isinstance(s, NavigableString):
                        sec.append(s)
                    else:
                        sec.append(s.text)
            secStr = " "
            for se in sec:
                se = se.replace('\n', '').replace('\r', '')
                if se == "" or se == " ":
                    continue
                secStr = secStr + se
            secArr = SortMirrorData.splitSecurity(secStr)
            self.metaData.update(Certificate_SHA1=secArr[0])
            self.metaData.update(Certificate_SHA256=secArr[1])
            self.metaData.update(File_MD5=secArr[2])
            self.metaData.update(File_SHA1=secArr[3])
            self.metaData.update(File_SHA256=secArr[4])
        except AttributeError:
            sec = None
            logToFile('SecurityCheck.txt', self.url)

    def getSpecs(self):
        specs = []
        try:
            author = self.soup.find_all("div", {"class": "appspec-value"})
            if author:
                for m in author:
                    if isinstance(m, NavigableString):
                        specs.append(m)
                    else:
                        specs.append(m.text)
            specsStr = " "
            for sp in specs:
                sp = sp.replace('\n', '').replace('\r', '')
                if sp == "" or sp == " ":
                    continue
                specsStr = specsStr + sp
            specsArr = SortMirrorData.splitSpecs(specsStr)
            self.metaData.update(VersionNumber=specsArr[0])
            self.metaData.update(Architecture=specsArr[1])
            self.metaData.update(Package=specsArr[2])
            self.metaData.update(Donwloads=specsArr[3])
            self.metaData.update(FileSize=specsArr[4])
            self.metaData.update(MinAndroid=specsArr[5])
            self.metaData.update(TargetAndroid=specsArr[6])
            self.metaData.update(UploadDate=specsArr[7])

        except AttributeError:
            specs = None
            logToFile('SpecsCheck.txt', self.url)
        self.metaData.update(Specs=specs)



