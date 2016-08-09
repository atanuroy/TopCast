__author__ = 'aroy'


import argparse
from bs4 import BeautifulSoup
import requests
import urllib


def main(id, typ):
    pid = id
    if typ == 'name':
        pid = findNID(id)

    if pid == '-1':
        exit()

    d_m_250 = dictTop250()
    findFilms(d_m_250, pid)




# Find nameID from a search string
# Returns the nameID nm######## or -1 if it fails to find a name

def findNID(search_item):
    search_item = urllib.quote_plus(search_item)
    search_url = 'http://www.imdb.com/find?q=' + search_item
    s_response = requests.get(search_url)
    s_html = s_response.content
    s_soup = BeautifulSoup(s_html, 'lxml')
    findname = s_soup.findAll('div', attrs={'class': 'findSection'})
    flag_name = False
    for eachname in findname:
        c = eachname.findChild('h3', attrs={'class':'findSectionHeader'}).findChild('a')['name']
        if c == 'nm':
            flag_name = True
            name_result = eachname.find('td', attrs = {'class':'result_text'})
            print 'IMDB found ', name_result.find('a', href=True).contents[0], 'with URL: ', 'http://www.imdb.com/name/' + name_result.find('a', href=True)['href'].split('/')[2]
            return name_result.find('a', href=True)['href'].split('/')[2]
    if not(flag_name):
        print 'IMDB couldn\'t find a film personality with your search string and thus exiiting'
        return '-1'

# Creates a dictionary of all top 250 movies

def dictTop250():
    url = 'http://www.imdb.com/chart/top'
    response = requests.get(url)
    html = response.content
    soup = BeautifulSoup(html, 'lxml')

    # get the table for the top 250

    table = soup.find('div', attrs={'class': 'lister'})
    tid_name_rank_dict = {}
    for row in table.findAll('tr'):
    #     print row
        title = row.find('td', attrs={'class':'titleColumn'})
        if title is not None:
    #         print title
            rank =  int(title.next.strip(' \n.'))

            title_vals = title.find('a', href = True)
            tid = title_vals['href'].split('/')[2]
            tid = tid.strip('\'')
            name = title_vals.contents

    #         Create the dictionaries
            tid_name_rank_dict[tid] = (name, rank)

    return tid_name_rank_dict

# Find top 250 movies in which the person appears
def findFilms(tid_name_rank_dict, pid):
    url = 'http://www.imdb.com/name/' + pid
    response = requests.get(url)
    html = response.content
    soup_name = BeautifulSoup(html, 'lxml')
    name = soup_name.find('span', attrs={'class': 'itemprop'}).contents[0]
    jumpto = soup_name.find('div', attrs={'id': 'jumpto'})
    types = jumpto.findAll('a')
    filmg = soup_name.find('div', attrs={'id': 'filmography'})
    # print filmg
    categories = filmg.findAll('div', attrs={'class': 'filmo-category-section'})

    flag = True
    for t,category in zip(types, categories):
    #     print t.contents[0]
        movies = category.findAll('b')
    #     print len(movies)
        list_of_types = []
        for movie in movies:
    #         tid_l = '\'' +  movie.contents[0]['href'].split('/')[2] + '\''
            tid_l = unicode(movie.contents[0]['href'].split('/')[2], "utf-8")
    #         print tid_l
    #         print movie.contents[0].contents[0]
            if tid_l in tid_name_rank_dict:
    #             print '-------\n\n'
                list_of_types.append(tid_name_rank_dict[tid_l])

        if len(list_of_types) > 0:
            flag = False
            print name, 'As', t.contents[0]
            sorted_list_movies = sorted(list_of_types, key = lambda x: x[1])
            for mov, rank in sorted_list_movies:
                print rank, mov[0]
            print '----------\n'

    if flag:
        print 'Sorry', name, 'doesn\'t appear in any Top 250 movie'



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Input for Top Cast')
    ip_grp = parser.add_mutually_exclusive_group(required = True)
    ip_grp.add_argument('-i', '--id', help='Input ID')
    ip_grp.add_argument('-n', '--name', help='Input name')

    args = parser.parse_args()

    if args.id:
        main(args.id, 'id')
    else:
        main(args.name, 'name')