from selenium.webdriver.common.by import By

class MainPageLocators:
    """A class for main page locators.

    All main page locators should live here.
    """
    HORSES_PAGE_LINK = (By.ID, 'menu_link_horses')
    RACES_PAGE_LINK = (By.ID, 'menu_link_races')
    TRACKS_PAGE_LINK = (By.ID, 'menu_link_tracks')
    DEEPNET_PAGE_LINK = (By.ID, 'menu_link_deepnet')
    DATABASE_DROPDOWN = (By.ID, 'database_dropdown')
    DATABASE_PAGE_LINK = (By.ID, 'menu_link_database')
    DATABASE_ADD_FILES_LINK = (By.ID, 'menu_link_database_add_files')

