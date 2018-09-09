
import requests, pandas, numpy, matplotlib.pyplot as plt, re, boto3
from bs4 import BeautifulSoup

#uri = "https://www.yelp.com/biz/renewal-charlottesville-2"
def YelpScraper(uri):
    soupBowl = []
    uriList = []
    rawList = []
    starList = []
    reviewList = []
    dateList = []
    reviewSentiment = []

    hasNextPage = True
    while(hasNextPage):
        page = requests.get(uri)
        soup = BeautifulSoup(page.content, 'html.parser')
        soupBowl.append(soup)
        nextPage = soup.find_all(class_="u-decoration-none next pagination-links_anchor")
        uriList.append(nextPage)
        hasNextPage = len(nextPage) > 0
        if(hasNextPage):
            uri = nextPage[0].get_attribute_list('href')[0]
            uriList.append(uri)

    for soup in soupBowl:
        gridCells = soup.find_all(class_="review-content")
        for c in gridCells:
            stars = c.find_all(class_="i-stars")[0]
            starInt = float(stars.get_attribute_list('title')[0].split()[0])
            starList.append(starInt)
            date = c.find_all(class_="rating-qualifier")[0].get_text().strip()
            date = re.sub(r'[\t\r\n\s]', '', date)
            date = re.sub('Updatedreview', '', date)
            dateList.append(date)
            rawList.append(c)
            c = re.sub(r'[\t\r\n]', '', c.get_text().strip())
            reviewList.append(c)

    reviewDF = pandas.DataFrame({
        "Date":pandas.to_datetime(dateList),
        "Stars":starList
    })

    reviewDF = reviewDF.sort_values('Date')
    reviewDF = reviewDF.set_index('Date')

    #fig, ax = plt.subplots()
    #fig.subplots_adjust(bottom=0.3)
    #fig.set_dpi(1000)
    #plt.xticks(rotation=90)
    #plt.plot(reviewDF)

    comprehend = boto3.client(
        service_name='comprehend',
        aws_access_key_id='AKIAIBIMJEFTF6E5F3YQ',
        aws_secret_access_key='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',
        region_name='us-east-1'
    )
    for r in reviewList:
        reviewSentiment.append(comprehend.detect_sentiment(Text=r, LanguageCode='en'))


    sentimentDF = pandas.DataFrame({
        "Date":pandas.to_datetime(dateList),
        "Stars":starList,
        "Sentiment": reviewSentiment,
        "Review":reviewList
    })

    sentimentDF = sentimentDF.sort_values('Date')
    sentimentDF = sentimentDF.set_index('Date')
    return sentimentDF.to_json(orient='records')
    #writer = pandas.ExcelWriter('output.xlsx')
    #sentimentDF.to_excel(writer,'Sheet1')
    #writer.save()