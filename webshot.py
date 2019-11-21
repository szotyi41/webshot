#!/usr/bin/python
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import logging
import os, sys

urls = []
directory = datetime.today().strftime('%Y-%m-%d-%H:%M')

removeCookiebar = True
headlessChrome = True
readFromFile = True
screenWidth = 1280

if (len(sys.argv) > 1):
	readFromFile = False
	urls = [sys.argv[1]]

logger = logging.getLogger('webshot')
logging.basicConfig(filename='logs.txt', filemode='a', format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S', level=logging.INFO)

def log(string, type='info'):
	logger.info(string)
	print(string)

def open_from_file(file='urls.txt'):
	f = open(file, 'r')
	lines = f.readlines()
	f.close()
	return lines

def start(urls = [], restart = False):

	global removeCookiebar, headlessChrome, readFromFile, screenWidth

	success = 0
	failed = []

	for url in urls:
		url = url.strip()
		filename = get_filename(url)

		try: 
			log('Open in chrome: ' + url + ' (' + str(success + 1) + '/' + str(len(urls)) + ')')
			driver = open_url_chrome(url)

			try:
				log('Create screenshot from ' + url)

				if (check_access_denied(driver)):
					log('Access denied page detected :(')
					failed.append(url)

				take_screenshot(driver, filename, screenWidth)
				log('Screenshot created successfully. ' + filename)
				success += 1
			except Exception as e:
				log(e)
				log('Failed to take screenshot ' + url)
				failed.append(url)

		except Exception as e:
			log(e)
			log('Failed to open url ' + url)
			failed.append(url)

	log(str(success) + ' screenshots created successfully of ' + str(len(urls)) + '. Failed: ' + str(len(failed)))
	
	# Try again without cookiebar remove and headless chrome
	if (restart == False) and (len(failed) > 0):
		removeCookiebar = False
		log('Try again take screenshots from ' + str(len(failed)) + ' failed pages')
		start(failed, True)
		if (len(failed) > 0):
			log('Failed pages: ' + ' '.join(failed))
	

# Generate filepath from url
def get_filename(url):
	url = url.replace('https://', '')
	url = url.replace('http://', '')
	url = url.replace('www.', '')
	url = url.replace('.', '_')
	url = url.replace('/', '')

	if os.path.isdir(directory) == False:
		os.mkdir(directory);

	return directory + '/' + url + '.png'

# Open url in chrome
def open_url_chrome(url):
	options = Options()
	if (headlessChrome == True):
		options.add_argument('--headless')
		options.add_argument('--start-maximized')

	driver = webdriver.Chrome(options=options)
	driver.maximize_window()
	driver.get(url)

	return driver

# Open url in firefox
def open_url_firefox(url):
	driver = webdriver.Firefox()
	driver.maximize_window()
	driver.get(url)
	time.sleep(10)

	return driver

# Remove cookiebar and modals
def remove_cookiebar(driver):
	driver.execute_script('try {var elements = document.body.querySelectorAll("*"); var removeWithIdClassName = ["cookie", "modal", "popup", "window"]; for (var i = 0; i < elements.length; i++) {var el = elements[i]; var st = getComputedStyle(el); var ci = ((el.id) ? el.id.toString().toLowerCase() : "") + ((el.className) ? el.className.toString().toLowerCase() : ""); for (var j = 0; j < removeWithIdClassName.length; j++) {if (ci.indexOf(removeWithIdClassName[j]) !== -1) {if (el) el.remove(); } } if ((el) && (st) && ((st.position === "fixed") || (st.position === "sticky")) && (st.bottom && parseInt(st.bottom) < 100)) {el.remove(); } } } catch (e) {}')

def take_screenshot(driver, filename, screen_width):
	driver.set_window_size(screen_width, 800)
	time.sleep(10)
	page_height = calculate_page_height(driver)
	log('Page size: ' + str(screen_width) + 'x' + str(page_height))
	driver.set_window_size(screen_width, int(page_height))
	driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
	driver.execute_script('window.scrollTo(0, 0)')
	time.sleep(10)

	if (removeCookiebar == True):
		remove_cookiebar(driver)

	driver.save_screenshot(filename)
	driver.quit()

def calculate_page_height(driver):
	try:
		body = driver.find_element_by_tag_name('body')
		html = driver.find_element_by_tag_name('html')
		body_height = int(body.size['height'])
		html_height = int(html.size['height'])
		scroll_height = int(driver.execute_script('return document.body.scrollHeight'))
		return max(body_height, scroll_height, html_height, 800)
	except Exception as e:
		return 3000

def check_access_denied(driver):
	text = driver.find_element_by_tag_name('body').text
	if text:
		text = text.lower()
		return text.find('denied') != -1 or text.find('forbidden') != -1

	return False

if (readFromFile == True):
	urls = open_from_file('urls.txt')

log('Webshot started to create ' + str(len(urls)) + ' screenshot(s)')
start(urls)
log('Webshot finished successfully')
