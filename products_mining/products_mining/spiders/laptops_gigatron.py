import scrapy
from scrapy.http import Request
from scrapy.contrib.loader import ItemLoader
import products_mining.items
from products_mining.items import Laptop

class GigatronLaptopSpider(scrapy.Spider):
    name = "gigatron_laptops"
    
    def start_requests(self):
        url = 'https://www.gigatron.rs/laptop_racunari'
        return [scrapy.Request(url, callback=self.get_number_of_items)]
        
    def get_number_of_items(self, response):
        number_of_items = response.css('b#total::text').extract_first()
        return [scrapy.Request('https://www.gigatron.rs/laptop_racunari?limit=1', callback=self.parse_links)]
    
    def parse_links(self,response):
        links = response.xpath("//*/h4/a[@class='product-name']/@href").extract()
        for link in links:
            return [scrapy.Request(link)]
        
    def parse(self,response):
        min_cena = 80000  # generated by dsl
        max_cena = 120000 # generated by dsl
        
        dijagonala = '14"' # generated by dsl
        
        max_masa = 3.5 # generated by dsl
        min_masa = 2 # generated by dsl
        
        memorija = '8GB' # generated by dsl
        
        laptop = Laptop()
        laptop['name'] = response.css('h1::text').extract_first()
        laptop['price'] = response.css('div.price-item.currency-item h5::text').extract_first().strip()
        
        if (laptop.price > max_cena) | (laptop.price < min_cena):
            return
        
        table = response.css('div.main.clearfix table.product-specs')
        for tr in table.css('tr'):
            name = tr.css('th::text').extract_first()
            if name == 'Grafička karta':
                value = tr.css('a::text').extract_first().strip()
            elif name == 'HDD1':
                value = str(tr.css('td::text').extract_first()).split(':')[1]
            elif name == 'Ekran':
                value = tr.css('td::text').extract()[1].split(':')[1].strip()
            elif name == 'Procesor':
                value = tr.css('a::text').extract_first()
            else:
                value = tr.css('td::text').extract_first().strip()
            
            property = self.gigatron_dictionary(name)
            if property == 'processor_model':
                laptop['processor_speed'] = tr.css('td::text').extract()[0].split(':')[1].strip()
                laptop['catche_memory'] = tr.css('td::text').extract()[1].split(':')[1].strip()
            elif property == 'screen_resolution':
                laptop['screen_type'] = tr.css('td::text').extract()[0].strip()
            elif property == 'screen_size':
                if value != dijagonala:
                    return
            elif property == 'weight':
                if (value > max_masa) | (value < min_masa):
                    return
            elif property == 'ram':
                if value != memorija:
                    return
            
            if property !='':
                laptop[property] = value
        
        print('laptop')
            
    def gigatron_dictionary(self, x):
        return {
        'RAM memorija': 'ram',
        'Dijagonala ekrana': 'screen_size',
        'Ekran': 'screen_resolution',
        'Ekran osetljiv na dodir' : 'touch_screen',
        'Procesor' : 'processor_model',
        'Čipset' : 'chipset',
        'Grafička karta': 'graphics_card',
        'HDD1' : 'hdd_size',
        'Tip HDD1' : 'hdd_type',
        'Optički uređaj' : 'optics',
        'Zvučnici' : 'speakers' ,
        'Web kamera' : 'web_camera',
        'HDMI' : 'hdmi_port',
        'VGA' : 'vga_port',
        'USB 2.0' : 'usb_2',
        'USB 3.0' : 'usb_3',
        'Mrežna kartica' : 'network_card',
        'Bluetooth' : 'bluetooth',
        'Čitač kartica' : 'card_reader',
        'Baterija' : 'batery',
        'Operativni sistem' : 'operating_system',
        'Boja': 'color',
        'Dimenzije (Š x D x V)' : 'dimensions',
        'Težina (kg)' : 'weight',
        'Memorija' : 'ram_type'
        }.get(x, '')   
        
        
        