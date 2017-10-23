import scrapy


class BookIt(scrapy.Spider):
    name = 'bookit'
    start_urls = ['https://hm.highfive.nl/login/osterley-health-and-fitness?lang=en']
    download_delay = 1.5

    def parse(self, response):
        print "Booking started"
        yield scrapy.FormRequest.from_response(
            response,
            formdata={'ctl00$cp1$password': self.settings.get('PASSWORD'), 'ctl00$cp1$userid': self.settings.get('USER_NAME')},
            callback=self.parse_results
        )

    def parse_results(self, response):
        print "Logged in as " + self.settings.get('USER_NAME')

        class_name = self.settings.get('CLASS_NAME')
        class_time = self.settings.get('CLASS_TIME')
        print "Looking for class: " + class_name + " at: " + class_time

        for row in response.css("tr.tablesubrow"):
            classname = row.xpath("@class").extract_first()

            if 'tablesubrow' == classname:
                cells = row.xpath(".//td")
                time = cells[0].xpath(".//text()").extract_first()[2:]
                type = cells[1].xpath(".//text()").extract_first()

                if time == class_time and type == class_name:
                    print "Class found. Trying to book you in"
                    bookable = cells[3].xpath("@class").extract_first() == "reserveerknop"
                    if bookable:
                        relpath = cells[3].xpath(".//a/@href").extract_first()[2:]
                        path = "https://hm.highfive.nl/hmuser" + relpath
                        yield response.follow(path, callback=self.parse_booked)
                    else:
                        print "Booking not available at this time"

    @staticmethod
    def parse_booked(response):
        print "Booking successful"
        print response
