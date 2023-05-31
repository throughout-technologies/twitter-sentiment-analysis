from django.shortcuts import render,HttpResponse
import matplotlib.pyplot as plt
import matplotlib
from textblob import TextBlob
import tweepy,re
from django.views import View
import io, urllib.parse
import urllib, base64
import datetime, json
from django.contrib import messages
from members.models import Sentiment
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger

matplotlib.use('Agg')


def index(req):
   
    data_org=Sentiment.objects.all().order_by('-id')
    p=Paginator(data_org,7)
    page_no=req.GET.get('page')
    try:
        data=p.get_page(page_no)
    except PageNotAnInteger :
        data=p.get_page(1)
    except EmptyPage :
        data=p.get_page(p.num_pages)
        
    args = {'image':False,'data':data}
    return render(req, "index.html",args) 

def sentimentAnalysis(request):
   
    tweets=[]
    tweetText=[]
    analysis_Data={}
    
    if request.method=='POST':
        inputtext=request.POST['title']
        inputnumber=request.POST['record']
       

        analysis_Data['date']=datetime.datetime.now().strftime('%x')
        analysis_Data['search']=inputtext
        analysis_Data['no_tweets']=inputnumber

        return downloadData(request, inputnumber, inputtext, tweets, tweetText, analysis_Data)

    
    return HttpResponse(request, "get method not allowed...")

def downloadData(request, inputnumber, inputtext, tweets, tweetText, analysis_Data):
    
    consumerKey = 'MLSfR0Sul4dgUSAZmiPNzINct'
    consumerSecret = 'imz2sRsFzCcfNgKqjxUhwJAq3mKBrf233ESHzcLxzDq1nT4vtk'
    accessToken =  '1653011167365984256-GQA1vGpfBuyVi30onxahlHgGab5Adf'
    accessTokenSecret = 'aMcdMWuRGe11K1VGJAvCWb9KeZF08lRII6kpCyhZMD2vW'
    auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
    auth.set_access_token(accessToken, accessTokenSecret)
    api = tweepy.API(auth)

    # input for term to be searched and how many tweets to search
    searchTerm = str(inputtext)
    NoOfTerms = int(inputnumber)

    # searching for tweets
    tweets = tweepy.Cursor(api.search_tweets, q=searchTerm, lang = "en").items(NoOfTerms)
    

    # creating some variables to store info
    polarity = 0
    positive = 0
    wpositive = 0
    spositive = 0
    negative = 0
    wnegative = 0
    snegative = 0
    neutral = 0

    # iterating through tweets fetched
    for tweet in tweets:
            #Append to temp so that we can store in csv later. I use encode UTF-8
            tweetText.append(cleanTweet(tweet.text).encode('utf-8'))
            # print (tweet.text.translate(non_bmp_map))    #print tweet's text
            analysis = TextBlob(tweet.text)
        
            # print(analysis.sentiment)  # print tweet's polarity
            polarity += analysis.sentiment.polarity  # adding up polarities to find the average later      
          
            if (analysis.sentiment.polarity == 0):  # adding reaction of how people are reacting to find average later
                neutral += 1
            elif (analysis.sentiment.polarity > 0 and analysis.sentiment.polarity <= 0.3):
                wpositive += 1
            elif (analysis.sentiment.polarity > 0.3 and analysis.sentiment.polarity <= 0.6):
                positive += 1
            elif (analysis.sentiment.polarity > 0.6 and analysis.sentiment.polarity <= 1):
                spositive += 1
            elif (analysis.sentiment.polarity > -0.3 and analysis.sentiment.polarity <= 0):
                wnegative += 1
            elif (analysis.sentiment.polarity > -0.6 and analysis.sentiment.polarity <= -0.3):
                negative += 1
            elif (analysis.sentiment.polarity > -1 and analysis.sentiment.polarity <= -0.6):
                snegative += 1 
 
    sent_list=[positive, wpositive, spositive, negative, wnegative, snegative, neutral]
  
    result_bool = all(not i for i in sent_list)

    if result_bool:  
        messages.error(request, f"No sentiment available {searchTerm}!!!")
        return render(request, "index.html",{"image":False})

    # finding average of how people are reacting
    positive = percentage(positive, NoOfTerms)
    wpositive = percentage(wpositive, NoOfTerms)
    spositive = percentage(spositive, NoOfTerms)
    negative = percentage(negative, NoOfTerms)
    wnegative = percentage(wnegative, NoOfTerms)
    snegative = percentage(snegative, NoOfTerms)
    neutral = percentage(neutral, NoOfTerms)

   

    # finding average reaction

    polarity = polarity / NoOfTerms
   

    # printing out data
    print("How people are reacting on " + searchTerm + " by analyzing " + str(NoOfTerms) + " tweets.")
    print()
    print("General Report: ")

    if (polarity == 0):
        print("Neutral")
    elif (polarity > 0 and polarity <= 0.3):
        print("Weakly Positive")
    elif (polarity > 0.3 and polarity <= 0.6):
        print("Positive")
    elif (polarity > 0.6 and polarity <= 1):
        print("Strongly Positive")
    elif (polarity > -0.3 and polarity <= 0):
        print("Weakly Negative")
    elif (polarity > -0.6 and polarity <= -0.3):
        print("Negative")
    elif (polarity > -1 and polarity <= -0.6):
        print("Strongly Negative")

    print()
    print("Detailed Report: ")
    print(str(positive) + "% people thought it was positive")
    print(str(wpositive) + "% people thought it was weakly positive")
    print(str(spositive) + "% people thought it was strongly positive")
    print(str(negative) + "% people thought it was negative")
    print(str(wnegative) + "% people thought it was weakly negative")
    print(str(snegative) + "% people thought it was strongly negative")
    print(str(neutral) + "% people thought it was neutral")

    analysis_Data['sentiments'] = {'positive':positive, 'neutral':neutral, 'negative':negative}

    # data is collected store in database:

    def default(o):
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()
        
    # print("report ==> ",analysis_Data)
    json_analysis_data=json.loads(json.dumps(analysis_Data, default=default))
    
   
    sent_data=Sentiment(data = json_analysis_data)
    sent_data.save()

    return plotPieChart(request, positive, wpositive, spositive, negative, wnegative, snegative, neutral, searchTerm, NoOfTerms)


def cleanTweet(tweet):
    # Remove Links, Special Characters etc from tweet
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w +:\ / \ / \S +)", " ", tweet).split())

# function to calculate percentage
def percentage(part, whole):
    temp = 100 * float(part) / float(whole)
    return format(temp, '.2f')

def plotPieChart(request, positive, wpositive, spositive, negative, wnegative, snegative, neutral, searchTerm, noOfSearchTerms):
    labels = ['Positive [' + str(positive) + '%]', 'Weakly Positive [' + str(wpositive) + '%]','Strongly Positive [' + str(spositive) + '%]', 'Neutral [' + str(neutral) + '%]',
            'Negative [' + str(negative) + '%]', 'Weakly Negative [' + str(wnegative) + '%]', 'Strongly Negative [' + str(snegative) + '%]']
    sizes = [positive, wpositive, spositive, neutral, negative, wnegative, snegative]
    colors = ['yellowgreen','lightgreen','darkgreen', 'gold', 'red','lightsalmon','darkred']
    patches, texts = plt.pie(sizes, colors=colors, startangle=90)
    plt.legend(patches, labels, loc="best")
    plt.title('How people are reacting on ' + searchTerm + ' by analyzing ' + str(noOfSearchTerms) + ' Tweets.')
    plt.axis('equal') 

    # image store process :

    buf=io.BytesIO()
    plt.savefig(buf,format='png' ) 
    buf.seek(0)
    string=base64.b64encode(buf.read())
    uri='data:image/png;base64,' + urllib.parse.quote(string)
    
    # instance close :
    plt.close()

    #  fetch data from data base : postgres DB
    data_org=Sentiment.objects.all().order_by('-id')
    p=Paginator(data_org,7)
    page_no=request.GET.get('page')
    try:
        data=p.get_page(page_no)
    except PageNotAnInteger :
        data=p.get_page(1)
    except EmptyPage :
        data=p.get_page(p.num_pages)

    args = {'image':uri,'data':data}
    return render(request, "index.html",args)


