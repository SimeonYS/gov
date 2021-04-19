import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import GovItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'
base = 'https://www.bnb.gov.br/sala-de-imprensa/noticias?p_p_id=101_INSTANCE_rpRfjO0wpalV&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&p_p_col_id=column-2&p_p_col_count=1&_101_INSTANCE_rpRfjO0wpalV_delta=10&_101_INSTANCE_rpRfjO0wpalV_keywords=&_101_INSTANCE_rpRfjO0wpalV_advancedSearch=false&_101_INSTANCE_rpRfjO0wpalV_andOperator=true&p_r_p_564233524_resetCur=false&_101_INSTANCE_rpRfjO0wpalV_cur={}'
class GovSpider(scrapy.Spider):
	name = 'gov'
	page = 1
	start_urls = [base.format(page)]

	def parse(self, response):
		articles = response.xpath('//div[@style="margin-bottom:30px;margin-top:-10px"]')
		links = []
		for article in articles:
			date = article.xpath('.//span[@class="datapublicacao"]/text()').get()
			post_links = article.xpath('.//a/@href').get()
			links.append(post_links)
			yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date))

		if len(links) == 10:
			self.page += 1
			yield response.follow(base.format(self.page), self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//h3/span/text()').get()
		content = response.xpath('//div[@class="asset-full-content show-asset-title"]//div[@class="journal-content-article"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=GovItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
