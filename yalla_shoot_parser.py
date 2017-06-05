import requests
import bs4
import urllib.request
import shutil


def get_matches_list(day_flag):
    if day_flag == 'today':
        try:
            yalla_page = requests.get('http://www.yalla-shoot.com/live/index.php')
        except:
            return [[' ', 'لا يوجد اتصال بالإنترنت', ' ']]
    elif day_flag == 'tomorrow':
        try:
            yalla_page = requests.get('http://www.yalla-shoot.com/live/tomorrow_matches.php')
        except:
            return [[' ', 'لا يوجد اتصال بالإنترنت', ' ']]
    elif day_flag == 'yesterday':
        try:
            yalla_page = requests.get('http://www.yalla-shoot.com/live/yesterday_matches.php')
        except:
            return [[' ', 'لا يوجد اتصال بالإنترنت', ' ']]

    soup = bs4.BeautifulSoup(yalla_page.text, "html.parser")
    matchelem = soup.select('a.matsh_live')
    matches_list = []
    images_list = shutil.os.listdir('./Images')
    for elem in matchelem:
        soup = bs4.BeautifulSoup(str(elem), "html.parser")
        # Here we will select some elements from yallashoot 
        match_link = elem.attrs['href']
        match_link = 'http://www.yalla-shoot.com/live/' + match_link
        tournament = soup.select('td[align="right"] > p')
        team_names = soup.select('td.fc_name')
        match_time = soup.select('span.fc_time')
        right_icon = soup.select('td[align="right"] > img')
        left_icon = soup.select('td[align="left"] > img')

        # convert the teams symbols from relative paths to absolute
        if right_icon[0].attrs['src'].startswith('../'):
            right_url = right_icon[0].attrs['src'].replace('../', 'http://yalla-shoot.com/')
        if left_icon[0].attrs['src'].startswith('../'):
            left_url = left_icon[0].attrs['src'].replace('../', 'http://yalla-shoot.com/')
        
        # We need this object to set a custom header and then download the images
        opener = urllib.request.URLopener()
        opener.addheader('User-Agent', 'Mozilla/5.0')
        right_image = right_url.replace('http://yalla-shoot.com/images/upload/images/', '')
        left_image = left_url.replace('http://yalla-shoot.com/images/upload/images/', '')

        # Download the image if it does not exist already in Images folder 
        if right_image not in images_list:
            right_filename, header = opener.retrieve(right_url, filename=right_url.replace(
                'http://yalla-shoot.com/images/upload/images/', './Images/'))
        else:
            right_filename = './Images/' + right_image
        if left_image not in images_list:
            left_filename, header = opener.retrieve(left_url, filename=left_url.replace(
                'http://yalla-shoot.com/images/upload/images/', './Images/'))
        else:
            left_filename = './Images/' + left_image
        if len(match_time[0].text.strip()) < 7:
            match_time = match_time[0].text.strip()[::-1]
        else:
            match_time = match_time[0].text.strip()[:5].strip()
        full_match = team_names[1].text.strip() + " " +\
            match_time + " " + team_names[0].text.strip() + "\n" + tournament[0].text.strip()
        matches_list.append([left_filename, team_names[1].text, match_time, team_names[0].text, right_filename, match_link, tournament[0].text])
    return matches_list


if __name__ == '__main__':
    matches_list = get_matches_list('yesterday')
    print('\n', matches_list)
    matches_list = get_matches_list('today')
    print('\n', matches_list)
    matches_list = get_matches_list('tomorrow')
    print('\n', matches_list)
