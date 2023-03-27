import asyncio
import hashlib
import os
import re
from datetime import datetime
from typing import List
from googletrans import Translator
from aiogram import Bot
import requests
from aiogram.types import ParseMode
from bs4 import BeautifulSoup
from aiogram.types import InputMediaPhoto, MediaGroup
from dotenv import load_dotenv

from config import get_bedrooms, Config
from models.ad import Advertisement

load_dotenv()
config = Config()


def get_listings():
    query_params = {
        "price_min": config.min_price,
        "price_max": config.max_price,
    }
    
    urls = [
        f'{config.bazaraki_url}/real-estate-to-rent/apartments-flats{config.furnishing}{get_bedrooms()}{config.city}',
        f'{config.bazaraki_url}/real-estate-to-rent/houses{config.furnishing}{get_bedrooms()}{config.city}'
    ]
    
    listings = []
    for url in urls:
        html = requests.get(url, params=query_params).text
        tree = BeautifulSoup(html, "html.parser")
        listings.extend(tree.find_all("div", class_="list-announcement-block"))

    return listings    


def parse() -> List[Advertisement]:
    listings = get_listings()

    result = []

    for listing in listings:
        announcement_block = listing.find("div", class_="announcement-block__date").text.strip().replace('\n', '')
        time, location = announcement_block.split(",")[:2]
        
        if "today" not in str(time).lower():
            continue
        time = format_time(time)
        
        # Clean up other fields
        title = listing.find("a", class_="announcement-block__title").text.strip().replace('\n', '')
        link = config.bazaraki_url + listing.find("a", class_="announcement-block__title").attrs['href']
        description = listing.find("div", class_="announcement-block__description").text.strip().replace('\n', '')[:400] + "..."
        price = listing.find("div", class_="announcement-block-link announcement-block__link").text
        price = re.sub(r"[^0-9€]+", "", price)
        type_property = listing.find("div", class_="announcement-block__breadcrumbs").text.split('»')[1].replace('\n', '').replace(' ', '')
        location = str(location).replace('district', '').replace(' ', '').capitalize()
        
        # Retrieve image URLs
        ad_tree = BeautifulSoup(requests.get(link).text, "html.parser")
        image_tags = ad_tree.find_all("img", class_="announcement__images-item js-image-show-full")
        image_urls = [img['src'] for img in image_tags[:config.count_photo]]
        
        # Create advertisement object and append to results
        ad = Advertisement(title=translate_text(title),
                           type=type_property,
                           description=translate_text(description),
                           link=link,
                           price=price,
                           location=translate_text(location),
                           time=time,
                           images=image_urls)
        result.append(ad)

    return result


def clear_previous_ads():
    with open("previous_ads.txt", "w") as f:
        f.write("")


def get_ad_hash(ad):
    hash_string = f"{ad['title']}_{ad['description']}_{ad['location']}"
    return hashlib.md5(hash_string.encode("utf-8")).hexdigest()


def format_time(time_str: str) -> str:
    time_str = time_str.lower().replace(' ', '')
    dt = datetime.strptime(time_str, 'today%H:%M')
    today = datetime.now().date()
    time_formatted = dt.strftime('%I:%M %p')
    date_formatted = today.strftime('%b %d')
    result = f'{date_formatted} {time_formatted}'
    return result


def translate_text(text):
    return Translator().translate(text, dest='ru').text


async def check_ads(bot: Bot):

    with open("previous_ads.txt", "r") as f:
        previous_ads = set()
        for line in f:
            previous_ads.add(line.strip())

    current_ads = parse()
    new_ads = [ad for ad in current_ads if get_ad_hash(ad.to_dict()) not in previous_ads]

    if new_ads:
        with open("previous_ads.txt", "a") as f:
            for ad in new_ads:
                media_list = []
                for i, image_url in enumerate(ad.images):
                    if i == 0:
                        media_list.append(InputMediaPhoto(media=image_url, caption=str(ad), parse_mode=ParseMode.HTML))
                    else:
                        media_list.append(InputMediaPhoto(media=image_url))

                media_group = MediaGroup(medias=media_list)
                await bot.send_media_group(chat_id=os.getenv('CHANNEL_ID'), media=media_group)
                f.write(get_ad_hash(ad.to_dict()) + "\n")
                await asyncio.sleep(2)



