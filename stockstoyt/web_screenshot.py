from selenium import webdriver



def screenshot_youtube_channels(channel_id, stock_to_company_names):
  driver = webdriver.Chrome()
  for symbol, id in channel_id.items():
    if id:
      driver.get(f'https://www.youtube.com/channel/{id}')
      print(f'Screenshots channel: {stock_to_company_names[symbol]}')
      driver.save_screenshot(f'channel_screenshot/{symbol}_{stock_to_company_names[symbol]}.png')
  
  driver.quit()