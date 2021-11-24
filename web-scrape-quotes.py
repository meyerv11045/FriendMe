import bs4
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
from unidecode import unidecode

#GoodReads motivational quotes
#"https://www.goodreads.com/quotes/tag/motivational?page=" + str(page_num)
#page 12

#motivation
#inspiration

#believe
#page 3

#happy
page_num = 3
with open('QuotesToAdd.txt', 'a') as f:
    while page_num < 101:
        url = "https://www.goodreads.com/quotes/tag/believe?page=" + str(page_num)
        Client = urlopen(url)
        xml_page = Client.read()
        Client.close()

        soup_page = soup(xml_page,"xml")
        quotes_list = soup_page.findAll('div', attrs={"class":"quoteText"})

        for quote in quotes_list:
            quote_string = unidecode(str(quote).split('<div class="quoteText">')[1].split('<span class="authorOrTitle">')[0].replace('<br>',' ').replace('<br/><br/><br/>', ' ').replace('<br/><br/>', ' ').replace('<br/>', ' ').strip().split('\n')[0])
            print(quote_string)
            use = input()
            if len(use) != 0:
                f.write('\n')
                f.write(quote_string)
                f.flush()

        page_num += 1
        
        print('Page:', page_num)
        