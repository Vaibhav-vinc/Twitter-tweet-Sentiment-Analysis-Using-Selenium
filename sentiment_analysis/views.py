from django.shortcuts import render, HttpResponse
from django.http import JsonResponse

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from textblob import TextBlob
import nltk

nltk.download(info_or_id="vader_lexicon")
from nltk.sentiment.vader import SentimentIntensityAnalyzer


def form(request) -> HttpResponse:
    return render(request=request, template_name="form.html")


def analyze(request) -> HttpResponse:
    return render(
        request=request,
        template_name="analyzed.html",
        context={"tw_url": request.POST.get("tweet-url")},
    )


def getTweet(request) -> JsonResponse:
    options = webdriver.ChromeOptions()
    options.add_argument(argument="--headless")
    options.add_argument("log-level=3")
    driver = webdriver.Chrome(options=options)
    tweet_url = request.GET.get("tw_url")
    print(f"{tweet_url = }")

    driver.get(url=tweet_url)

    time.sleep(3)

    # driver.execute_script(script=f"window.scrollTo(0, {700});")
    print("going in >>> ")
    selectorValue = '[data-testid="{}"]'
    try:
        tweet_text = driver.find_element(by=By.CSS_SELECTOR, value=selectorValue.format("tweetText")).text
        usernameSpans = driver.find_elements(
            by=By.CSS_SELECTOR, value=selectorValue.format("User-Name")
        )
        print(*[f"{span.text = }" for span in usernameSpans])
        usernameSpans = usernameSpans[0].text.splitlines()
        twitter_username, twitter_handle = usernameSpans[0], usernameSpans[-1]

        print(f"@{twitter_handle}: {tweet_text[:50]}")
    except Exception as e:
        print(e)
        return JsonResponse({"code": 404})
    # tweet_text: str = tweet.text

    driver.quit()
    processed_tweet_data: dict[str, float] = processTweet(tweet_text=tweet_text)
    processed_tweet_data.update(
        {
            "twitter_username": twitter_username,
            "twitter_handle": twitter_handle,
            "code": 200,
        }
    )
    return JsonResponse(data=processed_tweet_data, safe=True)


def processTweet(tweet_text) -> dict[str, float]:
    sid = SentimentIntensityAnalyzer()
    process_dict: dict[str, float] = sid.polarity_scores(tweet_text)

    compound: float = process_dict.pop("compound")
    if compound == 0:
        sentiment_type = "Neutral"
    elif compound > 0:
        sentiment_type = "Positive"
    elif compound < 0:
        sentiment_type = "Negative"

    new_dict: dict[str, float] = dict()
    new_dict["sentiment_type"] = sentiment_type
    new_dict["polarity"] = TextBlob(text=tweet_text).polarity
    new_dict["positive_pcnt"] = round(round(process_dict["pos"], 4), 2)
    new_dict["neutral_pcnt"] = round(process_dict["neu"] * 100, 2)
    new_dict["negative_pcnt"] = round(process_dict["neg"] * 100, 2)
    new_dict["tweet_text"] = tweet_text
    return new_dict
