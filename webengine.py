import sys
import os
import shutil
from touch import touch
from PyQt6.QtCore import QUrl, Qt, QDateTime
from PyQt6.QtCore import pyqtSlot as Slot
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QApplication, QLineEdit,
                             QMainWindow, QPushButton, QToolBar)
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings, QWebEngineProfile
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtNetwork import QNetworkCookie


class CookiesManager(object):
    def __init__(self, browser_view):
        self.browser_view = browser_view

        self.cookies_dir = os.getcwd() + '/.cookies/'

        # Both session and persistent cookies are stored in memory
        self.browser_view.page().profile().setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)

        self.cookie_store = self.browser_view.page().profile().cookieStore()

        self.cookie_store.cookieAdded.connect(self.add_cookie)      # save cookie to disk when captured cookieAdded signal
        self.cookie_store.cookieRemoved.connect(self.remove_cookie) # remove cookie stored on disk when captured cookieRemoved signal
        self.browser_view.loadStarted.connect(self.load_cookie)     # load disk cookie to QWebEngineView instance when page start load


    def add_cookie(self, cookie):
        '''Store cookie on disk.'''
        cookie_domain = cookie.domain()
        if not cookie.isSessionCookie():
            cookie_file = os.path.join(self.cookies_dir, cookie_domain, self._generate_cookie_filename(cookie))
            if not os.path.exists(self.cookies_dir + cookie_domain):
                os.makedirs(self.cookies_dir + cookie_domain)
            touch(cookie_file)

            # Save newest cookie to disk.
            with open(cookie_file, "wb") as f:
                f.write(cookie.toRawForm())

    def load_cookie(self):
        ''' Load cookie file from disk.'''
        if not os.path.exists(self.cookies_dir):
            return

        all_cookies_domain = os.listdir(self.cookies_dir)

        for domain in filter(self.domain_matching, all_cookies_domain):
            domain_dir = os.path.join(self.cookies_dir, domain)
            for cookie_file in os.listdir(domain_dir):
                with open(os.path.join(domain_dir, cookie_file), "rb") as f:
                    for cookie in QNetworkCookie.parseCookies(f.read()):
                        if not domain.startswith('.'):
                            if self.browser_view.url().host() == domain:
                                # restore host-only cookie
                                cookie.setDomain('')
                                self.cookie_store.setCookie(cookie, self.browser_view.url())
                                print("Restore host-only cookie")
                        else:
                            self.cookie_store.setCookie(cookie)
                            print("Cookie Load")

    def remove_cookie(self, cookie):
        ''' Delete cookie file.'''
        if not cookie.isSessionCookie():
            cookie_file = os.path.join(self.cookies_dir, cookie.domain(), self._generate_cookie_filename(cookie))

            if os.path.exists(cookie_file):
                # os.remove(cookie_file)
                # print("Cookies Removed")
                pass
    def delete_all_cookies(self):
        ''' Simply delete all cookies stored on memory and disk.'''
        self.cookie_store.deleteAllCookies()
        if os.path.exists(self.cookies_dir):
            shutil.rmtree(self.cookies_dir)
        print("All Cookies Deleted")
    def delete_cookie(self):
        ''' Delete all cookie used by current site except session cookies.'''
        from PyQt6.QtNetwork import QNetworkCookie
        import shutil

        cookies_domain = os.listdir(self.cookies_dir)

        for domain in filter(self.get_relate_domains, cookies_domain):
            domain_dir = os.path.join(self.cookies_dir, domain)

            for cookie_file in os.listdir(domain_dir):
                with open(os.path.join(domain_dir, cookie_file), "rb") as f:
                    for cookie in QNetworkCookie.parseCookies(f.read()):
                        self.cookie_store.deleteCookie(cookie)
            shutil.rmtree(domain_dir)
        print("Cookies Deleted")

    def domain_matching(self, cookie_domain):
        ''' Check if a given cookie's domain is matching for host string.'''

        cookie_is_hostOnly = True
        if cookie_domain.startswith('.'):
            # get rid of prefixing dot when matching domains
            cookie_domain = cookie_domain[1:]
            cookie_is_hostOnly = False

        host_string = self.browser_view.url().host()

        if cookie_domain == host_string:
            # The domain string and the host string are identical
            return True

        if len(host_string) < len(cookie_domain):
            # For obvious reasons, the host string cannot be a suffix if the domain
            # is shorter than the domain string
            return False

        if host_string.endswith(cookie_domain) and host_string[:-len(cookie_domain)][-1] == '.' and not cookie_is_hostOnly:
            # The domain string should be a suffix of the host string,
            # The last character of the host string that is not included in the
            # domain string should be a %x2E (".") character.
            # and cookie domain not have prefixing dot (host-only cookie is not for subdomains)
            return True

        return False

    def get_relate_domains(self, cookie_domain):
        ''' Check whether the cookie domain is located under the same root host as the current URL host.'''
        import tld, re

        host_string = self.browser_view.url().host()

        if cookie_domain.startswith('.'):
            cookie_domain = cookie_domain[1:]

        base_domain = tld.get_fld(host_string, fix_protocol=True, fail_silently=True)

        if not base_domain:
            # check whether host string is an IP address
            if re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$').match(host_string) and host_string == cookie_domain:
                return True
            return  False

        if cookie_domain == base_domain:
            return True

        if cookie_domain.endswith(base_domain) and cookie_domain[:-len(base_domain)][-1] == '.':
            return True

        return False

    def _generate_cookie_filename(self, cookie):
        ''' Gets the name of the cookie file stored on the hard disk.'''
        name = cookie.name().data().decode("utf-8")
        domain = cookie.domain()
        encode_path = cookie.path().replace("/", "|")

        return name + "+" + domain + "+" + encode_path


class WebBrowser(QMainWindow):

    def __init__(self, url: str, *args, **kwargs):
        super(WebBrowser, self).__init__(*args, **kwargs)
        self.url = url
        self.setWindowTitle('WebEngine')
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.toolBar = QToolBar()
        self.addToolBar(self.toolBar)
        self.backButton = QPushButton()
        self.backButton.setIcon(QIcon(':/qt-project.org/styles/commonstyle/images/left-32.png'))
        self.backButton.clicked.connect(self.back)
        self.toolBar.addWidget(self.backButton)
        self.forwardButton = QPushButton()
        self.forwardButton.setIcon(QIcon(':/qt-project.org/styles/commonstyle/images/right-32.png'))
        self.forwardButton.clicked.connect(self.forward)
        self.toolBar.addWidget(self.forwardButton)

        self.addressLineEdit = QLineEdit()
        self.addressLineEdit.returnPressed.connect(self.load)
        self.toolBar.addWidget(self.addressLineEdit)
        self.closeButton = QPushButton()
        self.closeButton.setIcon(QIcon.fromTheme("application-exit"))
        self.closeButton.clicked.connect(self.Exit)
        self.toolBar.addWidget(self.closeButton)

        self.webEngineView = QWebEngineView()
        self.cookies_manager = CookiesManager(self.webEngineView)
        self.setCentralWidget(self.webEngineView)
        self.webEngineView.settings().setAttribute(QWebEngineSettings.WebAttribute.SpatialNavigationEnabled, True)
        self.webEngineView.settings().setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        self.webEngineView.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        self.webEngineView.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        self.webEngineView.settings().setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        self.webEngineView.settings().setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)

        if self.url == "":
            initialUrl = 'https://youtube.com'
        else:
            initialUrl = self.url
        self.addressLineEdit.setText(initialUrl)
        self.webEngineView.load(QUrl(initialUrl))
        self.webEngineView.page().titleChanged.connect(self.setWindowTitle)
        self.webEngineView.page().urlChanged.connect(self.urlChanged)
        self.webEngineView.page().loadFinished.connect(self.handle_load_finished)

    def handle_load_finished(self, ok):
        if ok:
            print("Page loaded successfully")
            self.cookies_manager.load_cookie()
        else:
            print("Could not load page")
    @Slot()
    def load(self):
        url = QUrl.fromUserInput(self.addressLineEdit.text())
        if url.isValid():
            self.webEngineView.load(url)

    @Slot()
    def back(self):
        self.webEngineView.page().triggerAction(QWebEnginePage.Back)

    @Slot()
    def forward(self):
        self.webEngineView.page().triggerAction(QWebEnginePage.Forward)

    @Slot(QUrl)
    def urlChanged(self, url):
        self.addressLineEdit.setText(url.toString())

    @staticmethod
    def Exit(self):
        sys.exit(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    try:
        url = sys.argv[1]
    except IndexError:
        url = ""
    mainWin = WebBrowser(url)
    availableGeometry = mainWin.screen().availableGeometry()
    mainWin.showMaximized()
    sys.exit(app.exec())
