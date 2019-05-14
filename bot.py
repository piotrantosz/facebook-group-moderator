from selenium import webdriver
import time


import json



USERNAME = 'YOUR_USERNAME'
PASSWORD = 'YOUR_PASSWORD'
GROUP_NAME = 'GROUP_NAME'
# visit mbasic.facebook.com, go to your group, copy numbers after /groups/GROUP_ID?not_important_things
GROUP_ID = 'GROUP_ID'
# if post contains one of this words, it will be accepted
# use many dicts for multiple word "forms"
PHRASES = [
    ['dog', 'doggo', 'doggy'],
    ['cat', 'catty', 'kitty'],
    ['bla', 'blah', 'blahh'],
]



def authenticate():
    """
    Uses mbasic.facebook.com
    website to authenticate user
    """
    browser.get('https://mbasic.facebook.com/')
    element = browser.find_elements_by_id('m_login_email')
    element[0].send_keys(USERNAME)
    element = browser.find_element_by_name('pass')
    element.send_keys(PASSWORD)
    log_in = browser.find_elements_by_name('login')
    log_in[0].click()


def crawl_posts():
    """
    Create list of objects
    containing each pending
    post request
    :return: List of posts as dictionaries
    """
    browser.get('https://mbasic.facebook.com/groups/' + GROUP_ID + '/madminpanel/pending/?_rdr')
    result = []
    # article == post
    posts = browser.find_elements_by_xpath("//div[@role = 'article']")

    # detach from DOM
    posts_data = [post.get_attribute('data-ft') for post in posts]  # also do not call multiple things "link"
    posts_text = [(post.text).replace('Full Story · Save · More', '') for post in posts]

    if (len(posts_data) != len(posts_text)):
        print('posts_data != posts_text')
        exit(1)

    for i in range(len(posts_data)):
        if (posts_data[i]):
            # get ID
            data_attribute = json.loads(posts_data[i])
            top_level_post_id = data_attribute["top_level_post_id"]

            # get URL
            url = 'https://mbasic.facebook.com/groups/' + GROUP_ID + '?view=permalink&id=' + top_level_post_id

            # get CONTENT
            content = posts_text[i]
            if 'More' in content:
                browser.get(url)
                post_page_content = browser.find_element_by_xpath("//div[@id = 'm_story_permalink_view']")
                content = post_page_content.text

            content = content.replace(GROUP_NAME, '')
            content = content.replace('Full Story · Save · More', '')
            content = content.replace('>', '')
            content = content.lower()

            result.append({
                'top_level_post_id': top_level_post_id,
                'url': url,
                'content': content

            })

    return result


def analyze_posts(posts):
    """
    Check each post to determine
    if it's about wheels
    :return: list of (id's) accepted posts
    """


    accepted_posts = []

    for post in posts:
        for phrase in PHRASES:
            if (LinearSearch(phrase, post['content'])):
                accepted_posts.append(post['top_level_post_id'])

    accepted_posts = list(set(accepted_posts))


    return accepted_posts


def accept_posts(accepted_posts):
    browser.get('https://mbasic.facebook.com/groups/' + GROUP_ID + '/madminpanel/pending/?_rdr')
    # article == post
    all_posts = browser.find_elements_by_xpath("//div[@role = 'article']")
    for post in all_posts:
        if (post.get_attribute('data-ft')):
            post_id = json.loads(post.get_attribute('data-ft'))["top_level_post_id"]
            if post_id in accepted_posts:
                approve = post.find_element_by_xpath(".//input[@value = 'Approve']")
                approve.click()
                return
            else:
                approve = post.find_element_by_xpath(".//input[@value = 'Delete']")
                approve.click()
                return


def LinearSearch(lys, element):
    for i in range(len(lys)):
        if (lys[i]).lower() in element:
            return True
    return False


while True:
    chrome_options = webdriver.ChromeOptions()
    prefs = {'profile.default_content_setting_values.notifications': 2}
    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_argument("--start-maximized")

    browser = webdriver.Chrome()
    try:
        authenticate()
        posts = crawl_posts()
        accepted_posts = analyze_posts(posts)
        for post in posts:
            accept_posts(accepted_posts)
        browser.close()
        time.sleep(600)
    except Exception as e:
        print(e)
        browser.close()
