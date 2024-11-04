#!/usr/bin/env python
# coding: utf-8

import telebot
from telebot import types
from aliexpress_api import AliexpressApi, models
import re
import requests, json
from urllib.parse import urlparse, parse_qs
import urllib.parse
import os

# Initialize the bot with your token from the environment variable
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
if not bot_token:
    raise ValueError("Telegram bot token is not set in the environment variable 'TELEGRAM_BOT_TOKEN'")
bot = telebot.TeleBot(bot_token)

# Initialize the AliExpress API with your credentials from environment variables
app_key = os.getenv('ALIEXPRESS_APP_KEY')
app_secret = os.getenv('ALIEXPRESS_APP_SECRET')
if not app_key or not app_secret:
    raise ValueError("AliExpress API credentials are not set in environment variables 'ALIEXPRESS_APP_KEY' and 'ALIEXPRESS_APP_SECRET'")
aliexpress = AliexpressApi(app_key, app_secret, models.Language.EN, models.Currency.EUR, 'default')

# Constants for image links
IMAGE_LINK_1 = "https://i.postimg.cc/HkMxWS1T/photo-5893070682508606111-y.jpg"
IMAGE_LINK_2 = "https://i.postimg.cc/zvDbVTS0/photo-5893070682508606110-x.jpg"

# Define the keyboards
keyboardStart = types.InlineKeyboardMarkup(row_width=1)
btn1 = types.InlineKeyboardButton("⭐️ألعاب لجمع العملات المعدنية⭐️", callback_data="games")
btn2 = types.InlineKeyboardButton("⭐️تخفيض العملات على منتجات السلة 🛒⭐️", callback_data='click')
btn3 = types.InlineKeyboardButton("❤️ اشترك في القناة للمزيد من العروض ❤️", url="t.me/LaDeals")
keyboardStart.add(btn1, btn2, btn3)

keyboard = types.InlineKeyboardMarkup(row_width=1)
keyboard.add(btn1, btn2, btn3)

keyboard_games = types.InlineKeyboardMarkup(row_width=1)
keyboard_games.add(btn1, btn2, btn3)

# Welcome message handler
@bot.message_handler(commands=['start'])
def welcome_user(message):
    bot.send_message(
        message.chat.id,
        "مرحبا بك، ارسل لنا رابط المنتج الذي تريد شرائه لنوفر لك افضل سعر له 👌 \n",
        reply_markup=keyboardStart
    )

# Callback handler for 'click' button
@bot.callback_query_handler(func=lambda call: call.data == 'click')
def button_click(callback_query):
    bot.edit_message_text(chat_id=callback_query.message.chat.id,
                          message_id=callback_query.message.message_id,
                          text="...")

    bot.send_photo(callback_query.message.chat.id,
                   IMAGE_LINK_1,
                   caption="",
                   reply_markup=keyboard)

# Function to get affiliate links
def get_affiliate_links(message, message_id, link):
  try:

    affiliate_link = aliexpress.get_affiliate_links(
        f'https://star.aliexpress.com/share/share.htm?platform=AE&businessType=ProductDetail&redirectUrl={link}?sourceType=620&aff_fcid='
    )
    affiliate_link = affiliate_link[0].promotion_link

    super_links = aliexpress.get_affiliate_links(
        f'https://star.aliexpress.com/share/share.htm?platform=AE&businessType=ProductDetail&redirectUrl={link}?sourceType=562&aff_fcid='
    )
    super_links = super_links[0].promotion_link

    limit_links = aliexpress.get_affiliate_links(
        f'https://star.aliexpress.com/share/share.htm?platform=AE&businessType=ProductDetail&redirectUrl={link}?sourceType=561&aff_fcid='
    )
    limit_links = limit_links[0].promotion_link

    try:
      img_link = aliexpress.get_products_details([
          '1000006468625',
          f'https://star.aliexpress.com/share/share.htm?platform=AE&businessType=ProductDetail&redirectUrl={link}'
      ])
      price_pro = img_link[0].target_sale_price
      title_link = img_link[0].product_title
      img_link = img_link[0].product_main_image_url
      print(img_link)
      bot.delete_message(message.chat.id, message_id)
      bot.send_photo(message.chat.id,
                     img_link,
                     caption=" \n🛒 منتجك هو  : 🔥 \n"
                     f" {title_link} 🛍 \n"
                     f"  سعر المنتج  : "
                     f" {price_pro}  دولار 💵\n"
                     " \n قارن بين الاسعار واشتري 🔥 \n"
                     "💰 عرض العملات (السعر النهائي عند الدفع)  : \n"
                     f"الرابط {affiliate_link} \n"
                     f"💎 عرض السوبر  : \n"
                     f"الرابط {super_links} \n"
                     f"♨️ عرض محدود  : \n"
                     f"الرابط {limit_links} \n\n"
                     "#AliXPromotion ✅",
                     reply_markup=keyboard)

    except:

      bot.delete_message(message.chat.id, message_id)
      bot.send_message(message.chat.id, "قارن بين الاسعار واشتري 🔥 \n"
                       "💰 عرض العملات (السعر النهائي عند الدفع) : \n"
                       f"الرابط {affiliate_link} \n"
                       f"💎 عرض السوبر : \n"
                       f"الرابط {super_links} \n"
                       f"♨️ عرض محدود : \n"
                       f"الرابط {limit_links} \n\n"
                       "#AliXPromotion ✅",
                       reply_markup=keyboard)

  except:
    bot.send_message(message.chat.id, "حدث خطأ 🤷🏻‍♂️")


# In[6]:
def extract_link(text):
  # Regular expression pattern to match links
  link_pattern = r'https?://\S+|www\.\S+'

  # Find all occurrences of the pattern in the text
  links = re.findall(link_pattern, text)

  if links:
    return links[0]


def build_shopcart_link(link):
  params = get_url_params(link)
  shop_cart_link = "https://www.aliexpress.com/p/trade/confirm.html?"
  shop_cart_params = {
      "availableProductShopcartIds":
      ",".join(params["availableProductShopcartIds"]),
      "extraParams":
      json.dumps({"channelInfo": {
          "sourceType": "620"
      }}, separators=(',', ':'))
  }
  return create_query_string_url(link=shop_cart_link, params=shop_cart_params)


def get_url_params(link):
  parsed_url = urlparse(link)
  params = parse_qs(parsed_url.query)
  return params


def create_query_string_url(link, params):
  return link + urllib.parse.urlencode(params)


## Shop cart Affiliate تخفيض السلة
def get_affiliate_shopcart_link(link, message):
  try:
    shopcart_link = build_shopcart_link(link)
    affiliate_link = aliexpress.get_affiliate_links(
        shopcart_link)[0].promotion_link

    text2 = f"هذا رابط تخفيض السلة \n" \
           f"{str(affiliate_link)}" \

    img_link3 = "https://i.postimg.cc/HkMxWS1T/photo-5893070682508606111-y.jpg"
    bot.send_photo(message.chat.id, img_link3, caption=text2)

  except:
    bot.send_message(message.chat.id, "حدث خطأ 🤷🏻‍♂️")
